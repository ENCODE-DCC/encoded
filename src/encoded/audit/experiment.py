from contentbase.auditor import (
    AuditFailure,
    audit_checker,
)
from .conditions import rfa

targetBasedAssayList = [
    'ChIP-seq',
    'RNA Bind-n-Seq',
    'ChIA-PET',
    'RIP Array',
    'RIP-seq',
    'MeDIP-seq',
    'iCLIP',
    'shRNA knockdown followed by RNA-seq',
    ]

controlRequiredAssayList = [
    'ChIP-seq',
    'RNA Bind-n-Seq',
    'RIP-seq',
    'RAMPAGE',
    'CAGE',
    'shRNA knockdown followed by RNA-seq'
    ]

seq_assays = [
    'RNA-seq',
    'ChIP-seq',
    'RNA Bind-n-Seq',
    'MeDIP-seq',
    'RNA-PET',
    'DNA-PET',
    'ChIA-PET',
    'CAGE',
    'RAMPAGE',
    'RIP-seq',
    ]

non_seq_assays = [
    'RNA profiling by array assay',
    'DNA methylation profiling by array assay',
    'Genotype',
    'comparative genomic hybridization by array',
    'RIP-chip',
    'protein sequencing by tandem mass spectrometry assay',
    'microRNA profiling by array assay',
    'Switchgear',
    '5C',
    ]


@audit_checker('experiment', frame='object')
def audit_experiment_release_date(value, system):
    '''
    Released experiments need release date.
    This should eventually go to schema
    '''
    if value['status'] == 'released' and 'date_released' not in value:
        detail = 'Experiment {} is released and requires a value in date_released'.format(value['@id'])
        raise AuditFailure('missing date_released', detail, level='DCC_ACTION')


@audit_checker('experiment', frame=['replicates'])
def audit_experiment_replicated(value, system):
    '''
    Experiments in ready for review or release ready state should be replicated. If not,
    wranglers should check with lab as to why before release.
    '''
    if value['status'] not in ['released', 'release ready', 'ready for review']:
        return

    num_bio_reps = set()
    for rep in value['replicates']:
        num_bio_reps.add(rep['biological_replicate_number'])

    if len(num_bio_reps) <= 1:
        if value['status'] in ['released']:
            detail = 'Experiment {} has only one biological replicate and is released. Check for proper annotation of this state in the metadata'.format(value['@id'])
            raise AuditFailure('unreplicated experiment', detail, level='DCC_ACTION')
        if value['status'] in ['ready for review', 'release ready']:
            detail = 'Experiment {} has only one biological replicate, more than one is typically expected before release'.format(value['@id'])
            raise AuditFailure('unreplicated experiment', detail, level='WARNING')


@audit_checker('experiment', frame='object')
def audit_experiment_description(value, system):
    '''
    Experiments should have descriptions that contain the experimental variables and
    read like phrases.  I cannot get all of that here, but I thought I would start
    with looking for funny characters.
    '''
    if value['status'] == 'deleted':
        return

    if 'description' not in value:
        return

    notallowed = ['=', ':', '!', ';']
    if any(c in notallowed for c in value['description']):
        detail = 'Experiment {} has odd character(s) in the description'.format(value['@id'])
        raise AuditFailure('malformed description', detail, level='WARNING')


@audit_checker('experiment', frame=['replicates', 'replicates.library'])
def audit_experiment_documents(value, system):
    '''
    Experiments should have documents.  Protocol documents or some sort of document.
    '''
    if value['status'] in ['deleted', 'replaced', 'proposed', 'preliminary']:
        return

    # If the experiment has documents, we are good
    if len(value.get('documents')) > 0:
        return

    # If there are no replicates to check yet, why bother
    if 'replicates' not in value:
        return

    lib_docs = 0
    for rep in value['replicates']:
        if 'library' in rep:
            lib_docs += len(rep['library']['documents'])

    # If there are no library documents anywhere, then we say something
    if lib_docs == 0:
        detail = 'Experiment {} has no attached documents'.format(value['@id'])
        raise AuditFailure('missing documents', detail, level='WARNING')


