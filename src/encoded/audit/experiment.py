from snovault import (
    AuditFailure,
    audit_checker,
)


from .pipeline_structures import (
    encode_chip_control,
    encode_chip_histone_experiment_pooled,
    encode_chip_tf_experiment_pooled,
    encode_chip_experiment_replicate,
    encode_chip_tf_experiment_unreplicated,
    encode_chip_histone_experiment_unreplicated
    )

def getPipelines(alignment_files):
    pipelines = set()
    for alignment_file in alignment_files:
        if 'analysis_step_version' in alignment_file and \
           'analysis_step' in alignment_file['analysis_step_version'] and \
           'pipelines' in alignment_file['analysis_step_version']['analysis_step']:
            for p in alignment_file['analysis_step_version']['analysis_step']['pipelines']:
                pipelines.add(p['title'])
    return pipelines

def scan_files_for_file_format_output_type(files_to_scan, f_format, f_output_type):
    files_to_return = []
    for f in files_to_scan:
        if 'file_format' in f and f['file_format'] == f_format and \
           'output_type' in f and f['output_type'] == f_output_type and \
           f['status'] not in ['replaced', 'revoked', 'deleted', 'archived']:
            files_to_return.append(f)
    return files_to_return

def get_bio_replicates(experiment):
    bio_reps = set()
    for f in experiment['original_files']:
        if f['status'] not in ['replaced', 'revoked', 'deleted', 'archived'] and f['file_format'] == 'fastq' and f.get('replicate'):
            rep = f.get('replicate')
            if rep['status'] not in ['deleted']:
                bio_reps.add(str(rep['biological_replicate_number']))
    return bio_reps

def get_assemblies(list_of_files):
    assemblies = set()
    for f in filter_files(list_of_files):
        if f['status'] not in ['replaced', 'revoked', 'deleted', 'archived'] and \
           f['output_category'] not in ['raw data', 'reference'] and \
           f.get('assembly') is not None and \
           f.get('assembly') not in ['mm9', 'mm10-minimal', 'GRCh38-minimal']:
                assemblies.add(f['assembly'])
    return assemblies

def filter_files(list_of_files):
    to_return = []
    for f in list_of_files:
        if f.get('lab') == '/labs/encode-processing-pipeline/' and \
            ((f.get('assembly') is None) or 
             (f.get('assembly') is not None and f.get('assembly') not in ['mm9', 'mm10-minimal', 'GRCh38-minimal'])):
            to_return.append(f)       
    return to_return


@audit_checker('Experiment', frame=['original_files',
                                    'original_files.replicate',
                                    'original_files.derived_from',
                                    'original_files.analysis_step_version',
                                    'original_files.analysis_step_version.analysis_step',
                                    'original_files.analysis_step_version.analysis_step.pipelines',
                                    'target',
                                    'award',
                                    'replicates'])
