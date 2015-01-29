from ..auditor import (
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
    'RIP-chip',
    'protein sequencing by tandem mass spectrometry assay',
    'microRNA profiling by array assay',
    'Switchgear',
    '5C',
    ]

paired_end_assays = [
    'RNA-PET',
    'ChIA-PET',
    'DNA-PET',
    ]


@audit_checker('experiment')
def audit_experiment_release_date(value, system):
    '''
    Released experiments need release date.
    This should eventually go to schema
    '''
    if value['status'] == 'released' and 'date_released' not in value:
        detail = 'Experiment {} is released and requires a value in date_released'.format(value['accession'])
        raise AuditFailure('missing date_released', detail, level='DCC_ACTION')


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

    notallowed = ['=', ':', '!', ';']
    if any(c in notallowed for c in value['description']):
        detail = 'Experiment {} has odd character(s) in the description'.format(value['accession'])
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
        detail = 'Experiment {} is missing assay_term_id'.format(value['accession'])
        yield AuditFailure('missing assay information', detail, level='ERROR')
        return
        # This should be a dependancy

    if 'assay_term_name' not in value:
        detail = 'Experiment {} is missing assay_term_name'.format(value['accession'])
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
            detail = 'Replicate {} requires an antibody'.format(rep['uuid'])
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
                        detail = '{} is not found in target for {}'.format(prefix, antibody['@id'])
                        yield AuditFailure('tag target mismatch', detail, level='ERROR')
            else:
                target_matches = False
                for antibody_target in antibody['targets']:
                    if target['name'] == antibody_target.get('name'):
                        target_matches = True
                if not target_matches:
                    detail = '{} is not found in target for {}'.format(target['name'], antibody['@id'])
                    yield AuditFailure('mismatched target', detail, level='ERROR')


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
                control['accession'],
                control['biosample_term_name'],
                value['biosample_term_name'])
            raise AuditFailure('mismatched control', detail, level='ERROR')


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

    if value['award'].get('rfa') in ['ENCODE2', 'ENCODE2-Mouse']:
        return

    read_lengths = []

    for i in range(len(value['replicates'])):
        rep = value['replicates'][i]
        read_length = rep.get('read_length')
        read_lengths.append(read_length)

        if read_length is None:
            detail = 'Replicate {} requires a value for read_length'.format(rep['uuid'])
            yield AuditFailure('missing read_length', detail, level='ERROR')

    if len(set(read_lengths)) > 1:
        list_of_lens = str(read_lengths)
        detail = '{} has mixed values for read_length between replicates: {}'.format(value['accession'], list_of_lens)
        yield AuditFailure('mismatched read_length', detail, level='WARNING')


@audit_checker('experiment')
def audit_experiment_platform(value, system):
    '''
    Platform has moved to file.  It is checked for presence there.
    Here we look for mismatched platforms.
    We should likely check that the platform is valid for the assay type
    '''

    if value['status'] in ['deleted', 'replaced']:
        return

    platforms = set()

    for ff in value['files']:
        platform = ff.get('platform')

        if ff['file_format'] not in ['rcc', 'fasta', 'fastq', 'csqual', 'csfasta']:
            continue

        if platform is None:
            continue  # This error is caught in file
        else:
            platforms.add(platform['@id'])

    if len(platforms) > 1:
        detail = '{} has mixed values for platform files {}'.format(
            value['accession'],
            repr(sorted(platforms)))
        yield AuditFailure('mismatched platform', detail, level='WARNING')