@audit_checker('experiment', frame='object')
def audit_experiment_assay(value, system):
    '''
    Experiments should have assays with valid ontologies term ids and names that
    are a valid synonym.
    '''
    if value['status'] == 'deleted':
        return

    if 'assay_term_id' not in value:
        detail = 'Experiment {} is missing assay_term_id'.format(value['@id'])
        yield AuditFailure('missing assay information', detail, level='ERROR')
        return
        # This should be a dependancy

    if 'assay_term_name' not in value:
        detail = 'Experiment {} is missing assay_term_name'.format(value['@id'])
        yield AuditFailure('missing assay information', detail, level='ERROR')
        return
        # This should be a dependancy

    ontology = system['registry']['ontology']
    term_id = value.get('assay_term_id')
    term_name = value.get('assay_term_name')

    if term_id.startswith('NTR:'):
        detail = 'Assay_term_id is a New Term Request ({} - {})'.format(term_id, term_name)
        yield AuditFailure('NTR assay', detail, level='DCC_ACTION')
        return

    if term_id not in ontology:
        detail = 'Assay_term_id {} is not found in cached version of ontology'.format(term_id)
        yield AuditFailure('assay_term_id not in ontology', term_id, level='DCC_ACTION')
        return

    ontology_term_name = ontology[term_id]['name']
    modifed_term_name = term_name + ' assay'
    if (ontology_term_name != term_name and term_name not in ontology[term_id]['synonyms']) and \
        (ontology_term_name != modifed_term_name and
            modifed_term_name not in ontology[term_id]['synonyms']):
        detail = 'Experiment has a mismatch between assay_term_name "{}" and assay_term_id "{}"'.format(
            term_name,
            term_id,
            )
        yield AuditFailure('mismatched assay_term_name', detail, level='DCC_ACTION')
        return


@audit_checker('experiment', frame=['replicates.antibody', 'target', 'replicates.antibody.targets'])
def audit_experiment_target(value, system):
    '''
    Certain assay types (ChIP-seq, ...) require valid targets and the replicate's
    antibodies should match.
    '''

    if value['status'] in ['deleted', 'proposed']:
        return

    if value.get('assay_term_name') not in targetBasedAssayList:
        return

    if 'target' not in value:
        detail = '{} experiments require a target'.format(value['assay_term_name'])
        yield AuditFailure('missing target', detail, level='ERROR')
        return

    target = value['target']
    if 'control' in target['investigated_as']:
        return

    # Some assays don't need antibodies
    if value['assay_term_name'] in ['RNA Bind-n-Seq', 'shRNA knockdown followed by RNA-seq']:
        return

    # Check that target of experiment matches target of antibody
    for rep in value['replicates']:
        if 'antibody' not in rep:
            detail = 'Replicate {} in a {} assay requires an antibody'.format(
                rep['@id'],
                value['assay_term_name']
                )
            yield AuditFailure('missing antibody', detail, level='ERROR')
        else:
            antibody = rep['antibody']
            if 'recombinant protein' in target['investigated_as']:
                prefix = target['label'].split('-')[0]
                unique_antibody_target = set()
                unique_investigated_as = set()
                for antibody_target in antibody['targets']:
                    label = antibody_target['label']
                    unique_antibody_target.add(label)
                    for investigated_as in antibody_target['investigated_as']:
                        unique_investigated_as.add(investigated_as)
                if 'tag' not in unique_investigated_as:
                    detail = '{} is not to tagged protein'.format(antibody['@id'])
                    yield AuditFailure('not tagged antibody', detail, level='ERROR')
                else:
                    if prefix not in unique_antibody_target:
                        detail = '{} is not found in target for {}'.format(
                            prefix,
                            antibody['@id']
                            )
                        yield AuditFailure('mismatched tag target', detail, level='ERROR')
            else:
                target_matches = False
                for antibody_target in antibody['targets']:
                    if target['name'] == antibody_target.get('name'):
                        target_matches = True
                if not target_matches:
                    detail = '{} is not found in target list for antibody {}'.format(
                        target['name'],
                        antibody['@id']
                        )
                    yield AuditFailure('mismatched target', detail, level='ERROR')