def audit_experiment_missing_processed_files(value, system):
    if value.get('award').get('project') != 'ENCODE' and value.get('assay_term_name') != 'ChIP-seq':
        return
    un_alignment_files = scan_files_for_file_format_output_type(value['original_files'],
                                                             'bam', 'alignments')
    un_alignment_files.extend(scan_files_for_file_format_output_type(value['original_files'],
                                                                  'bam',
                                                                  'unfiltered alignments'))
    un_alignment_files.extend(scan_files_for_file_format_output_type(value['original_files'],
                                                             'bed', 'peaks'))
    alignment_files = filter_files(un_alignment_files)

    # if there are no bam files - we don't know what pipeline, exit
    if len(alignment_files) == 0:
        return
    # find out the pipeline
    pipelines = getPipelines(alignment_files)
    if len(pipelines) == 0:  # no pipelines detected
        return

    target = value.get('target')
    if target is None:
        return
    
    
    # control
    if 'control' in target.get('investigated_as'):
        if 'ChIP-seq read mapping' in pipelines:
            # check if control
            replicate_structures = create_pipeline_structures(filter_files(value['original_files']),
                                                              'encode_chip_control')
            for failure in check_structures(replicate_structures, True, value):
                yield failure       
    #histone
    elif 'histone' in target.get('investigated_as'):
        if 'Histone ChIP-seq (unreplicated)' in pipelines:
            replicate_structures = create_pipeline_structures(
                filter_files(value['original_files']),
                'encode_chip_histone_experiment_unreplicated')
            for failure in check_structures(replicate_structures, False, value):
                yield failure
        elif  'Histone ChIP-seq' in pipelines:
            replicate_structures = create_pipeline_structures(
                filter_files(value['original_files']),
                'encode_chip_histone')
            for failure in check_structures(replicate_structures, False, value):
                yield failure
    #tf
    elif 'transcription factor' in target.get('investigated_as'):
        if 'Transcription factor ChIP-seq (unreplicated)' in pipelines:
            replicate_structures = create_pipeline_structures(
                filter_files(value['original_files']),
                'encode_chip_tf_experiment_unreplicated')
            for failure in check_structures(replicate_structures, False, value):
                yield failure       
        elif  'Transcription factor ChIP-seq' in pipelines:
            replicate_structures = create_pipeline_structures(
                filter_files(value['original_files']),
                'encode_chip_tf')
            for failure in check_structures(replicate_structures, False, value):
                yield failure




def check_structures(replicate_structures, control_flag, experiment):
    bio_reps = get_bio_replicates(experiment)
    assemblies = get_assemblies(experiment['original_files'])
    present_assemblies = []
    replicates_dict = {}
    for bio_rep in bio_reps:
        for assembly in assemblies:
            replicates_dict[(bio_rep, assembly)] = 0
    pooled_quantity = 0

    for (bio_rep_num, assembly) in replicate_structures.keys():
        replicates_string = bio_rep_num[1:-1]
        if len(replicates_string) > 0 and \
           is_single_replicate(replicates_string) is True:
            replicates_dict[(replicates_string, assembly)] = 1
        elif len(replicates_string) > 0 and is_single_replicate(replicates_string) is False:
            pooled_quantity += 1
            present_assemblies.append(assembly)

        if replicate_structures[(bio_rep_num, assembly)].has_orphan_files() is True:
            detail = 'Experiment {} contains '.format(experiment['@id']) + \
                     '{} '.format(replicate_structures[(bio_rep_num, assembly)].get_orphan_files()) + \
                     'files, genomic assembly {} '.format(assembly) + \
                     ' that are not associated with any replicate'
            yield AuditFailure('orphan pipeline files', detail, level='INTERNAL_ACTION')
        else:
            if replicate_structures[(bio_rep_num, assembly)].has_unexpected_files() is True:
                for unexpected_file in \
                        replicate_structures[(bio_rep_num, assembly)].get_unexpected_files():
                    detail = 'Experiment {} contains '.format(experiment['@id']) + \
                             'unexpected file {} '.format(unexpected_file) + \
                             'that is associated with ' + \
                             'biolofgical replicates {}.'.format(bio_rep_num)
                    yield AuditFailure('unexpected pipeline files', detail, level='INTERNAL_ACTION')

            if replicate_structures[(bio_rep_num, assembly)].is_complete() is False:
                for missing_tuple in \
                        replicate_structures[(bio_rep_num, assembly)].get_missing_fields_tuples():
                    if is_single_replicate(bio_rep_num[1:-1]) is True:
                        detail = 'In experiment {}, '.format(experiment['@id']) + \
                                 'biological replicate {}, '.format(bio_rep_num[1:-1]) + \
                                 'genomic assembly {} '.format(assembly) + \
                                 'the file {} is missing.'.format(missing_tuple)
                        yield AuditFailure('missing pipeline files', detail, level='INTERNAL_ACTION')
                    else:
                        detail = 'In experiment {}, '.format(experiment['@id']) + \
                                 'biological replicates {}, '.format(bio_rep_num) + \
                                 'genomic assembly {}, '.format(assembly) + \
                                 'the file {} is missing.'.format(missing_tuple)
                        yield AuditFailure('missing pipeline files', detail, level='INTERNAL_ACTION')

            if replicate_structures[(bio_rep_num, assembly)].is_analyzed_more_than_once() is True:
                detail = 'In experiment {}, '.format(experiment['@id']) + \
                         'biological replicate {} contains '.format(bio_rep_num) + \
                         'multiple processed files associated with the same fastq ' + \
                         'files for {} assembly.'.format(assembly)
                yield AuditFailure('mismatched pipeline files', detail, level='INTERNAL_ACTION')

    if pooled_quantity < (len(assemblies)) and control_flag is False and not is_single_replicate(replicates_string):
        detail = 'Experiment {} '.format(experiment['@id']) + \
                 'does not contain all of the inter-replicate comparison anlaysis files. ' + \
                 'Analysis was performed using {} assemblies, '.format(assemblies) + \
                 'while inter-replicate comparison anlaysis was performed only using ' + \
                 '{} assemblies.'.format(present_assemblies)
        yield AuditFailure('missing pipeline files', detail, level='INTERNAL_ACTION')
    for (rep_num, assembly) in replicates_dict:
        if replicates_dict[(rep_num, assembly)] == 0:
            detail = 'Experiment {} '.format(experiment['@id']) + \
                     'contains biological replicate {}, '.format(rep_num) + \
                     'without any processed files associated with {} assembly.'.format(assembly)
            yield AuditFailure('missing pipeline files', detail, level='INTERNAL_ACTION')
    return


