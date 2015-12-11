from contentbase import (
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
    'eCLIP',
    'shRNA knockdown followed by RNA-seq',
    ]

controlRequiredAssayList = [
    'ChIP-seq',
    'RNA Bind-n-Seq',
    'RIP-seq',
    'RAMPAGE',
    'CAGE',
    'single cell isolation followed by RNA-seq',
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


@audit_checker('experiment',
               frame=['replicates', 'award'],
               condition=rfa("ENCODE3", "modERN",
                             "ENCODE", "modENCODE", "MODENCODE", "ENCODE2-Mouse"))
def audit_experiment_replicated(value, system):
    '''
    Experiments in ready for review or release ready state should be replicated. If not,
    wranglers should check with lab as to why before release.
    '''
    if value['status'] not in ['released', 'release ready', 'ready for review']:
        return
    '''
    Excluding single cell isolation experiments from the replication requirement
    '''
    if value['assay_term_name'] == 'single cell isolation followed by RNA-seq':
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

@audit_checker('experiment', frame=['replicates', 'replicates.library'])
def audit_experiment_replicates_with_no_libraries(value, system):
    if value['status'] in ['deleted','replaced','revoked']:
        return
    if len(value['replicates'])==0:
        return 
    for rep in value['replicates']:
        if 'library' not in rep:
            detail = 'Experiment {} has a replicate {}, that has no library associated with'.format(
                value['@id'],
                rep['@id'])
            yield AuditFailure('replicate with no library', detail, level='NOT_COMPLIANT')
    return


@audit_checker('experiment', frame=['replicates', 'replicates.library.biosample'])
def audit_experiment_isogeneity(value, system):

    if value['status'] in ['deleted', 'replaced']:
        return

    if len(value['replicates']) < 2:
        return

    if value.get('replication_type') is None:
        detail = 'In experiment {} the replication_type cannot be determined'.format(value['@id'])
        yield AuditFailure('undetermined replication_type', detail, level='DCC_ACTION')

    biosample_dict = {}
    biosample_age_list = []
    biosample_sex_list = []
    biosample_donor_list = []

    for rep in value['replicates']:
        if 'library' in rep:
            if 'biosample' in rep['library']:
                biosampleObject = rep['library']['biosample']
                biosample_dict[biosampleObject['accession']] = biosampleObject
                biosample_age_list.append(biosampleObject.get('age'))
                biosample_sex_list.append(biosampleObject.get('sex'))
                biosample_donor_list.append(biosampleObject.get('donor'))
                biosample_species = biosampleObject.get('organism')
            else:
                # If I have a library without a biosample,
                # I cannot make a call about replicate structure
                return
        else:
            # REPLICATES WITH NO LIBRARIES WILL BE CAUGHT BY AUDIT (TICKET 3268)
            # If I have a replicate without a library,
            # I cannot make a call about the replicate structure
            return

    if len(biosample_dict.keys()) < 2:
            return  # unreplicated

    if biosample_species == '/organisms/human/':
        return  # humans are handled in the the replication_type

    if len(set(biosample_donor_list)) > 1:
        detail = 'In experiment {} the biosamples have varying strains {}'.format(
            value['@id'],
            biosample_donor_list)
        yield AuditFailure('mismatched donor', detail, level='ERROR')

    if len(set(biosample_age_list)) > 1:
        detail = 'In experiment {} the biosamples have varying ages {}'.format(
            value['@id'],
            biosample_age_list)
        yield AuditFailure('mismatched age', detail, level='ERROR')

    if len(set(biosample_sex_list)) > 1:
        detail = 'In experiment {} the biosamples have varying sexes {}'.format(
            value['@id'],
            repr(biosample_sex_list))
        yield AuditFailure('mismatched sex', detail, level='ERROR')
    return


@audit_checker('experiment', frame=['replicates', 'replicates.library'])
def audit_experiment_technical_replicates_same_library(value, system):
    if value['status'] in ['deleted', 'replaced', 'revoked']:
        return
    biological_replicates_dict = {}
    for rep in value['replicates']:
        bio_rep_num = rep['biological_replicate_number']
        tech_rep_num = rep['technical_replicate_number']
        if 'library' in rep:         
            library = rep['library']            
            if not bio_rep_num in biological_replicates_dict:
                biological_replicates_dict[bio_rep_num]=[]            
            if library['accession'] in biological_replicates_dict[bio_rep_num]:               
                detail = 'Experiment {} has different technical replicates associated with the same library'.format(value['@id'])
                raise AuditFailure('technical replicates with identical library', detail, level='DCC_ACTION')
            else:
                biological_replicates_dict[bio_rep_num].append(library['accession'])


@audit_checker('experiment', frame=['replicates', 
                                    'replicates.library', 'replicates.library.biosample'])
def audit_experiment_replicates_biosample(value, system):
    if value['status'] in ['deleted', 'replaced', 'revoked']:
        return
    biological_replicates_dict = {}
    biosamples_list = []
    assay_name = 'unknown'
    if 'assay_term_name' in value:
        assay_name = value['assay_term_name']

    for rep in value['replicates']:
        bio_rep_num = rep['biological_replicate_number']
        tech_rep_num = rep['technical_replicate_number']
        if 'library' in rep and 'biosample' in rep['library']:
            biosample = rep['library']['biosample']

            if bio_rep_num not in biological_replicates_dict:
                biological_replicates_dict[bio_rep_num] = biosample['accession']
                if biosample['accession'] in biosamples_list:
                    detail = 'Experiment {} has multiple biological replicates \
                              associated with the same biosample {}'.format(
                        value['@id'],
                        biosample['@id'])
                    raise AuditFailure('biological replicates with identical biosample',
                                       detail, level='DCC_ACTION')
                else:
                    biosamples_list.append(biosample['accession'])

            else:
                if biosample['accession'] != biological_replicates_dict[bio_rep_num] and \
                   assay_name != 'single cell isolation followed by RNA-seq':
                    detail = 'Experiment {} has technical replicates \
                              associated with the different biosamples'.format(
                        value['@id'])
                    raise AuditFailure('technical replicates with not identical biosample',
                                       detail, level='ERROR')


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
        raise AuditFailure('missing documents', detail, level='NOT_COMPLIANT')


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


@audit_checker('experiment', frame=['replicates',
                                    'replicates.library',
                                    'replicates.library.biosample'])
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
        'replicates.antibody.lot_reviews'
        'replicates.antibody.lot_reviews.organisms',
        'replicates.library',
        'replicates.library.biosample',
        'replicates.library.biosample.organism',
    ],
    condition=rfa('ENCODE3', 'modERN'))