@audit_checker('experiment', frame=['target', 'possible_controls'])
def audit_experiment_control(value, system):
    '''
    Certain assay types (ChIP-seq, ...) require possible controls with a matching biosample.
    Of course, controls do not require controls.
    '''

    if value['status'] in ['deleted', 'proposed']:
        return

    # Currently controls are only be required for ChIP-seq
    if value.get('assay_term_name') not in controlRequiredAssayList:
        return

    # We do not want controls
    if 'target' in value and 'control' in value['target']['investigated_as']:
        return

    if value['possible_controls'] == []:
        detail = '{} experiments require a value in possible_control'.format(
            value['assay_term_name']
            )
        raise AuditFailure('missing possible_controls', detail, level='NOT_COMPLIANT')

    for control in value['possible_controls']:
        if control.get('biosample_term_id') != value.get('biosample_term_id'):
            detail = 'Control {} is for {} but experiment is done on {}'.format(
                control['@id'],
                control.get('biosample_term_name'),
                value['biosample_term_name'])
            raise AuditFailure('mismatched control', detail, level='ERROR')


@audit_checker('experiment', frame=['target', 'possible_controls', 'replicates', 'replicates.antibody', 'possible_controls.replicates', 'possible_controls.replicates.antibody', 'possible_controls.target'], condition=rfa('ENCODE3'))
def audit_experiment_ChIP_control(value, system):

    if value['status'] in ['deleted', 'proposed', 'preliminary', 'replaced', 'revoked']:
        return

    # Currently controls are only be required for ChIP-seq
    if value.get('assay_term_name') != 'ChIP-seq':
        return

    # We do not want controls
    if 'target' in value and 'control' in value['target']['investigated_as']:
        return

    if not value['possible_controls']:
        return

    num_IgG_controls = 0
    for control in value['possible_controls']:
        if ('target' not in control) or ('control' not in control['target']['investigated_as']):
            detail = 'Experiment {} is ChIP-seq but its control {} is not linked to a target with investigated.as = control'.format(
                value['@id'],
                control['@id'])
            raise AuditFailure('invalid possible_control', detail, level='ERROR')

        if not control['replicates']:
            continue

        if 'antibody' in control['replicates'][0]:
            num_IgG_controls += 1

    # If all of the possible_control experiments are mock IP control experiments
    if num_IgG_controls == len(value['possible_controls']):
        if value.get('assay_term_name') == 'ChIP-seq':
            # The binding group agreed that ChIP-seqs all should have an input control.
            detail = 'Experiment {} is ChIP-seq and requires at least one input control, as agreed upon by the binding group. {} is not an input control'.format(
                value['@id'],
                control['@id'])
            raise AuditFailure('missing input control', detail, level='NOT_COMPLIANT')


@audit_checker('experiment', frame=['replicates', 'replicates.library'])
def audit_experiment_spikeins(value, system):
    '''
    All ENCODE 3 long (>200) RNA-seq experiments should specify their spikeins.
    The spikeins specified should have datasets of type spikeins.
    The spikeins datasets should have a fasta file, a document, and maybe a tsv
    '''

    if value['status'] in ['deleted', 'replaced']:
        return

    if value.get('assay_term_name') != 'RNA-seq':
        return

    for rep in value['replicates']:

        lib = rep.get('library')
        if lib is None:
            continue

        size_range = lib.get('size_range')
        if size_range != '>200':
            continue

        spikes = lib.get('spikeins_used')
        if (spikes is None) or (spikes == []):
            detail = 'Library {} is in an RNA-seq experiment and has size_range >200. It requires a value for spikeins_used'.format(lib['@id'])
            yield AuditFailure('missing spikeins_used', detail, level='NOT_COMPLIANT')
            # Informattional if ENCODE2 and release error if ENCODE3