def is_single_replicate(replicates_string):
    if ',' not in replicates_string:
        return True
    return False

def create_pipeline_structures(files_to_scan, structure_type):
    structures_mapping = {
        'encode_chip_control': encode_chip_control,
        'encode_chip_histone': encode_chip_histone_experiment_pooled,
        'encode_chip_tf': encode_chip_tf_experiment_pooled,
        'encode_chip_replicate': encode_chip_experiment_replicate,
        'encode_chip_tf_experiment_unreplicated': encode_chip_tf_experiment_unreplicated,
        'encode_chip_histone_experiment_unreplicated': encode_chip_histone_experiment_unreplicated
    }

    structures_to_return = {}
    replicates_set = set()
    for f in files_to_scan:
        if f['status'] not in ['replaced', 'revoked', 'deleted', 'archived'] and \
           f['output_category'] not in ['raw data', 'reference']:
            bio_rep_num = str(f.get('biological_replicates'))
            assembly = f.get('assembly')

            if (bio_rep_num, assembly) not in replicates_set:
                replicates_set.add((bio_rep_num, assembly))
                if structure_type in ['encode_chip_control']:
                    structures_to_return[(bio_rep_num, assembly)] = \
                        structures_mapping[structure_type]()
                else:
                    if structure_type == 'encode_chip_histone':
                        if is_single_replicate(str(bio_rep_num)) is True:
                            structures_to_return[(bio_rep_num, assembly)] = \
                                structures_mapping['encode_chip_replicate']()
                        else:
                            structures_to_return[(bio_rep_num, assembly)] = \
                                structures_mapping['encode_chip_histone']()
                    elif structure_type == 'encode_chip_tf':
                        if is_single_replicate(str(bio_rep_num)) is True:
                            structures_to_return[(bio_rep_num, assembly)] = \
                                structures_mapping['encode_chip_replicate']()
                        else:
                            structures_to_return[(bio_rep_num, assembly)] = \
                                structures_mapping['encode_chip_tf']()
                    elif structure_type == 'encode_chip_histone_experiment_unreplicated':
                        structures_to_return[(bio_rep_num, assembly)] = \
                                structures_mapping['encode_chip_histone_experiment_unreplicated']()
                    elif structure_type == 'encode_chip_tf_experiment_unreplicated':
                        structures_to_return[(bio_rep_num, assembly)] = \
                                structures_mapping['encode_chip_tf_experiment_unreplicated']()

                structures_to_return[(bio_rep_num, assembly)].update_fields(f)
            else:
                structures_to_return[(bio_rep_num, assembly)].update_fields(f)
    return structures_to_return

