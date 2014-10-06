
import string
from pyramid.traversal import find_resource
from ..auditor import (
    AuditFailure,
    audit_checker,
)

targetBasedAssayList = ['ChIP-seq',
                        'RNA Bind-n-Seq',
                        'ChIA-PET',
                        'RIP Array',
                        'RIP-seq',
                        'MeDIP-seq',
                        'iCLIP',
                        'shRNA knockdown followed by RNA-seq',
                        ]

controlRequiredAssayList = ['ChIP-seq',
                            'RNA Bind-n-Seq',
                            'RIP-seq',
                            ]


@audit_checker('experiment')
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

    notallowed = ['=', '_', ':', ';']
    if any(c in notallowed for c in value['description']):
        detail = 'Bad characters'  # I would like to report the errant char here
        raise AuditFailure('malformed description', detail, level='WARNING')


@audit_checker('experiment')
def audit_experiment_assay(value, system):
    '''
    Experiments should have assays with valid ontologies term ids and names that
    are a valid synonym.
    '''
    if value['status'] == 'deleted':
        return

    if 'assay_term_id' not in value:
        detail = 'assay_term_id missing'
        yield AuditFailure('missing assay information', detail, level='ERROR')
        return

    if 'assay_term_name' not in value:
        detail = 'assay_term_name missing'
        yield AuditFailure('missing assay information', detail, level='ERROR')
        return

    ontology = system['registry']['ontology']
    term_id = value.get('assay_term_id')
    term_name = value.get('assay_term_name')

    if term_id.startswith('NTR:'):
        detail = '{} - {}'.format(term_id, term_name)
        yield AuditFailure('NTR, assay', detail, level='WARNING')
        return

    if term_id not in ontology:
        detail = 'assay_term_id - {}'.format(term_id)
        yield AuditFailure('assay term_id not in ontology', term_id, level='ERROR')
        return

    ontology_term_name = ontology[term_id]['name']
    modifed_term_name = term_name + ' assay'
    if (ontology_term_name != term_name and term_name not in ontology[term_id]['synonyms']) and \
        (ontology_term_name != modifed_term_name and
            modifed_term_name not in ontology[term_id]['synonyms']):
        detail = '{} - {} - {}'.format(term_id, term_name, ontology_term_name)
        yield AuditFailure('assay term name mismatch', detail, level='ERROR')
        return


@audit_checker('experiment')
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
        detail = '{} requires a target'.format(value['assay_term_name'])
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
            detail = 'rep {} missing antibody'.format(rep["uuid"])
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
                        detail = '{} not found in target for {}'.format(prefix, antibody['@id'])
                        yield AuditFailure('tag target mismatch', detail, level='ERROR')
            else:
                target_matches = False
                for antibody_target in antibody['targets']:
                    if target['name'] == antibody_target.get('name'):
                        target_matches = True
                if not target_matches:
                    detail = '{} not found in target for {}'.format(target['name'], antibody['@id'])
                    yield AuditFailure('target mismatch', detail, level='ERROR')


@audit_checker('experiment')
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

    # If there is no targets, for now we will just ignore it, likely this is an error
    if 'target' not in value:
        return

    # We do not want controls
    target = value['target']

    if value['possible_controls'] == []:
        detail = 'missing control'
        raise AuditFailure('missing possible controls', detail, level='ERROR')

    # A check should go here that would go through all possible controls to
    # verify that they are the same biosample term
    for control in value['possible_controls']:
        if control.get('biosample_term_id') != value.get('biosample_term_id'):
            detail = 'mismatch control'
            raise AuditFailure('control has mismatched biosample_id', detail, level='ERROR')


# @audit_checker('experiment')
# def audit_experiment_ownership(value, system):
#     '''
#     Do the award and lab make sense together. We may want to extend this to submitter
#     ENCODE2 and ENCODE2-Mouse data should have a dbxref for wgEncode
#     '''
#     if 'lab' not in value or 'award' not in value:
#         return
#         # should I make this an error case?
#     if value['award']['@id'] not in value['lab']['awards']:
#         detail = '{} is not part of {}'.format(value['lab']['name'], value['award']['name'])
#         yield AuditFailure('award mismatch', detail, level='ERROR')
#     if value['award']['rfa'] in ['ENCODE2', 'ENCODE2-Mouse']:
#         if 'wgEncode' not in value['dbxrefs']:
#             detail = '{} has no dbxref'.format(value['accession'])
#             raise AuditFailure('missing ENCODE2 dbxref', detail, level='ERROR')


@audit_checker('experiment')
def audit_experiment_platform(value, system):
    '''
    All ENCODE 3 experiments should specify thier platform, certain platforms require read_length.
    Eventually we should enforce that the platform is appropirate for the assay.
    '''

    if value['status'] in ['deleted', 'proposed']:
        return

    if ('award' not in value) or (value['award'].get('rfa') != 'ENCODE3') or (value['replicates'] == []):
        return

    for i in range(0, len(value['replicates'])):
        rep = value['replicates'][i]
        if 'platform' not in rep:
            detail = 'rep {} missing platform'.format(rep["uuid"])
            raise AuditFailure('missing platform', detail, level='WARNING')
        if value['assay_term_name'] in ['Proteogenomics']:  # There will be more
            return
        if 'read_length' not in rep:
            detail = 'rep {} missing read_length'.format(rep["uuid"])
            raise AuditFailure('missing read_length', detail, level='WARNING')