@audit_checker('experiment')
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
            detail = 'Library {} is in an RNA-seq experiment and has size_range >200. It requires a value for spikeins_used'.format(lib['accession'])
            yield AuditFailure('missing spikeins_used', detail, level='NOT_COMPLIANT')
            # Informattional if ENCODE2 and release error if ENCODE3


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
        detail = '{} is missing biosample_type'.format(value['accession'])
        yield AuditFailure('missing biosample_type', detail, level='ERROR')

    if 'biosample_term_name' not in value:
        detail = '{} is missing biosample_term_name'.format(value['accession'])
        yield AuditFailure('missing biosample_term_name', detail, level='ERROR')
    # The type and term name should be put into dependancies

    if term_id is None:
        detail = '{} is missing biosample_term_id'.format(value['accession'])
        yield AuditFailure('missing biosample_term_id', detail, level='ERROR')
    elif term_id.startswith('NTR:'):
        detail = '{} has {} - {}'.format(value['accession'], term_id, term_name)
        yield AuditFailure('NTR biosample', detail, level='DCC_ACTION')
    elif term_id not in ontology:
        detail = '{} has term_id {} which is not in ontology'.format(value['accession'], term_id)
        yield AuditFailure('term_id not in ontology', term_id, level='DCC_ACTION')
    else:
        ontology_name = ontology[term_id]['name']
        if ontology_name != term_name and term_name not in ontology[term_id]['synonyms']:
            detail = '{} has {} - {} - {}'.format(
                value['accession'],
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
            detail = '{} is missing biosample, expected is {}'.format(lib['accession'], term_name)
            yield AuditFailure('missing biosample', detail, level='NOT_COMPLIANT')
            continue

        biosample = lib['biosample']
        bs_type = biosample.get('biosample_type')
        bs_name = biosample.get('biosample_term_name')

        if bs_type != term_type:
            detail = '{} has mismatched biosample_type, {} - {}'.format(
                lib['accession'],
                term_type,
                bs_type
                )
            yield AuditFailure('mismatched biosample_type', detail, level='ERROR')

        if bs_name != term_name:
            detail = '{} has mismatched biosample_term_name, {} - {}'.format(lib['accession'], term_name, bs_name)
            yield AuditFailure('mismatched biosample_term_name', detail, level='ERROR')


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
        if rep_paired_ended is not None:
            reps_list.append(rep_paired_ended)

        if rep_paired_ended is None:
            detail = 'Replicate {} is missing value for paired_ended'.format(rep['uuid'])
            yield AuditFailure('missing replicate.paired_ended', detail, level='ERROR')

        if (rep_paired_ended is False) and (term_name in paired_end_assays):
            detail = '{} experiments require paired end replicates. {}.paired_ended is False'.format(term_name, rep['uuid'])
            yield AuditFailure('paired end required for assay', detail, level='ERROR')

        if 'library' not in rep:
            continue

        lib = rep['library']
        lib_paired_ended = lib.get('paired_ended')
        if lib_paired_ended is not None:
            libs_list.append(lib_paired_ended)

        if lib_paired_ended is None:
            detail = '{} is missing value for paired_ended'.format(lib['accession'])
            yield AuditFailure('missing library.paired_ended', detail, level='WARNING')

        if (lib_paired_ended is False) and (term_name in paired_end_assays):
            detail = '{} experiments require paired end libraries. {}.paired_ended is False'.format(term_name, lib['accession'])
            yield AuditFailure('paired end required for assay', detail, level='ERROR')

        if (rep_paired_ended is True) and (lib_paired_ended is False):
            detail = 'Library {} has paired_ended as false and replicate {} is not false'.format(lib['accession'], rep['uuid'])
            yield AuditFailure('mismatched paired_ended', detail, level='ERROR')

    if len(set(reps_list)) > 1:
            detail = '{} has mixed paired_ended replicates: {}'.format(value['accession'], repr(reps_list))
            yield AuditFailure('mismatched paired_ended', detail, level='WARNING')

    if len(set(libs_list)) > 1:
            detail = '{} has mixed paired_ended libraries: {}'.format(value['accession'], repr(reps_list))
            yield AuditFailure('mismatched paired_ended', detail, level='WARNING')


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
    condition=rfa('ENCODE3', 'FlyWormChIP'))
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
                        yield AuditFailure('not eligible histone antibody', detail, level='NOT_COMPLIANT')
                else:
                    detail = '{} is not eligible for {}'.format(antibody["@id"], organism)
                    yield AuditFailure('not eligible histone antibody', detail, level='NOT_COMPLIANT')
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