@audit_checker('experiment', frame='object')
def audit_experiment_biosample_term(value, system):
    '''
    The biosample term and id and type information should be present and
    concordent with library biosamples,
    Exception: RNA Bind-n-Seq
    '''
    if value['status'] in ['deleted', 'replaced']:
        return

    if value.get('assay_term_name') == 'RNA Bind-n-Seq':
        return

    ontology = system['registry']['ontology']
    term_id = value.get('biosample_term_id')
    term_type = value.get('biosample_type')
    term_name = value.get('biosample_term_name')

    if 'biosample_type' not in value:
        detail = '{} is missing biosample_type'.format(value['@id'])
        yield AuditFailure('missing biosample_type', detail, level='ERROR')

    if 'biosample_term_name' not in value:
        detail = '{} is missing biosample_term_name'.format(value['@id'])
        yield AuditFailure('missing biosample_term_name', detail, level='ERROR')
    # The type and term name should be put into dependancies

    if term_id is None:
        detail = '{} is missing biosample_term_id'.format(value['@id'])
        yield AuditFailure('missing biosample_term_id', detail, level='ERROR')
    elif term_id.startswith('NTR:'):
        detail = '{} has an NTR biosample {} - {}'.format(value['@id'], term_id, term_name)
        yield AuditFailure('NTR biosample', detail, level='DCC_ACTION')
    elif term_id not in ontology:
        detail = '{} has term_id {} which is not in ontology'.format(value['@id'], term_id)
        yield AuditFailure('term_id not in ontology', term_id, level='DCC_ACTION')
    else:
        ontology_name = ontology[term_id]['name']
        if ontology_name != term_name and term_name not in ontology[term_id]['synonyms']:
            detail = '{} has a biosample mismatch {} - {} but ontology says {}'.format(
                value['@id'],
                term_id,
                term_name,
                ontology_name
                )
            yield AuditFailure('mismatched biosample_term_name', detail, level='ERROR')

    for rep in value['replicates']:
        if 'library' not in rep:
            continue

        lib = rep['library']
        if 'biosample' not in lib:
            detail = '{} is missing biosample, expecting one of type {}'.format(
                lib['@id'],
                term_name
                )
            yield AuditFailure('missing biosample', detail, level='NOT_COMPLIANT')
            continue

        biosample = lib['biosample']
        bs_type = biosample.get('biosample_type')
        bs_name = biosample.get('biosample_term_name')

        if bs_type != term_type:
            detail = '{} has mismatched biosample_type, {} - {}'.format(
                lib['@id'],
                term_type,
                bs_type
                )
            yield AuditFailure('mismatched biosample_type', detail, level='ERROR')

        if bs_name != term_name:
            detail = '{} has mismatched biosample_term_name, {} - {}'.format(
                lib['@id'],
                term_name,
                bs_name
                )
            yield AuditFailure('mismatched biosample_term_name', detail, level='ERROR')


@audit_checker(
    'experiment',
    frame=[
        'target',
        'replicates',
        'replicates.antibody',
        'replicates.antibody.lot_reviews.organisms',
        'replicates.library',
        'replicates.library.biosample',
        'replicates.library.biosample.organism',
    ],
    condition=rfa('ENCODE3', 'modERN'))
def audit_experiment_antibody_eligible(value, system):
    '''Check that biosample in the experiment is eligible for new data for the given antibody.'''

    if value['status'] in ['deleted', 'proposed']:
        return

    if value.get('assay_term_name') not in targetBasedAssayList:
        return

    if 'target' not in value:
        return

    target = value['target']
    if 'control' in target['investigated_as']:
        return

    if value['assay_term_name'] in ['RNA Bind-n-Seq', 'shRNA knockdown followed by RNA-seq']:
        return

    for rep in value['replicates']:
        if 'antibody' not in rep:
            continue
        if 'library' not in rep:
            continue

        antibody = rep['antibody']
        lib = rep['library']

        if 'biosample' not in lib:
            continue

        biosample = lib['biosample']
        organism = biosample['organism']['name']

        if 'histone modification' in target['investigated_as']:
            for lot_review in antibody['lot_reviews']:
                if (lot_review['status'] == 'eligible for new data') and (lot_review['biosample_term_id'] == 'NTR:00000000'):
                    organism_match = False
                    for lot_organism in lot_review['organisms']:
                        if organism == lot_organism['name']:
                            organism_match = True
                    if not organism_match:
                        detail = '{} is not eligible for {}'.format(antibody["@id"], organism)
                        yield AuditFailure('not eligible antibody', detail, level='NOT_COMPLIANT')
                else:
                    detail = '{} is not eligible for {}'.format(antibody["@id"], organism)
                    yield AuditFailure('not eligible antibody', detail, level='NOT_COMPLIANT')
        else:
            biosample_term_id = value['biosample_term_id']
            biosample_term_name = value['biosample_term_name']
            experiment_biosample = (biosample_term_id, organism)
            eligible_biosamples = set()
            for lot_review in antibody['lot_reviews']:
                if lot_review['status'] == 'eligible for new data':
                    for lot_organism in lot_review['organisms']:
                        eligible_biosample = (lot_review['biosample_term_id'], lot_organism['name'])
                        eligible_biosamples.add(eligible_biosample)
            if experiment_biosample not in eligible_biosamples:
                detail = '{} is not eligible for {} in {}'.format(antibody["@id"], biosample_term_name, organism)
                yield AuditFailure('not eligible antibody', detail, level='NOT_COMPLIANT')