@audit_checker('experiment')
def audit_experiment_biosample_term(value, system):
    '''
    The biosample term and id and type information should be present and
    concordent with library biosamples,
    probably there are assays that are the exception
    '''
    if value['status'] in ['deleted', 'proposed']:
        return

    if 'biosample_term_id' not in value:
        return

    if 'biosample_type' not in value:
        detail = 'biosample type missing'
        yield AuditFailure('biosample type missing', detail, level='ERROR')
        return

    if 'target' in value:
        target = value['target']
        if 'control' in target['investigated_as']:
            return

    if 'biosample_term_id' not in value:
        yield AuditFailure('term id missing', detail, level='ERROR')

    ontology = system['registry']['ontology']
    term_id = value.get('biosample_term_id')
    term_type = value.get('biosample_type')
    term_name = value.get('biosample_term_name')

    if term_id.startswith('NTR:'):
        detail = '{} - {}'.format(term_id, term_name)
        yield AuditFailure('NTR,biosample', detail, level='WARNING')
        return

    if term_id not in ontology:
        yield AuditFailure('term id not in ontology', term_id, level='ERROR')
        return

    ontology_term_name = ontology[term_id]['name']
    if ontology_term_name != term_name and term_name not in ontology[term_id]['synonyms']:
        detail = '{} - {} - {}'.format(term_id, term_name, ontology_term_name)
        yield AuditFailure('term name mismatch', detail, level='ERROR')
        return

    for rep in value['replicates']:
        if 'library' not in rep:
            continue

        lib = rep['library']
        if 'biosample' not in lib:
            detail = '{} missing biosample, expected {}'.format(lib['accession'], term_name)
            yield AuditFailure('missing biosample', detail, level='ERROR')
            continue

        biosample = lib['biosample']
        if 'biosample_term_id' not in biosample or 'biosample_term_name' not in biosample or 'biosample_type' not in biosample:
            continue

        if biosample.get('biosample_type') != term_type:
            detail = '{} - {} in {}'.format(term_type, biosample.get('biosample_type'), lib['accession'])
            yield AuditFailure('biosample mismatch', detail, level='ERROR')

        if biosample.get('biosample_term_name') != term_name:
            detail = '{} - {} in {}'.format(term_name, biosample.get('biosample_term_name'), lib['accession'])
            yield AuditFailure('biosample mismatch', detail, level='ERROR')

        if biosample.get('biosample_term_id') != term_id:
            detail = '{} - {} in {}'.format(term_id, biosample.get('biosample_term_id'), lib['accession'])
            yield AuditFailure('biosample mismatch', detail, level='ERROR')


@audit_checker('experiment')
def audit_experiment_paired_end(value,system):
    '''
    Check that if the concordance of replicate and library information for paired end sequencing.
    '''
    ignore_assays = [
        "RNA Array",
        "Methyl Array",
        "Genotype",
        "RIP Array",
        "Proteogenomics",
        "microRNA Array",
        "Switchgear",
        "5C"
    ]

    paired_end_assays = [
        "RNA-PET",
        "ChIA-PET",
        "DNA-PET"
    ]

    if value['status'] in ['deleted', 'proposed']:
        return

    term_name = value.get('assay_term_name')

    if term_name in ignore_assays:
        return

    for rep in value['replicates']:
        if 'paired_ended' not in rep:
            detail = '{} missing paired end information'.format(rep['uuid'])
            yield AuditFailure('missing replicate paired end', detail, level='ERROR')

        if 'library' not in rep:
            continue

        lib = rep['library']

        if 'paired_ended' not in lib:
            detail = '{} missing paired end information'.format(lib['accession'])
            yield AuditFailure('missing library paired end', detail, level='ERROR')

        if 'paired_ended' not in rep or 'paired_ended' not in lib:
            continue

        if (rep['paired_ended'] is False or lib['paired_ended'] is False) and term_name in paired_end_assays:
            detail = 'paired ended required for {} either {} or {} is not paired ended'.format(term_name, rep['uuid'], lib['accession'])
            yield AuditFailure('paired end required for assay', detail, level='ERROR')

        if rep['paired_ended'] != lib['paired_ended'] and lib['paired_ended'] is False:
            detail = 'paired ended mismatch between {} - {}'.format(rep['uuid'], lib['accession'])
            yield AuditFailure('paired end mismatch', detail, level='ERROR')


@audit_checker('experiment')
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
        context = system['context']

        if 'histone modification' in target['investigated_as']:
            for lot_review in antibody['lot_reviews']:
                if (lot_review['status'] == 'eligible for new data') and (lot_review['biosample_term_id'] == 'NTR:00000000'):
                    organism_match = False
                    for lo in lot_review['organisms']:
                        lot_organism = find_resource(context, lo)
                        lot_organism_properties = lot_organism.upgrade_properties(finalize=False)
                        if organism == lot_organism_properties['name']:
                            organism_match = True
                    if not organism_match:
                        detail = '{} not eligible for {}'.format(antibody["@id"], organism)
                        yield AuditFailure('not eligible histone antibody', detail, level='ERROR')
                else:
                    detail = '{} not eligible for {}'.format(antibody["@id"], organism)
                    yield AuditFailure('not eligible histone antibody', detail, level='ERROR')
        else:
            biosample_term_id = value['biosample_term_id']
            biosample_term_name = value['biosample_term_name']
            experiment_biosample = set([biosample_term_id, organism])
            eligible_biosamples = set()
            for lot_review in antibody['lot_reviews']:
                if lot_review['status'] == 'eligible for new data':
                    for lo in lot_review['organisms']:
                        lot_organism = find_resource(context, lo)
                        lot_organism_properties = lot_organism.upgrade_properties(finalize=False)
                        eligible_biosample = frozenset([lot_review['biosample_term_id'], lot_organism_properties['name']])
                        eligible_biosamples.add(eligible_biosample)
            if experiment_biosample not in eligible_biosamples:
                detail = '{} not eligible for {} in {}'.format(antibody["@id"], biosample_term_name, organism)
                yield AuditFailure('not eligible antibody', detail, level='ERROR')