def audit_experiment_antibody_eligible(value, system):
    '''Check that biosample in the experiment is eligible for new data for the given antibody.'''

    if value['status'] in ['deleted', 'proposed', 'preliminary']:
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
        organism = biosample['organism']['@id']

        # We only want the audit raised if the organism in lot reviews matches that of the biosample
        # and if is not eligible for new data. Otherwise, it doesn't apply and we shouldn't raise a stink

        if 'histone modification' in target['investigated_as']:
            for lot_review in antibody['lot_reviews']:
                if (lot_review['status'] == 'awaiting lab characterization'):
                    for lot_organism in lot_review['organisms']:
                        if organism == lot_organism:
                            detail = '{} is not eligible for {}'.format(antibody["@id"], organism)
                            yield AuditFailure('not eligible antibody',
                                               detail, level='NOT_COMPLIANT')

        else:
            biosample_term_id = value['biosample_term_id']
            biosample_term_name = value['biosample_term_name']
            experiment_biosample = (biosample_term_id, organism)
            eligible_biosamples = set()
            warning_flag = False
            for lot_review in antibody['lot_reviews']:
                if lot_review['status'] in ['eligible for new data',
                                            'eligible for new data (via exemption)']:
                    for lot_organism in lot_review['organisms']:
                        eligible_biosample = (lot_review['biosample_term_id'], lot_organism)
                        eligible_biosamples.add(eligible_biosample)
                if lot_review['status'] == 'eligible for new data (via exemption)':
                    warning_flag = True
            if warning_flag is True:
                detail = '{} is eligible via exempt for {} in {}'.format(antibody["@id"],
                                                                         biosample_term_name,
                                                                         organism)
                yield AuditFailure('antibody eligible via exemption', detail, level='WARNING')

            if experiment_biosample not in eligible_biosamples:
                detail = '{} is not eligible for {} in {}'.format(antibody["@id"],
                                                                  biosample_term_name, organism)
                yield AuditFailure('not eligible antibody', detail, level='NOT_COMPLIANT')


@audit_checker(
    'experiment',
    frame=[
        'replicates',
        'replicates.library'])
def audit_experiment_library_biosample(value, system):
    if value['status'] in ['deleted', 'replaced']:
        return

    if value.get('assay_term_name') == 'RNA Bind-n-Seq':
        return
    for rep in value['replicates']:
        if 'library' not in rep:
            continue

        lib = rep['library']
        if 'biosample' not in lib:
            detail = '{} is missing biosample'.format(
                lib['@id'])
            yield AuditFailure('missing biosample', detail, level='ERROR')


@audit_checker(
    'experiment',
    frame=[
        'replicates',
        'replicates.library'])
def audit_library_RNA_size_range(value, system):
    '''
    An RNA library should have a size_range specified.
    This needs to accomodate the rfa
    '''
    if value['status'] in ['deleted', 'replaced']:
        return

    if value.get('assay_term_name') == 'transcription profiling by array assay':
        return

    if value['status'] in ['deleted']:
        return

    RNAs = ['SO:0000356', 'SO:0000871']

    for rep in value['replicates']:
        if 'library' not in rep:
            continue
        lib = rep['library']
        if (lib['nucleic_acid_term_id'] in RNAs) and ('size_range' not in lib):
            detail = 'RNA library {} requires a value for size_range'.format(rep['library']['@id'])
            raise AuditFailure('missing size_range', detail, level='ERROR')


@audit_checker('experiment', frame=['object'])
def audit_temp_unique_array_items(value, system):
    '''
    Array values should not be duplicated
    '''

    if 'dbxrefs' in value:
        if len(value['dbxrefs']) != len(set(value['dbxrefs'])):
            detail = 'Duplicated dbxrefs in {}'.format(value['@id'])
            yield AuditFailure('duplicated expt dbxrefs', detail, level='DCC_ACTION')

    if 'possible_controls' in value:
        if len(value['possible_controls']) != len(set(value['possible_controls'])):
            detail = 'Duplicated possible_controls in {}'.format(value['@id'])
            yield AuditFailure('duplicated controls', detail, level='DCC_ACTION')

    if 'documents' in value:
        if len(value['documents']) != len(set(value['documents'])):
            detail = 'Duplicated documents in {}'.format(value['@id'])
            yield AuditFailure('duplicated expt docs', detail, level='DCC_ACTION')
            return
