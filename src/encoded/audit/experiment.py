
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

seq_assays = ['RNA-seq',
              'ChIP-seq',
              'RNA Bind-n-Seq',
              'MeDIP-seq',
              'RNA-PET',
              'DNA-PET',
              'ChIA-PET',
              'CAGE',
              'RAMPAGE',
              'RIP-seq'
              ]

non_seq_assays = ["RNA profiling by array assay",
                  "DNA methylation profiling by array assay",
                  "Genotype",
                  "RIP-chip",
                  "protein sequencing by tandem mass spectrometry assay",
                  "microRNA profiling by array assay",
                  "Switchgear",
                  "5C"
                  ]

paired_end_assays = ["RNA-PET",
                     "ChIA-PET",
                     "DNA-PET"
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
def audit_experiment_readlength(value, system):
    '''
    All ENCODE 3 experiments of sequencing type should specify their read_length
    Read-lengths should likely match across replicates
    Other rfas likely should have warning
    '''

    if value['status'] in ['deleted', 'replaced']:
        return

    if value.get('assay_term_name') not in seq_assays:
        return

    if ('award' not in value) or (value['award'].get('rfa') in ['ENCODE2', 'ENCODE2-Mouse']): # or (value['replicates'] == []):  # This logic seems redundant
        return

    read_lengths = []

    for i in range(len(value['replicates'])):
        rep = value['replicates'][i]
        read_length = rep.get('read_length')
        read_lengths.append(read_length)

        if read_length is None:
            detail = 'rep {} missing read_length'.format(rep['uuid'])
            yield AuditFailure('missing read length', detail, level='WARNING')  # release error

    if len(set(read_lengths)) > 1:
        list_of_lens = str(read_lengths)
        detail = '{} has mixed read_length replicates: {}'.format(value['accession'], list_of_lens)
        yield AuditFailure('read_length mismatch', detail, level='ERROR')  # informational


@audit_checker('experiment')
def audit_experiment_platform(value, system):
    '''
    All ENCODE 3 experiments should specify thier platform.
    Eventually we should enforce that the platform is appropirate for the assay.
    Other rfas likely should have warning
    '''

    if value['status'] in ['deleted', 'replaced']:
        return

    if (value['award'].get('rfa') != 'ENCODE3'):  # or (value['replicates'] == []):  # This logic seems redundant
        return

    platforms = []

    for i in range(len(value['replicates'])):
        rep = value['replicates'][i]
        platform = rep.get('platform')  # really need to get the name here?
        platforms.append(platform)

        if platform is None:
            detail = '{} missing platform'.format(rep["uuid"])
            yield AuditFailure('missing platform', detail, level='WARNING')  # release error

    if len(set(platforms)) > 1:
        detail = '{} has mixed platform replicates'.format(value['accession'])
        yield AuditFailure('platform mismatch', detail, level='ERROR')  # informational


@audit_checker('experiment')
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
        detail = '{} missing biosample_type'.format(value['accession'])
        yield AuditFailure('biosample type missing', detail, level='ERROR')  # release error

    if 'biosample_term_name' not in value:
        detail = '{} missing biosample_term_name'.format(value['accession'])
        yield AuditFailure('missing biosample_term_name', detail, level='ERROR')  # release error
    # The type and term name should be put into dependancies

    if term_id is None:
        detail = '{} missing biosample_term_id'.format(value['accession'])
        yield AuditFailure('missing biosample_term_id', detail, level='ERROR')  # release error
    elif term_id.startswith('NTR:'):
        detail = '{} has {} - {}'.format(value['accession'], term_id, term_name)
        yield AuditFailure('NTR,biosample', detail, level='WARNING')  # DCC Error
    elif term_id not in ontology:
        detail = '{} has term_id {} not in ontology'.format(value['accession'], term_id)
        yield AuditFailure('term id not in ontology', term_id, level='ERROR')
    else:
        ontology_name = ontology[term_id]['name']
        if ontology_name != term_name and term_name not in ontology[term_id]['synonyms']:
            detail = '{} has {} - {} - {}'.format(value['accession'], term_id, term_name, ontology_name)
            yield AuditFailure('term name mismatch', detail, level='ERROR')

    for rep in value['replicates']:
        if 'library' not in rep:
            continue

        lib = rep['library']
        if 'biosample' not in lib:
            detail = '{} missing biosample, expected {}'.format(lib['accession'], term_name)
            yield AuditFailure('missing biosample', detail, level='ERROR')  # release error
            continue

        biosample = lib['biosample']
        bs_type = biosample.get('biosample_type')
        bs_name = biosample.get('biosample_term_name')
        bs_id = biosample.get('biosample_term_id')

        if bs_type != term_type:
            detail = '{} has mismatched biosample_type {} - {}'.format(lib['accession'], term_type, bs_type)
            yield AuditFailure('biosample mismatch', detail, level='ERROR')

        if bs_name != term_name:
            detail = '{} has mismatched biosample_term_name {} - {}'.format(lib['accession'], term_name, bs_name)
            yield AuditFailure('biosample mismatch', detail, level='ERROR')
            # This is propbably a duplicate warning to the biosample mismatches

        if bs_id != term_id:
            detail = '{} has a mismatched biosample_term_id {} - {}'.format(lib['accession'], term_id, bs_id)
            yield AuditFailure('biosample mismatch', detail, level='ERROR')


@audit_checker('experiment')
def audit_experiment_paired_end(value, system):
    '''
    Libraries and replicates of certain assays should be paired end.
    Libraries and replicates of ignore_assays are not applicable for paired_end.
    All other libraries and replicates should have a value for paired_end.
    If a replicate says it is paired_end and it's library does not, that is an error.
    If a library says it is paired_end and it's replicate is not, that is informational.
    If two replicates do not match, that is a warning.
    '''

    if value['status'] in ['deleted', 'replaced']:
        return

    term_name = value.get('assay_term_name')

    if (term_name in non_seq_assays) or (term_name is None):
        return

    reps_list = []
    libs_list = []

    for rep in value['replicates']:

        rep_paired_ended = rep.get('paired_ended')
        reps_list.append(rep_paired_ended)

        if rep_paired_ended is None:
            detail = '{} missing paired_ended'.format(rep['uuid'])
            yield AuditFailure('missing replicate paired end', detail, level='ERROR')
            # release error

        if (rep_paired_ended is False) and (term_name in paired_end_assays):
            detail = '{} requires paired end. {}.paired_ended is False'.format(term_name, rep['uuid'])
            yield AuditFailure('paired end required for assay', detail, level='ERROR')

        if 'library' not in rep:
            continue

        lib = rep['library']
        lib_paired_ended = lib.get('paired_ended')
        libs_list.append(lib_paired_ended)

        if lib_paired_ended is None:
            detail = '{} missing paired_ended'.format(lib['accession'])
            yield AuditFailure('missing library paired end', detail, level='ERROR')
            # release error

        if (lib_paired_ended is False) and (term_name in paired_end_assays):
            detail = '{} requires paired end. {}.paired_ended is False'.format(term_name, lib['accession'])
            yield AuditFailure('paired end required for assay', detail, level='ERROR')

        if (rep_paired_ended != lib_paired_ended) and (lib_paired_ended is False):
            detail = 'paired ended mismatch between {} - {}'.format(rep['uuid'], lib['accession'])
            yield AuditFailure('paired end mismatch', detail, level='ERROR')

    if len(set(reps_list)) > 1:
            detail = '{} has mixed paired_ended replicates: {}'.format(value['accession'], string(reps_list))
            yield AuditFailure('paired end mismatch', detail, level='ERROR')  # informational

    if len(set(libs_list)) > 1:
            detail = '{} has mixed paired_ended libraries: {}'.format(value['accession'], string(reps_list))
            yield AuditFailure('paired end mismatch', detail, level='ERROR')  # informational


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
