from snovault import (
    AuditFailure,
    audit_checker,
)
from .conditions import rfa
from .ontology_data import (biosampleType_ontologyPrefix, NTR_assay_lookup)
from .gtex_data import gtexDonorsList
from .standards_data import pipelines_with_read_depth

from .pipeline_structures import (
    modERN_TF_control,
    modERN_TF_replicate,
    modERN_TF_pooled,
    encode_chip_control,
    encode_chip_histone_experiment_pooled,
    encode_chip_tf_experiment_pooled,
    encode_chip_experiment_replicate,
    encode_rampage_experiment_replicate,
    encode_rampage_experiment_pooled
    )


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
    'siRNA knockdown followed by RNA-seq',
    'CRISPR genome editing followed by RNA-seq',
    ]

controlRequiredAssayList = [
    'ChIP-seq',
    'RNA Bind-n-Seq',
    'RIP-seq',
    'RAMPAGE',
    'CAGE',
    'eCLIP',
    'single cell isolation followed by RNA-seq',
    'shRNA knockdown followed by RNA-seq',
    'siRNA knockdown followed by RNA-seq',
    'CRISPR genome editing followed by RNA-seq',
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


@audit_checker('experiment', frame=['replicates',
                                    'replicates.library'])
def audit_experiment_mixed_libraries(value, system):
    '''
    Experiments should not have mixed libraries nucleic acids
    '''
    if value['status'] in ['deleted', 'replaced']:
        return

    if 'replicates' not in value:
        return

    nucleic_acids = set()

    for rep in value['replicates']:
        if 'library' in rep and rep['library']['status'] not in ['deleted',
                                                                 'replaced',
                                                                 'revoked']:
            if 'nucleic_acid_term_name' in rep['library']:
                nucleic_acids.add(rep['library']['nucleic_acid_term_name'])

    if len(nucleic_acids) > 1:
        detail = 'Experiment {} '.format(value['@id']) + \
                 'contains libraries with mixed nucleic acids {} '.format(nucleic_acids)
        yield AuditFailure('mixed libraries', detail, level='INTERNAL_ACTION')
    return


@audit_checker('Experiment', frame=['original_files',
                                    'original_files.replicate',
                                    'original_files.derived_from',
                                    'original_files.analysis_step_version',
                                    'original_files.analysis_step_version.analysis_step',
                                    'original_files.analysis_step_version.analysis_step.pipelines'])
def audit_experiment_pipeline_assay_details(value, system):
    if 'original_files' not in value or len(value['original_files']) == 0:
        return
    if 'assay_term_id' not in value:
        return
    files_to_check = []
    for f in value['original_files']:
        if f['status'] not in ['replaced', 'revoked', 'deleted', 'archived']:
            files_to_check.append(f)
    pipelines = get_pipeline_objects(files_to_check)
    reported_pipelines = []
    for p in pipelines:
        if 'assay_term_id' not in p:
            continue
        if p['assay_term_id'] != value['assay_term_id'] and \
           p['assay_term_id'] not in reported_pipelines:
                reported_pipelines.append(p['assay_term_id'])
                detail = 'This experiment ' + \
                         'contains file(s) associated with ' + \
                         'pipeline {} '.format(p['@id']) + \
                         'which assay_term_id does not match experiments\'s asssay_term_id.'
                yield AuditFailure('inconsistent assay_term_name', detail, level='INTERNAL_ACTION')


@audit_checker('Experiment', frame=['original_files',
                                    'original_files.replicate',
                                    'original_files.derived_from',
                                    'original_files.analysis_step_version',
                                    'original_files.analysis_step_version.analysis_step',
                                    'original_files.analysis_step_version.analysis_step.pipelines',
                                    'target',
                                    'replicates'],
               condition=rfa('modERN'))
def audit_experiment_missing_processed_files(value, system):
    alignment_files = scan_files_for_file_format_output_type(value['original_files'],
                                                             'bam', 'alignments')
    alignment_files.extend(scan_files_for_file_format_output_type(value['original_files'],
                                                                  'bam',
                                                                  'unfiltered alignments'))
    alignment_files.extend(scan_files_for_file_format_output_type(value['original_files'],
                                                                  'bam',
                                                                  'transcriptome alignments'))

    # if there are no bam files - we don't know what pipeline, exit
    if len(alignment_files) == 0:
        return
    # find out the pipeline
    pipelines = getPipelines(alignment_files)
    if len(pipelines) == 0:  # no pipelines detected
        return

    if 'Transcription factor ChIP-seq pipeline (modERN)' in pipelines:
        # check if control
        target = value.get('target')
        if target is None:
            return
        if 'control' in target.get('investigated_as'):
            replicate_structures = create_pipeline_structures(value['original_files'],
                                                              'modERN_control')
            for failure in check_structures(replicate_structures, True, value):
                yield failure
        else:
            replicate_structures = create_pipeline_structures(value['original_files'],
                                                              'modERN')
            for failure in check_structures(replicate_structures, False, value):
                yield failure


@audit_checker('Experiment', frame=['original_files',
                                    'original_files.analysis_step_version',
                                    'original_files.analysis_step_version.analysis_step',
                                    'original_files.analysis_step_version.analysis_step.pipelines',
                                    'original_files.derived_from'])
def audit_experiment_missing_unfiltered_bams(value, system):
    if 'assay_term_id' not in value:  # unknown assay
        return
    if value['assay_term_id'] != 'OBI:0000716':  # not a ChIP-seq
        return

    alignment_files = scan_files_for_file_format_output_type(value['original_files'],
                                                             'bam', 'alignments')

    unfiltered_alignment_files = scan_files_for_file_format_output_type(value['original_files'],
                                                                        'bam',
                                                                        'unfiltered alignments')
    # if there are no bam files - we don't know what pipeline, exit
    if len(alignment_files) == 0:
        return
    # find out the pipeline
    pipelines = getPipelines(alignment_files)

    if len(pipelines) == 0:  # no pipelines detected
        return

    if 'Histone ChIP-seq' in pipelines or \
       'Transcription factor ChIP-seq' in pipelines:

        for filtered_file in alignment_files:
            if has_only_raw_files_in_derived_from(filtered_file) and \
               has_no_unfiltered(filtered_file, unfiltered_alignment_files):

                detail = 'Experiment {} contains biological replicate '.format(value['@id']) + \
                         '{} '.format(filtered_file['biological_replicates']) + \
                         'with a filtered alignments file {}, mapped to '.format(filtered_file['@id']) + \
                         'a {} assembly, '.format(filtered_file['assembly']) + \
                         'but has no unfiltered alignments file.'
                yield AuditFailure('missing unfiltered alignments', detail, level='INTERNAL_ACTION')


def has_only_raw_files_in_derived_from(bam_file):
    if 'derived_from' in bam_file:
        if bam_file['derived_from'] == []:
            return False
        for f in bam_file['derived_from']:
            if f['file_format'] not in ['fastq', 'tar', 'fasta']:
                return False
        return True
    else:
        return False


def has_no_unfiltered(filtered_bam, unfiltered_bams):
    if 'assembly' in filtered_bam:
        for f in unfiltered_bams:
            if 'assembly' in f:
                if f['assembly'] == filtered_bam['assembly'] and \
                   f['biological_replicates'] == filtered_bam['biological_replicates']:
                    derived_candidate = set()
                    derived_filtered = set()
                    if 'derived_from' in f:
                        for entry in f['derived_from']:
                            derived_candidate.add(entry['uuid'])
                    if 'derived_from' in filtered_bam:
                        for entry in filtered_bam['derived_from']:
                            derived_filtered.add(entry['uuid'])
                    if derived_candidate == derived_filtered:
                        return False
        return True
    return False


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
                             'biological replicates {}.'.format(bio_rep_num)
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
                yield AuditFailure('inconsistent pipeline files', detail, level='INTERNAL_ACTION')

    if pooled_quantity < (len(assemblies)) and control_flag is False:
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
        'modERN_control': modERN_TF_control,
        'modERN_pooled': modERN_TF_pooled,
        'modERN_replicate': modERN_TF_replicate
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
                if structure_type in ['modERN_control']:
                    structures_to_return[(bio_rep_num, assembly)] = \
                        structures_mapping[structure_type]()
                else:
                    if structure_type == 'modERN':
                        if is_single_replicate(str(bio_rep_num)) is True:
                            structures_to_return[(bio_rep_num, assembly)] = \
                                structures_mapping['modERN_replicate']()
                        else:
                            structures_to_return[(bio_rep_num, assembly)] = \
                                structures_mapping['modERN_pooled']()

                structures_to_return[(bio_rep_num, assembly)].update_fields(f)
            else:
                structures_to_return[(bio_rep_num, assembly)].update_fields(f)
    return structures_to_return


def get_bio_replicates(experiment):
    bio_reps = set()
    for rep in experiment['replicates']:
        if rep['status'] not in ['deleted']:
            bio_reps.add(str(rep['biological_replicate_number']))
    return bio_reps


def get_assemblies(list_of_files):
    assemblies = set()
    for f in list_of_files:
        if f['status'] not in ['replaced', 'revoked', 'deleted', 'archived'] and \
           f['output_category'] not in ['raw data', 'reference'] and \
           f.get('assembly') is not None:
                assemblies.add(f['assembly'])
    return assemblies


@audit_checker('Experiment', frame=[
    'target',
    'original_files',
    'original_files.derived_from',
    'original_files.derived_from.derived_from',
    'original_files.derived_from.dataset',
    'original_files.derived_from.dataset.original_files'])
def audit_experiment_control_out_of_date_analysis(value, system):
    if value['assay_term_name'] not in ['ChIP-seq']:
        return
    if 'target' in value and 'investigated_as' in value['target'] and \
       'control' in value['target']['investigated_as']:
        return
    all_signal_files = scan_files_for_file_format_output_type(value['original_files'],
                                                              'bigWig', 'signal p-value')
    signal_files = []
    for signal_file in all_signal_files:
        if 'lab' in signal_file and signal_file['lab'] == '/labs/encode-processing-pipeline/':
            signal_files.append(signal_file)

    if len(signal_files) == 0:
        return

    derived_from_bams = get_derived_from_files_set(signal_files, 'bam', True)
    for bam_file in derived_from_bams:
        if bam_file['dataset']['accession'] != value['accession'] and \
           is_outdated_bams_replicate(bam_file):
            detail = 'Experiment {} '.format(value['@id']) + \
                     'processed files are using alignment files from a control ' + \
                     'replicate that is out of date.'
            yield AuditFailure('out of date analysis', detail, level='INTERNAL_ACTION')
            return


def is_outdated_bams_replicate(bam_file):
    if 'lab' not in bam_file or bam_file['lab'] != '/labs/encode-processing-pipeline/' or \
       'dataset' not in bam_file or 'original_files' not in bam_file['dataset']:
        return False
    derived_from_fastqs = get_derived_from_files_set([bam_file], 'fastq', True)
    if len(derived_from_fastqs) == 0:
        return False

    derived_from_fastq_accessions = get_file_accessions(derived_from_fastqs)

    bio_rep = []
    for fastq_file in derived_from_fastqs:
        if 'biological_replicates' in fastq_file and \
           len(fastq_file['biological_replicates']) != 0:
            for entry in fastq_file['biological_replicates']:
                bio_rep.append(entry)
            break

    fastq_files = scan_files_for_file_format_output_type(
        bam_file['dataset']['original_files'],
        'fastq', 'reads')

    bio_rep_fastqs = []
    for fastq_file in fastq_files:
        if 'biological_replicates' in fastq_file:
            for entry in fastq_file['biological_replicates']:
                if entry in bio_rep:
                    bio_rep_fastqs.append(fastq_file)
                    break

    replicate_fastq_accessions = get_file_accessions(bio_rep_fastqs)
    for f_accession in replicate_fastq_accessions:
        if f_accession not in derived_from_fastq_accessions:
            return True

    for f_accession in derived_from_fastq_accessions:
        if f_accession not in replicate_fastq_accessions:
            return True
    return False


@audit_checker('Experiment', frame=['original_files'])
def audit_experiment_with_uploading_files(value, system):
    if 'original_files' not in value:
        return
    for f in value['original_files']:
        if f['status'] in ['uploading', 'upload failed']:
            detail = 'Experiment {} '.format(value['@id']) + \
                     'contains a file {} '.format(f['@id']) + \
                     'with the status {}.'.format(f['status'])
            yield AuditFailure('not uploaded files', detail, level='INTERNAL_ACTION')


@audit_checker('Experiment', frame=['original_files',
                                    'original_files.replicate',
                                    'original_files.derived_from'])
def audit_experiment_out_of_date_analysis(value, system):
    alignment_files = scan_files_for_file_format_output_type(value['original_files'],
                                                             'bam', 'alignments')
    not_filtered_alignments = scan_files_for_file_format_output_type(
        value['original_files'],
        'bam', 'unfiltered alignments')
    transcriptome_alignments = scan_files_for_file_format_output_type(value['original_files'],
                                                                      'bam',
                                                                      'transcriptome alignments')
    if len(alignment_files) == 0 and len(transcriptome_alignments) == 0 and \
       len(not_filtered_alignments) == 0:
        return  # probably needs pipeline, since there are no processed files

    uniform_pipeline_flag = False
    for bam_file in alignment_files:
        if bam_file['lab'] == '/labs/encode-processing-pipeline/':
            uniform_pipeline_flag = True
            break
    for bam_file in transcriptome_alignments:
        if bam_file['lab'] == '/labs/encode-processing-pipeline/':
            uniform_pipeline_flag = True
            break
    for bam_file in not_filtered_alignments:
        if bam_file['lab'] == '/labs/encode-processing-pipeline/':
            uniform_pipeline_flag = True
            break
    if uniform_pipeline_flag is False:
        return
    alignment_derived_from = get_derived_from_files_set(alignment_files, 'fastq', False)
    transcriptome_alignment_derived_from = get_derived_from_files_set(
        transcriptome_alignments, 'fastq', False)
    not_filtered_alignment_derived_from = get_derived_from_files_set(
        not_filtered_alignments, 'fastq', False)

    derived_from_set = alignment_derived_from | \
        not_filtered_alignment_derived_from | \
        transcriptome_alignment_derived_from

    fastq_files = scan_files_for_file_format_output_type(value['original_files'],
                                                         'fastq', 'reads')
    fastq_accs = get_file_accessions(fastq_files)

    orfan_fastqs = set()
    for f_accession in fastq_accs:
        if f_accession not in derived_from_set:
            orfan_fastqs.add(f_accession)
    lost_fastqs = set()
    for f_accession in derived_from_set:
        if f_accession not in fastq_accs:
            lost_fastqs.add(f_accession)

    if len(orfan_fastqs) > 0:
        orfan_bio_reps = set()

        for fastq_f in fastq_files:
            if fastq_f['accession'] in orfan_fastqs:
                if 'replicate' in fastq_f:
                    orfan_bio_reps.add(fastq_f['replicate']['biological_replicate_number'])
        detail = 'Experiment {} '.format(value['@id']) + \
                 'biological replicates {} '.format(orfan_bio_reps) + \
                 'contain FASTQ files {} '.format(orfan_fastqs) + \
                 ' that have not been processed.'
        yield AuditFailure('out of date analysis', detail, level='INTERNAL_ACTION')

    if len(lost_fastqs) > 0:
        detail = 'Experiment {} '.format(value['@id']) + \
                 'processed files contain in derived_from list FASTQ files {} '.format(lost_fastqs) + \
                 ' that are no longer eligible for analysis.'
        yield AuditFailure('out of date analysis', detail, level='INTERNAL_ACTION')


def get_file_accessions(list_of_files):
    accessions_set = set()
    for f in list_of_files:
        accessions_set.add(f['accession'])
    return accessions_set


def get_derived_from_files_set(list_of_files, file_format, object_flag):
    derived_from_set = set()
    derived_from_objects_list = []
    for f in list_of_files:
        if 'derived_from' in f:
            for d_f in f['derived_from']:
                if 'file_format' in d_f and d_f['file_format'] == file_format and \
                   d_f['accession'] not in derived_from_set:
                    derived_from_set.add(d_f['accession'])
                    if object_flag:
                        derived_from_objects_list.append(d_f)
    if object_flag:
        return derived_from_objects_list
    return derived_from_set


@audit_checker('Experiment', frame=['original_files',
                                    'award',
                                    'target',
                                    'replicates',
                                    'replicates.library',
                                    'replicates.library.spikeins_used',
                                    'replicates.library.spikeins_used.files',
                                    'replicates.library.biosample',
                                    'replicates.library.biosample.organism',
                                    'original_files.quality_metrics',
                                    'original_files.quality_metrics.quality_metric_of',
                                    'original_files.quality_metrics.quality_metric_of.replicate',
                                    'original_files.derived_from',
                                    'original_files.analysis_step_version',
                                    'original_files.analysis_step_version.software_versions',
                                    'original_files.analysis_step_version.software_versions.software',
                                    'original_files.analysis_step_version.analysis_step',
                                    'original_files.analysis_step_version.analysis_step.pipelines'],
               condition=rfa('ENCODE3', 'ENCODE2-Mouse', 'ENCODE2', 'ENCODE', 'Roadmap'))
def audit_experiment_standards_dispatcher(value, system):
    '''
    Dispatcher function that will redirect to other functions that would
    deal with specific assay types standards
    '''
    #if value['status'] not in ['released', 'release ready']:
    if value['status'] in ['revoked', 'deleted', 'replaced']:
        return
    if 'assay_term_name' not in value or \
       value['assay_term_name'] not in ['DNase-seq', 'RAMPAGE', 'RNA-seq', 'ChIP-seq', 'CAGE',
                                        'shRNA knockdown followed by RNA-seq',
                                        'siRNA knockdown followed by RNA-seq',
                                        'CRISPR genome editing followed by RNA-seq',
                                        'single cell isolation followed by RNA-seq',
                                        'whole-genome shotgun bisulfite sequencing']:
        return
    if 'original_files' not in value or len(value['original_files']) == 0:
        return
    if 'replicates' not in value:
        return

    num_bio_reps = set()
    for rep in value['replicates']:
        num_bio_reps.add(rep['biological_replicate_number'])

    if len(num_bio_reps) < 1:
        return

    organism_name = get_organism_name(value['replicates'])  # human/mouse
    if organism_name == 'human':
        desired_assembly = 'GRCh38'
        desired_annotation = 'V24'
    else:
        if organism_name == 'mouse':
            desired_assembly = 'mm10'
            desired_annotation = 'M4'
        else:
            return

    alignment_files = scan_files_for_file_format_output_type(value['original_files'],
                                                             'bam', 'alignments')

    fastq_files = scan_files_for_file_format_output_type(value['original_files'],
                                                         'fastq', 'reads')

    standards_version = 'ENC3'

    if value['assay_term_name'] in ['DNase-seq']:
        hotspots = scanFilesForOutputType(value['original_files'],
                                          'hotspots')
        signal_files = scanFilesForOutputType(value['original_files'],
                                              'signal of unique reads')
        for failure in check_experiment_dnase_seq_standards(value,
                                                            fastq_files,
                                                            alignment_files,
                                                            hotspots,
                                                            signal_files,
                                                            desired_assembly,
                                                            desired_annotation,
                                                            ' /data-standards/dnase-seq/ '):
            yield failure
        return
    if value['assay_term_name'] in ['RAMPAGE', 'RNA-seq', 'CAGE',
                                    'shRNA knockdown followed by RNA-seq',
                                    'siRNA knockdown followed by RNA-seq',
                                    'CRISPR genome editing followed by RNA-seq',
                                    'single cell isolation followed by RNA-seq']:
        gene_quantifications = scanFilesForOutputType(value['original_files'],
                                                      'gene quantifications')
        for failure in check_experiment_rna_seq_standards(value,
                                                          fastq_files,
                                                          alignment_files,
                                                          gene_quantifications,
                                                          desired_assembly,
                                                          desired_annotation,
                                                          standards_version):
            yield failure
        return
    if value['assay_term_name'] == 'ChIP-seq':
        optimal_idr_peaks = scanFilesForOutputType(value['original_files'],
                                                   'optimal idr thresholded peaks')
        for failure in check_experiment_chip_seq_standards(value,
                                                           fastq_files,
                                                           alignment_files,
                                                           optimal_idr_peaks,
                                                           standards_version):
            yield failure
        return
    if standards_version == 'ENC3' and \
            value['assay_term_name'] == 'whole-genome shotgun bisulfite sequencing':
        cpg_quantifications = scanFilesForOutputType(value['original_files'],
                                                     'methylation state at CpG')

        for failure in check_experiment_wgbs_encode3_standards(value,
                                                               alignment_files,
                                                               organism_name,
                                                               fastq_files,
                                                               cpg_quantifications,
                                                               desired_assembly):
            yield failure
        return


@audit_checker('Experiment', frame=['original_files',
                                    'award',
                                    'target',
                                    'replicates',
                                    'replicates.library',
                                    'replicates.library.spikeins_used',
                                    'replicates.library.spikeins_used.files',
                                    'replicates.library.biosample',
                                    'replicates.library.biosample.organism',
                                    'original_files.quality_metrics',
                                    'original_files.quality_metrics.quality_metric_of',
                                    'original_files.quality_metrics.quality_metric_of.replicate',
                                    'original_files.derived_from',
                                    'original_files.step_run',
                                    'original_files.analysis_step_version',
                                    'original_files.analysis_step_version.software_versions',
                                    'original_files.analysis_step_version.software_versions.software',
                                    'original_files.analysis_step_version.analysis_step',
                                    'original_files.analysis_step_version.analysis_step.pipelines'],
               condition=rfa('modERN'))
def audit_modERN_experiment_standards_dispatcher(value, system):
    '''
    Dispatcher function that will redirect to other functions that would
    deal with specific assay types standards. This version is for the modERN project
    '''

    if value['status'] in ['revoked', 'deleted', 'replaced']:
        return
    if 'assay_term_name' not in value or value['assay_term_name'] not in ['ChIP-seq']:
        return
    if 'original_files' not in value or len(value['original_files']) == 0:
        return
    if 'replicates' not in value:
        return

    alignment_files = scan_files_for_file_format_output_type(value['original_files'],
                                                             'bam', 'alignments')

    fastq_files = scan_files_for_file_format_output_type(value['original_files'],
                                                         'fastq', 'reads')

    if value['assay_term_name'] == 'ChIP-seq':
        optimal_idr_peaks = scanFilesForOutputType(value['original_files'],
                                                   'optimal idr thresholded peaks')
        for failure in check_experiment_chip_seq_standards(value,
                                                           fastq_files,
                                                           alignment_files,
                                                           optimal_idr_peaks,
                                                           'modERN'):
                yield failure


def check_experiment_dnase_seq_standards(experiment,
                                         fastq_files,
                                         alignment_files,
                                         hotspots_files,
                                         signal_files,
                                         desired_assembly,
                                         desired_annotation,
                                         link_to_standards):
    pipeline_title = scanFilesForPipelineTitle_not_chipseq(
        alignment_files,
        ['GRCh38', 'mm10'],
        ['DNase-HS pipeline (paired-end)',
         'DNase-HS pipeline (single-end)'])
    if pipeline_title is False:
        return
    for f in fastq_files:
        for failure in check_file_read_length_rna(f, 36,
                                                  pipeline_title,
                                                  link_to_standards):
            yield failure

    pipelines = get_pipeline_objects(alignment_files)
    if pipelines is not None and len(pipelines) > 0:
        samtools_flagstat_metrics = get_metrics(alignment_files,
                                                'SamtoolsFlagstatsQualityMetric',
                                                desired_assembly)
        if samtools_flagstat_metrics is not None and \
                len(samtools_flagstat_metrics) > 0:
            for metric in samtools_flagstat_metrics:
                if 'mapped' in metric and 'quality_metric_of' in metric:
                    alignment_file = metric['quality_metric_of'][0]
                    suffix = 'According to ENCODE standards, conventional ' + \
                             'DNase-seq profile requires a minimum of 20 million uniquely mapped ' + \
                             'reads to generate a reliable ' + \
                             'SPOT (Signal Portion of Tags) score. ' + \
                             'The recommended value is > 50 million. For deep, foot-printing depth ' + \
                             'DNase-seq 150-200 million uniquely mapped reads are ' + \
                             'recommended. (See {} )'.format(
                                 link_to_standards)
                    if 'assembly' in alignment_file:
                        detail = 'Alignment file {} '.format(alignment_file['@id']) + \
                                 'produced by {} '.format(pipelines[0]['title']) + \
                                 '( {} ) '.format(pipelines[0]['@id']) + \
                                 'for {} assembly has {} '.format(
                                     alignment_file['assembly'],
                                     metric['mapped']) + \
                                 'mapped reads. ' + suffix
                    else:
                        detail = 'Alignment file {} '.format(alignment_file['@id']) + \
                                 'produced by {} '.format(pipelines[0]['title']) + \
                                 '( {} ) '.format(pipelines[0]['@id']) + \
                                 'has {} '.format(
                                     metric['mapped']) + \
                                 'mapped reads. ' + suffix
                    if 20000000 <= metric['mapped'] < 50000000:
                        yield AuditFailure('insufficient read depth', detail, level='WARNING')
                    elif metric['mapped'] < 20000000:
                        yield AuditFailure('extremely low read depth', detail, level='ERROR')
        elif alignment_files is not None and len(alignment_files) > 0 and \
                (samtools_flagstat_metrics is None or
                    len(samtools_flagstat_metrics) == 0):
            files_list = []
            for f in alignment_files:
                files_list.append(f['@id'])
            detail = 'Alignment files ( {} ) '.format(', '.join(files_list)) + \
                     'produced by {} '.format(pipelines[0]['title']) + \
                     '( {} ) '.format(pipelines[0]['@id']) + \
                     'lack read depth information.'
            yield AuditFailure('missing read depth', detail, level='WARNING')

        hotspot_quality_metrics = get_metrics(hotspots_files,
                                              'HotspotQualityMetric',
                                              desired_assembly)
        if hotspot_quality_metrics is not None and \
           len(hotspot_quality_metrics) > 0:
            for metric in hotspot_quality_metrics:
                if "SPOT score" in metric:
                    file_names = []
                    for f in metric['quality_metric_of']:
                        file_names.append(f['@id'])
                    file_names_string = str(file_names).replace('\'', ' ')

                    detail = "Signal Portion of Tags (SPOT) is a measure of enrichment, " + \
                             "analogous to the commonly used fraction of reads in peaks metric. " + \
                             "ENCODE processed hotspots files {} ".format(file_names_string) + \
                             "produced by {} ".format(pipelines[0]['title']) + \
                             "( {} ) ".format(pipelines[0]['@id']) + \
                             "have a SPOT score of {0:.2f}. ".format(metric["SPOT score"]) + \
                             "According to ENCODE standards, " + \
                             "SPOT score of 0.4 or higher is considered a product of high quality " + \
                             "data. " + \
                             "Any sample with a SPOT score <0.3 should be targeted for replacement " + \
                             "with a higher quality sample, and a " + \
                             "SPOT score of 0.25 is considered minimally acceptable " + \
                             "for rare and hard to find primary tissues. (See {} )".format(
                                 link_to_standards)
                    if 0.3 <= metric["SPOT score"] < 0.4:
                        yield AuditFailure('low spot score', detail, level='WARNING')
                    elif 0.25 <= metric["SPOT score"] < 0.3:
                        yield AuditFailure('insufficient spot score', detail, level='NOT_COMPLIANT')
                    elif metric["SPOT score"] < 0.25:
                        yield AuditFailure('extremely low spot score', detail, level='ERROR')

        if 'replication_type' not in experiment or experiment['replication_type'] == 'unreplicated':
            return

        signal_quality_metrics = get_metrics(signal_files,
                                             'CorrelationQualityMetric',
                                             desired_assembly)
        if signal_quality_metrics is not None and \
           len(signal_quality_metrics) > 0:
            threshold = 0.9
            if experiment['replication_type'] == 'anisogenic':
                threshold = 0.85
            for metric in signal_quality_metrics:
                if 'Pearson correlation' in metric:
                    file_names = []
                    for f in metric['quality_metric_of']:
                        file_names.append(f['@id'])
                    file_names_string = str(file_names).replace('\'', ' ')

                    detail = 'Replicate concordance in DNase-seq expriments is measured by ' + \
                        'calculating the Pearson correlation between signal quantification ' + \
                        'of the replicates. ' + \
                        'ENCODE processed signal files {} '.format(file_names_string) + \
                        'produced by {} '.format(pipelines[0]['title']) + \
                        '( {} ) '.format(pipelines[0]['@id']) + \
                        'have a Pearson correlation of {0:.2f}. '.format(metric['Pearson correlation']) + \
                        'According to ENCODE standards, in an {} '.format(experiment['replication_type']) + \
                        'assay a Pearson correlation value > {} '.format(threshold) + \
                        'is recommended. (See {} )'.format(
                            link_to_standards)

                    if metric['Pearson correlation'] < threshold:
                        yield AuditFailure('insufficient replicate concordance',
                                           detail, level='NOT_COMPLIANT')


def check_experiment_rna_seq_standards(value,
                                       fastq_files,
                                       alignment_files,
                                       gene_quantifications,
                                       desired_assembly,
                                       desired_annotation,
                                       standards_version):

    pipeline_title = scanFilesForPipelineTitle_not_chipseq(
        alignment_files,
        ['GRCh38', 'mm10'],
        ['RNA-seq of long RNAs (paired-end, stranded)',
         'RNA-seq of long RNAs (single-end, unstranded)',
         'Small RNA-seq single-end pipeline',
         'RAMPAGE (paired-end, stranded)'])
    if pipeline_title is False:
        return

    standards_links = {
        'RNA-seq of long RNAs (paired-end, stranded)': ' /data-standards/rna-seq/long-rnas/ ',
        'RNA-seq of long RNAs (single-end, unstranded)': ' /data-standards/rna-seq/long-rnas/ ',
        'Small RNA-seq single-end pipeline': ' /data-standards/rna-seq/small-rnas/ ',
        'RAMPAGE (paired-end, stranded)': ' /data-standards/rampage/  '
    }

    for f in fastq_files:
        for failure in check_file_read_length_rna(f, 50,
                                                  pipeline_title,
                                                  standards_links[pipeline_title]):
            yield failure
        for failure in check_file_platform(f, ['OBI:0002024', 'OBI:0000696']):
            yield failure

    if pipeline_title in ['RNA-seq of long RNAs (paired-end, stranded)',
                          'RNA-seq of long RNAs (single-end, unstranded)',
                          'Small RNA-seq single-end pipeline',
                          'RAMPAGE (paired-end, stranded)']:
        star_metrics = get_metrics(alignment_files,
                                   'StarQualityMetric',
                                   desired_assembly)

        if len(star_metrics) < 1:
            detail = 'ENCODE experiment {} '.format(value['@id']) + \
                     'of {} assay'.format(value['assay_term_name']) + \
                     ', processed by {} pipeline '.format(pipeline_title) + \
                     ' has no read depth containig quality metric associated with it.'
            yield AuditFailure('missing read depth', detail, level='INTERNAL_ACTION')

    alignment_files = get_non_tophat_alignment_files(alignment_files)

    if pipeline_title in ['RAMPAGE (paired-end, stranded)']:
        upper_limit = 20000000
        medium_limit = 10000000
        lower_limit = 1000000
        for failure in check_experiment_cage_rampage_standards(value,
                                                               fastq_files,
                                                               alignment_files,
                                                               pipeline_title,
                                                               gene_quantifications,
                                                               desired_assembly,
                                                               desired_annotation,
                                                               upper_limit,
                                                               medium_limit,
                                                               lower_limit,
                                                               standards_version,
                                                               standards_links[pipeline_title]):
            yield failure
    elif pipeline_title in ['Small RNA-seq single-end pipeline']:
        upper_limit = 30000000
        medium_limit = 20000000
        lower_limit = 1000000
        for failure in check_experiment_small_rna_standards(value,
                                                            fastq_files,
                                                            alignment_files,
                                                            pipeline_title,
                                                            gene_quantifications,
                                                            desired_assembly,
                                                            desired_annotation,
                                                            upper_limit,
                                                            medium_limit,
                                                            lower_limit,
                                                            standards_links[pipeline_title]):
            yield failure

    elif pipeline_title in ['RNA-seq of long RNAs (paired-end, stranded)',
                            'RNA-seq of long RNAs (single-end, unstranded)']:
        upper_limit = 30000000
        medium_limit = 20000000
        lower_limit = 1000000
        for failure in check_experiment_long_rna_standards(value,
                                                           fastq_files,
                                                           alignment_files,
                                                           pipeline_title,
                                                           gene_quantifications,
                                                           desired_assembly,
                                                           desired_annotation,
                                                           upper_limit,
                                                           medium_limit,
                                                           lower_limit,
                                                           standards_links[pipeline_title]):
            yield failure

    return


def check_experiment_wgbs_encode3_standards(experiment,
                                            alignment_files,
                                            organism_name,
                                            fastq_files,
                                            cpg_quantifications,
                                            desired_assembly):
    if fastq_files == []:
        return

    for failure in check_wgbs_read_lengths(fastq_files, organism_name, 130, 100):
        yield failure

    read_lengths = get_read_lengths_wgbs(fastq_files)

    pipeline_title = scanFilesForPipelineTitle_not_chipseq(alignment_files,
                                                           ['GRCh38', 'mm10'],
                                                           ['WGBS single-end pipeline - version 2',
                                                            'WGBS single-end pipeline',
                                                            'WGBS paired-end pipeline'])

    if pipeline_title is False:
        return

    if 'replication_type' not in experiment or experiment['replication_type'] == 'unreplicated':
        return

    bismark_metrics = get_metrics(cpg_quantifications, 'BismarkQualityMetric', desired_assembly)
    cpg_metrics = get_metrics(cpg_quantifications, 'CpgCorrelationQualityMetric', desired_assembly)

    samtools_metrics = get_metrics(cpg_quantifications,
                                   'SamtoolsFlagstatsQualityMetric',
                                   desired_assembly)

    for failure in check_wgbs_coverage(samtools_metrics,
                                       pipeline_title,
                                       min(read_lengths),
                                       organism_name,
                                       get_pipeline_objects(alignment_files)):
        yield failure

    for failure in check_wgbs_pearson(cpg_metrics, 0.8, pipeline_title):
        yield failure

    for failure in check_wgbs_lambda(bismark_metrics, 1, pipeline_title):
        yield failure

    return


def get_read_lengths_wgbs(fastq_files):
    list_of_lengths = []
    for f in fastq_files:
        if 'read_length' in f:
            list_of_lengths.append(f['read_length'])
    return list_of_lengths


def check_wgbs_read_lengths(fastq_files,
                            organism_name,
                            human_threshold,
                            mouse_threshold):
    for f in fastq_files:
        if 'read_length' in f:
            l = f['read_length']
            if organism_name == 'mouse' and l < 100:
                detail = 'Fastq file {} '.format(f['@id']) + \
                         'has read length of {}bp, while '.format(l) + \
                         'the recommended read length for {} '.format(organism_name) + \
                         'data is > 100bp.'
                yield AuditFailure('insufficient read length',
                                   detail, level='NOT_COMPLIANT')
            elif organism_name == 'human' and l < 100:
                detail = 'Fastq file {} '.format(f['@id']) + \
                         'has read length of {}bp, while '.format(l) + \
                         'the recommended read length for {} '.format(organism_name) + \
                         'data is > 100bp.'
                yield AuditFailure('insufficient read length',
                                   detail, level='NOT_COMPLIANT')


def get_non_tophat_alignment_files(files_list):
    list_to_return = []
    for f in files_list:
        tophat_flag = False
        if 'analysis_step_version' in f and \
           'software_versions' in f['analysis_step_version']:
            for soft_version in f['analysis_step_version']['software_versions']:
                #  removing TopHat files
                if 'software' in soft_version and \
                   soft_version['software']['uuid'] == '7868f960-50ac-11e4-916c-0800200c9a66':
                    tophat_flag = True
        if tophat_flag is False and \
           f['lab'] == '/labs/encode-processing-pipeline/':
            list_to_return.append(f)
    return list_to_return


def get_metrics(files_list, metric_type, desired_assembly=None, desired_annotation=None):
    metrics_dict = {}
    for f in files_list:
        if (desired_assembly is None or ('assembly' in f and
                                         f['assembly'] == desired_assembly)) and \
            (desired_annotation is None or ('genome_annotation' in f and
                                            f['genome_annotation'] == desired_annotation)):
            if 'quality_metrics' in f and len(f['quality_metrics']) > 0:
                for qm in f['quality_metrics']:
                    if metric_type in qm['@type']:
                        if qm['uuid'] not in metrics_dict:
                            metrics_dict[qm['uuid']] = qm
    metrics = []
    for k in metrics_dict:
        metrics.append(metrics_dict[k])
    return metrics


def check_experiment_chip_seq_standards(experiment,
                                        fastq_files,
                                        alignment_files,
                                        idr_peaks_files,
                                        standards_version):

    upper_limit_read_length = 50
    medium_limit_read_length = 36
    lower_limit_read_length = 26
    for f in fastq_files:
        for failure in check_file_read_length_chip(f,
                                                   upper_limit_read_length,
                                                   medium_limit_read_length,
                                                   lower_limit_read_length):
            yield failure

    pipeline_title = scanFilesForPipelineTitle_yes_chipseq(
        alignment_files,
        ['Histone ChIP-seq', 'Transcription factor ChIP-seq pipeline (modERN)']
    )
    if pipeline_title is False:
        return

    for f in alignment_files:
        target = get_target(experiment)
        if target is False:
            return

        read_depth = get_file_read_depth_from_alignment(f, target, 'ChIP-seq')

        for failure in check_file_chip_seq_read_depth(f, target, read_depth, standards_version):
            yield failure
        for failure in check_file_chip_seq_library_complexity(f):
            yield failure

    if 'replication_type' not in experiment or experiment['replication_type'] == 'unreplicated':
        return

    idr_metrics = get_metrics(idr_peaks_files, 'IDRQualityMetric')

    for failure in check_idr(idr_metrics, 2, 2, pipeline_title):
        yield failure


def check_experiment_long_rna_standards(experiment,
                                        fastq_files,
                                        alignment_files,
                                        pipeline_title,
                                        gene_quantifications,
                                        desired_assembly,
                                        desired_annotation,
                                        upper_limit_read_depth,
                                        medium_limit_read_depth,
                                        lower_limit_read_depth,
                                        standards_link):

    for failure in check_experiment_ERCC_spikeins(experiment, pipeline_title):
        yield failure

    pipelines = get_pipeline_objects(alignment_files)
    if pipelines is not None and len(pipelines) > 0:
        for f in alignment_files:

            if 'assembly' in f and f['assembly'] == desired_assembly:

                read_depth = get_file_read_depth_from_alignment(f,
                                                                get_target(experiment),
                                                                'long RNA')

                if experiment['assay_term_name'] in ['shRNA knockdown followed by RNA-seq',
                                                     'siRNA knockdown followed by RNA-seq',
                                                     'CRISPR genome editing followed by RNA-seq']:
                    for failure in check_file_read_depth(f, read_depth, 10000000, 10000000, 1000000,
                                                         experiment['assay_term_name'],
                                                         pipeline_title,
                                                         pipelines[0],
                                                         standards_link):
                        yield failure
                elif experiment['assay_term_name'] in ['single cell isolation followed by RNA-seq']:
                    for failure in check_file_read_depth(f, read_depth, 5000000, 5000000, 500000,
                                                         experiment['assay_term_name'],
                                                         pipeline_title,
                                                         pipelines[0],
                                                         standards_link):
                        yield failure
                else:
                    for failure in check_file_read_depth(f, read_depth,
                                                         upper_limit_read_depth,
                                                         medium_limit_read_depth,
                                                         lower_limit_read_depth,
                                                         experiment['assay_term_name'],
                                                         pipeline_title,
                                                         pipelines[0],
                                                         standards_link):
                        yield failure

    if 'replication_type' not in experiment:
        return

    mad_metrics = get_metrics(gene_quantifications,
                              'MadQualityMetric',
                              desired_assembly,
                              desired_annotation)

    if experiment['assay_term_name'] != 'single cell isolation followed by RNA-seq':
        for failure in check_spearman(mad_metrics, experiment['replication_type'],
                                      0.9, 0.8, pipeline_title):
            yield failure
    # for failure in check_mad(mad_metrics, experiment['replication_type'],
    #                         0.2, pipeline_title):
    #    yield failure

    return


def check_experiment_small_rna_standards(experiment,
                                         fastq_files,
                                         alignment_files,
                                         pipeline_title,
                                         gene_quantifications,
                                         desired_assembly,
                                         desired_annotation,
                                         upper_limit_read_depth,
                                         medium_limit_read_depth,
                                         lower_limit_read_depth,
                                         standards_link):
    for f in fastq_files:
        if 'run_type' in f and f['run_type'] != 'single-ended':
            detail = 'Small RNA-seq experiment {} '.format(experiment['@id']) + \
                     'contains a file {} '.format(f['@id']) + \
                     'that is not single-ended.'
            yield AuditFailure('non-standard run type', detail, level='WARNING')
    pipelines = get_pipeline_objects(alignment_files)
    if pipelines is not None and len(pipelines) > 0:
        for f in alignment_files:
            if 'assembly' in f and f['assembly'] == desired_assembly:
                read_depth = get_file_read_depth_from_alignment(f,
                                                                get_target(experiment),
                                                                'small RNA')

                for failure in check_file_read_depth(f, read_depth,
                                                     upper_limit_read_depth,
                                                     medium_limit_read_depth,
                                                     lower_limit_read_depth,
                                                     experiment['assay_term_name'],
                                                     pipeline_title,
                                                     pipelines[0],
                                                     standards_link):
                    yield failure

    if 'replication_type' not in experiment:
        return

    mad_metrics = get_metrics(gene_quantifications,
                              'MadQualityMetric',
                              desired_assembly,
                              desired_annotation)

    for failure in check_spearman(mad_metrics, experiment['replication_type'],
                                  0.9, 0.8, 'Small RNA-seq single-end pipeline'):
        yield failure
    return


def check_experiment_cage_rampage_standards(experiment,
                                            fastq_files,
                                            alignment_files,
                                            pipeline_title,
                                            gene_quantifications,
                                            desired_assembly,
                                            desired_annotation,
                                            upper_limit_read_depth,
                                            middle_limit_read_depth,
                                            lower_limit_read_depth,
                                            standards_version,
                                            standards_link):

    if standards_version == 'ENC3':
        for f in fastq_files:
            if 'run_type' in f and f['run_type'] != 'paired-ended':
                detail = '{} experiment {} '.format(
                    experiment['assay_term_name'],
                    experiment['@id']) + \
                    'contains a file {} '.format(f['@id']) + \
                    'that is not paired-ended.'
                yield AuditFailure('non-standard run type', detail, level='WARNING')
    pipelines = get_pipeline_objects(alignment_files)
    if pipelines is not None and len(pipelines) > 0:
        for f in alignment_files:
            if 'assembly' in f and f['assembly'] == desired_assembly:

                read_depth = get_file_read_depth_from_alignment(f,
                                                                get_target(experiment),
                                                                experiment['assay_term_name'])
                for failure in check_file_read_depth(f, read_depth,
                                                     upper_limit_read_depth,
                                                     middle_limit_read_depth,
                                                     lower_limit_read_depth,                            
                                                     experiment['assay_term_name'],
                                                     pipeline_title,
                                                     pipelines[0],
                                                     standards_link):
                    yield failure

    if 'replication_type' not in experiment:
        return

    mad_metrics = get_metrics(gene_quantifications,
                              'MadQualityMetric',
                              desired_assembly,
                              desired_annotation)

    for failure in check_spearman(mad_metrics, experiment['replication_type'],
                                  0.9, 0.8, 'RAMPAGE (paired-end, stranded)'):
        yield failure
    return


def check_idr(metrics, rescue, self_consistency, pipeline):
    for m in metrics:
        if 'rescue_ratio' in m and 'self_consistency_ratio' in m:
            rescue_r = m['rescue_ratio']
            self_r = m['self_consistency_ratio']
            if rescue_r > rescue and self_r > self_consistency:
                file_names = []
                for f in m['quality_metric_of']:
                    file_names.append(f['@id'])
                file_names_string = str(file_names).replace('\'', ' ')
                detail = 'Replicate concordance in ChIP-seq expriments is measured by ' + \
                         'calculating IDR values (Irreproducible Discovery Rate). ' + \
                         'ENCODE processed IDR thresholded peaks files {} '.format(file_names_string) + \
                         'have a rescue ratio of {0:.2f} and a '.format(rescue_r) + \
                         'self consistency ratio of {0:.2f}. '.format(self_r) + \
                         'According to ENCODE standards, having both rescue ratio ' + \
                         'and self consistency ratio values < 2 is recommended, but ' + \
                         'having only one of the ratio values < 2 is acceptable.'
                yield AuditFailure('insufficient replicate concordance', detail,
                                   level='NOT_COMPLIANT')
            elif (rescue_r <= rescue and self_r > self_consistency) or \
                 (rescue_r > rescue and self_r <= self_consistency):
                    file_names = []
                    for f in m['quality_metric_of']:
                        file_names.append(f['@id'])
                    file_names_string = str(file_names).replace('\'', ' ')
                    detail = 'Replicate concordance in ChIP-seq expriments is measured by ' + \
                             'calculating IDR values (Irreproducible Discovery Rate). ' + \
                             'ENCODE processed IDR thresholded peaks files {} '.format(file_names_string) + \
                             'have a rescue ratio of {0:.2f} and a '.format(rescue_r) + \
                             'self consistency ratio of {0:.2f}. '.format(self_r) + \
                             'According to ENCODE standards, having both rescue ratio ' + \
                             'and self consistency ratio values < 2 is recommended, but ' + \
                             'having only one of the ratio values < 2 is acceptable.'
                    yield AuditFailure('borderline replicate concordance', detail,
                                       level='WARNING')


def check_mad(metrics, replication_type, mad_threshold, pipeline):
    if replication_type == 'anisogenic':
        experiment_replication_type = 'anisogenic'
    elif replication_type == 'isogenic':
        experiment_replication_type = 'isogenic'
    else:
        return

    mad_value = None
    for m in metrics:
        if 'MAD of log ratios' in m:
            mad_value = m['MAD of log ratios']
            if mad_value > 0.2:
                file_names = []
                for f in m['quality_metric_of']:
                    file_names.append(f['@id'])
                detail = 'ENCODE processed gene quantification files {} '.format(file_names) + \
                         'has Median-Average-Deviation (MAD) ' + \
                         'of replicate log ratios from quantification ' + \
                         'value of {}.'.format(mad_value) + \
                         ' For gene quantification files from an {}'.format(experiment_replication_type) + \
                         ' assay in the {} '.format(pipeline) + \
                         'pipeline, a value <0.2 is recommended, but a value between ' + \
                         '0.2 and 0.5 is acceptable.'
                if experiment_replication_type == 'isogenic':
                    if mad_value < 0.5:
                        yield AuditFailure('low replicate concordance', detail,
                                           level='WARNING')
                    else:
                        yield AuditFailure('insufficient replicate concordance', detail,
                                           level='NOT_COMPLIANT')
                elif experiment_replication_type == 'anisogenic' and mad_value > 0.5:
                    detail = 'ENCODE processed gene quantification files {} '.format(file_names) + \
                             'has Median-Average-Deviation (MAD) ' + \
                             'of replicate log ratios from quantification ' + \
                             'value of {}.'.format(mad_value) + \
                             ' For gene quantification files from an {}'.format(experiment_replication_type) + \
                             ' assay in the {} '.format(pipeline) + \
                             'pipeline, a value <0.5 is recommended.'
                    yield AuditFailure('low replicate concordance', detail,
                                       level='WARNING')


def check_experiment_ERCC_spikeins(experiment, pipeline):
    '''
    The assumption in this functon is that the regular audit will catch anything without spikeins.
    This audit is checking specifically for presence of ERCC spike-in in long-RNA pipeline
    experiments
    '''
    for rep in experiment['replicates']:
        lib = rep.get('library')
        if lib is None:
            continue

        size_range = lib.get('size_range')
        if size_range != '>200':
            continue

        ercc_flag = False
        some_spikein_present = False
        spikes = lib.get('spikeins_used')

        if (spikes is not None) and (len(spikes) > 0):
            for s in spikes:
                some_spikein_present = True
                if 'files' in s:
                    for f in s['files']:
                        if (('ENCFF001RTP' == f['accession']) or
                           ('ENCFF001RTO' == f['accession'] and
                           experiment['assay_term_name'] ==
                           'single cell isolation followed by RNA-seq')):
                            ercc_flag = True

        if ercc_flag is False:
            if some_spikein_present is True:
                detail = 'Library {} '.format(lib['@id']) + \
                         'in experiment {} '.format(experiment['@id']) + \
                         'that was processed by {} pipeline '.format(pipeline) + \
                         'requires standard ERCC spike-in to be used in its preparation.'
                yield AuditFailure('missing spikeins',
                                   detail, level='WARNING')
            else:
                detail = 'Library {} '.format(lib['@id']) + \
                         'in experiment {} '.format(experiment['@id']) + \
                         'that was processed by {} pipeline '.format(pipeline) + \
                         'requires ERCC spike-in to be used in its preparation.'
                yield AuditFailure('missing spikeins',
                                   detail, level='NOT_COMPLIANT')


def get_target(experiment):
    if 'target' in experiment:
        return experiment['target']
    return False


def check_spearman(metrics, replication_type, isogenic_threshold,
                   anisogenic_threshold, pipeline):

    if replication_type == 'anisogenic':
        threshold = anisogenic_threshold
    elif replication_type == 'isogenic':
        threshold = isogenic_threshold
    else:
        return

    for m in metrics:
        if 'Spearman correlation' in m:
            spearman_correlation = m['Spearman correlation']
            if spearman_correlation < threshold:
                file_names = []
                for f in m['quality_metric_of']:
                    file_names.append(f['@id'])
                file_names_string = str(file_names).replace('\'', ' ')
                detail = 'Replicate concordance in RNA-seq expriments is measured by ' + \
                         'calculating the Spearman correlation between gene quantifications ' + \
                         'of the replicates. ' + \
                         'ENCODE processed gene quantification files {} '.format(file_names_string) + \
                         'have a Spearman correlation of {0:.2f}. '.format(spearman_correlation) + \
                         'According to ENCODE standards, in an {} '.format(replication_type) + \
                         'assay analyzed using the {} pipeline, '.format(pipeline) + \
                         'a Spearman correlation value > {} '.format(threshold) + \
                         'is recommended.'
                yield AuditFailure('low replicate concordance', detail,
                                   level='WARNING')


def get_file_read_depth_from_alignment(alignment_file, target, assay_name):

    if alignment_file['output_type'] in ['transcriptome alignments',
                                         'unfiltered alignments']:
        return False

    if alignment_file['lab'] not in ['/labs/encode-processing-pipeline/', '/labs/kevin-white/']:
        return False

    quality_metrics = alignment_file.get('quality_metrics')

    if (quality_metrics is None) or (quality_metrics == []):
        return False

    if assay_name in ['RAMPAGE', 'CAGE',
                      'small RNA',
                      'long RNA']:
        for metric in quality_metrics:
            if 'Uniquely mapped reads number' in metric and \
               'Number of reads mapped to multiple loci' in metric:
                unique = metric['Uniquely mapped reads number']
                multi = metric['Number of reads mapped to multiple loci']
                return (unique + multi)

    elif assay_name in ['ChIP-seq']:

        derived_from_files = alignment_file.get('derived_from')

        if (derived_from_files is None) or (derived_from_files == []):
            return False

        if target is not False and \
           'name' in target and target['name'] in ['H3K9me3-human', 'H3K9me3-mouse']:
            # exception (mapped)
            for metric in quality_metrics:
                if 'processing_stage' in metric and \
                    metric['processing_stage'] == 'unfiltered' and \
                        'mapped' in metric:
                    if "read1" in metric and "read2" in metric:
                        return int(metric['mapped']/2)
                    else:
                        return int(metric['mapped'])
        else:
            # not exception (useful fragments)
            for metric in quality_metrics:
                if ('total' in metric) and \
                   (('processing_stage' in metric and metric['processing_stage'] == 'filtered') or
                   ('processing_stage' not in metric)):
                    if "read1" in metric and "read2" in metric:
                        return int(metric['total']/2)
                    else:
                        return int(metric['total'])
    return False


def check_file_chip_seq_library_complexity(alignment_file):
    '''
    An alignment file from the ENCODE ChIP-seq processing pipeline
    should have minimal library complexity in accordance with the criteria
    '''
    if alignment_file['output_type'] == 'transcriptome alignments':
        return

    if alignment_file['lab'] not in ['/labs/encode-processing-pipeline/', '/labs/kevin-white/']:
        return

    if ('quality_metrics' not in alignment_file) or (alignment_file.get('quality_metrics') == []):
        return

    nrf_detail = 'NRF (Non Redundant Fraction) is equal to the result of the ' + \
                 'division of the number of reads after duplicates removal by ' + \
                 'the total number of reads. ' + \
                 'An NRF value in the range 0 - 0.5 is poor complexity, ' + \
                 '0.5 - 0.8 is moderate complexity, ' + \
                 'and > 0.8 high complexity. NRF value > 0.8 is recommended, ' + \
                 'but > 0.5 is acceptable. '

    pbc1_detail = 'PBC1 (PCR Bottlenecking Coefficient 1) is equal to the result of the division of ' + \
                  'the number of genomic locations where exactly one read maps uniquely by ' + \
                  'the number of distinct genomic locations to which some read maps uniquely. ' + \
                  'A PBC1 value in the range 0 - 0.5 is severe bottlenecking, 0.5 - 0.8 ' + \
                  'is moderate bottlenecking, 0.8 - 0.9 is mild bottlenecking, and > 0.9 ' + \
                  'is no bottlenecking. PBC1 value > 0.9 is recommended, but > 0.8 is ' + \
                  'acceptable. '

    pbc2_detail = 'PBC2 (PCR Bottlenecking Coefficient 2) is equal to the result of the division of ' + \
                  'the number of genomic locations where only one read maps uniquely by ' + \
                  'the number of genomic locations where 2 reads map uniquely. ' + \
                  'A PBC2 value in the range 0 - 1 is severe bottlenecking, 1 - 3 ' + \
                  'is moderate bottlenecking, 3 - 10 is mild bottlenecking, > 10 is ' + \
                  'no bottlenecking. PBC2 value > 10 is recommended, but > 3 is acceptable. '

    quality_metrics = alignment_file.get('quality_metrics')
    for metric in quality_metrics:

        if 'NRF' in metric:
            NRF_value = float(metric['NRF'])
            if NRF_value < 0.5:
                detail = nrf_detail + 'ENCODE processed alignment file {} '.format(
                    alignment_file['@id']) + \
                    'was generated from a library with ' + \
                    'NRF value of {0:.2f}.'.format(NRF_value)
                yield AuditFailure('poor library complexity', detail,
                                   level='NOT_COMPLIANT')
            elif NRF_value >= 0.5 and NRF_value < 0.8:
                detail = nrf_detail + 'ENCODE Processed alignment file {} '.format(
                    alignment_file['@id']) + \
                    'was generated from a library with NRF value of {0:.2f}.'.format(NRF_value)
                yield AuditFailure('moderate library complexity', detail,
                                   level='WARNING')
        if 'PBC1' in metric:
            PBC1_value = float(metric['PBC1'])
            if PBC1_value < 0.5:
                detail = pbc1_detail + 'ENCODE processed alignment file {} '.format(
                    alignment_file['@id']) + \
                    'was generated from a library with PBC1 value of {0:.2f}.'.format(PBC1_value)
                yield AuditFailure('severe bottlenecking', detail,
                                   level='NOT_COMPLIANT')
            elif PBC1_value >= 0.5 and PBC1_value < 0.9:
                detail = pbc1_detail + 'ENCODE processed alignment file {} '.format(
                    alignment_file['@id']) + \
                    'was generated from a library with PBC1 value of {0:.2f}.'.format(PBC1_value)
                yield AuditFailure('mild to moderate bottlenecking', detail,
                                   level='WARNING')
        if 'PBC2' in metric:
            PBC2_raw_value = metric['PBC2']
            if PBC2_raw_value == 'Infinity':
                PBC2_value = float('inf')
            else:
                PBC2_value = float(metric['PBC2'])
            if PBC2_value < 1:
                detail = pbc2_detail + 'ENCODE processed alignment file {} '.format(
                    alignment_file['@id']) + \
                    'was generated from a library with PBC2 value of {0:.2f}.'.format(PBC2_value)
                yield AuditFailure('severe bottlenecking', detail,
                                   level='NOT_COMPLIANT')
            elif PBC2_value >= 1 and PBC2_value < 10:
                detail = pbc2_detail + 'ENCODE processed alignment file {} '.format(
                    alignment_file['@id']) + \
                    'was generated from a library with PBC2 value of {0:.2f}.'.format(PBC2_value)
                yield AuditFailure('mild to moderate bottlenecking', detail,
                                   level='WARNING')


def check_wgbs_coverage(samtools_metrics,
                        pipeline_title,
                        read_length,
                        organism,
                        pipeline_objects):
    for m in samtools_metrics:
        if 'mapped' in m:
            bio_rep_num = False
            for f in m['quality_metric_of']:
                if 'replicate' in f and \
                   'biological_replicate_number' in f['replicate']:
                    bio_rep_num = f['replicate']['biological_replicate_number']
                    break
            mapped_reads = m['mapped']
            if organism == 'mouse':
                coverage = float(mapped_reads * read_length)/2800000000.0
            elif organism == 'human':
                coverage = float(mapped_reads * read_length)/3300000000.0

            if coverage < 30:
                if bio_rep_num is not False:
                    detail = 'Biological replicate {} '.format(bio_rep_num) + \
                             'of experiment processed by {} '.format(pipeline_title) + \
                             '( {} ) '.format(pipeline_objects[0]['@id']) + \
                             'has a coverage of {}. '.format(int(coverage)) + \
                             'The minimum ENCODE standard for each replicate in ' + \
                             'a WGBS assay is 30X. (See /data-standards/wgbs/ )'
                    yield AuditFailure('insufficient coverage',
                                       detail,
                                       level='NOT_COMPLIANT')
                else:
                    detail = 'Replicate ' + \
                             'of experiment processed by {} '.format(pipeline_title) + \
                             '( {} ) '.format(pipeline_objects[0]['@id']) + \
                             'has a coverage of {}. '.format(int(coverage)) + \
                             'The minimum ENCODE standard for each replicate in ' + \
                             'a WGBS assay is 30X. (See /data-standards/wgbs/ )'
                    yield AuditFailure('insufficient coverage',
                                       detail,
                                       level='INTERNAL_ACTION')
    return


def check_wgbs_pearson(cpg_metrics, threshold,  pipeline_title):
    for m in cpg_metrics:
        if 'Pearson Correlation Coefficient' in m:
            if m['Pearson Correlation Coefficient'] < threshold:
                detail = 'ENCODE experiment processed by {} '.format(pipeline_title) + \
                         'pipeline has CpG quantification Pearson Correlation Coefficient of ' + \
                         '{}, '.format(m['Pearson Correlation Coefficient']) + \
                         'while a value >={} is required.'.format(threshold)
                yield AuditFailure('insufficient replicate concordance',
                                   detail,
                                   level='NOT_COMPLIANT')


def check_wgbs_lambda(bismark_metrics, threshold, pipeline_title):
    for metric in bismark_metrics:
        lambdaCpG = float(metric['lambda C methylated in CpG context'][:-1])
        lambdaCHG = float(metric['lambda C methylated in CHG context'][:-1])
        lambdaCHH = float(metric['lambda C methylated in CHH context'][:-1])

        if (lambdaCpG > 1 and lambdaCHG > 1 and lambdaCHH > 1) or \
           (((lambdaCpG*0.25) + (lambdaCHG*0.25) + (lambdaCHH*0.5)) > 1):
            detail = 'ENCODE experiment processed by {} '.format(pipeline_title) + \
                     'pipeline has the following %C methylated in different contexts. ' + \
                     'lambda C methylated in CpG context was {}%, '.format(lambdaCpG) + \
                     'lambda C methylated in CHG context was {}%, '.format(lambdaCHG) + \
                     'lambda C methylated in CHH context was {}%. '.format(lambdaCHH) + \
                     'The %C methylated in all contexts should be < 1%.'
            yield AuditFailure('high lambda C methylation ratio', detail,
                               level='WARNING')


def check_file_chip_seq_read_depth(file_to_check,
                                   target,
                                   read_depth,
                                   standards_version):
    # added individual file pipeline validation due to the fact that one experiment may
    # have been mapped using 'Raw mapping' and also 'Histone ChIP-seq' - and there is no need to
    # check read depth on Raw files, while it is required for Histone
    pipeline_title = scanFilesForPipelineTitle_yes_chipseq(
        [file_to_check],
        ['Histone ChIP-seq',
         'Transcription factor ChIP-seq pipeline (modERN)'])
    pipeline_objects = get_pipeline_objects([file_to_check])
    if pipeline_title is False:
        return


    marks = pipelines_with_read_depth['Histone ChIP-seq']
    modERN_cutoff = pipelines_with_read_depth['Transcription factor ChIP-seq pipeline (modERN)']
    if read_depth is False:
        detail = 'ENCODE Processed alignment file {} has no read depth information.'.format(
            file_to_check['@id'])
        yield AuditFailure('missing read depth', detail, level='INTERNAL_ACTION')
        return

    if target is not False and 'name' in target:
        target_name = target['name']
    else:
        return

    if target is not False and 'investigated_as' in target:
        target_investigated_as = target['investigated_as']
    else:
        return

    if target_name in ['Control-human', 'Control-mouse'] and 'control' in target_investigated_as:
        if pipeline_title == 'Transcription factor ChIP-seq pipeline (modERN)':
            if read_depth < modERN_cutoff:
                detail = 'modERN processed alignment file {} has {} '.format(file_to_check['@id'],
                                                                             read_depth) + \
                    'usable fragments. It cannot be used as a control ' + \
                    'in experiments studying transcription factors, which ' + \
                    'require {} usable fragments, according to '.format(modERN_cutoff) + \
                    'the standards defined by the modERN project.'
                yield AuditFailure('insufficient read depth',
                                   detail, level='NOT_COMPLIANT')
        else:
            if read_depth >= marks['narrow'] and read_depth < marks['broad']:
                if 'assembly' in file_to_check:
                    detail = 'Control alignment file {} mapped using {} assembly has {} '.format(
                        file_to_check['@id'],
                        file_to_check['assembly'],
                        read_depth) + \
                        'usable fragments. ' + \
                        'The minimum ENCODE standard for a control of ChIP-seq assays targeting broad ' + \
                        'histone marks ' + \
                        'is 20 million usable fragments, the recommended number of usable ' + \
                        'fragments is > 45 million. (See /data-standards/chip-seq/ )'
                else:
                    detail = 'Control alignment file {} has {} '.format(file_to_check['@id'],
                                                                        read_depth) + \
                        'usable fragments. ' + \
                        'The minimum ENCODE standard for a control of ChIP-seq assays targeting broad ' + \
                        'histone marks ' + \
                        'is 20 million usable fragments, the recommended number of usable ' + \
                        'fragments is > 45 million. (See /data-standards/chip-seq/ )'
                yield AuditFailure('low read depth', detail, level='INTERNAL_ACTION')
            if read_depth < marks['narrow']:
                if 'assembly' in file_to_check:
                    detail = 'Control alignment file {} mapped using {} assembly has {} '.format(
                        file_to_check['@id'],
                        file_to_check['assembly'],
                        read_depth) + \
                        'usable fragments. ' + \
                        'The minimum ENCODE standard for a control of ChIP-seq assays targeting broad ' + \
                        'histone marks ' + \
                        'is 20 million usable fragments, the recommended number of usable ' + \
                        'fragments is > 45 million. ' + \
                        'The minimum for a control of ChIP-seq assays targeting narrow ' + \
                        'histone marks or transcription factors ' + \
                        'is 10 million usable fragments, the recommended number of usable ' + \
                        'fragments is > 20 million. (See /data-standards/chip-seq/ )'
                else:
                    detail = 'Control alignment file {} has {} '.format(file_to_check['@id'],
                                                                        read_depth) + \
                        'usable fragments. ' + \
                        'The minimum ENCODE standard for a control of ChIP-seq assays targeting broad ' + \
                        'histone marks ' + \
                        'is 20 million usable fragments, the recommended number of usable ' + \
                        'fragments is > 45 million. ' + \
                        'The minimum for a control of ChIP-seq assays targeting narrow ' + \
                        'histone marks or transcription factors ' + \
                        'is 10 million usable fragments, the recommended number of usable ' + \
                        'fragments is > 20 million. (See /data-standards/chip-seq/ )'
                if read_depth >= 10000000:
                    yield AuditFailure('low read depth', detail, level='WARNING')
                elif read_depth >= 3000000 and read_depth < 10000000:
                    yield AuditFailure('insufficient read depth',
                                       detail, level='NOT_COMPLIANT')
                else:
                    yield AuditFailure('extremely low read depth',
                                       detail, level='ERROR')
    elif 'broad histone mark' in target_investigated_as and \
         standards_version != 'modERN':  # target_name in broad_peaks_targets:
        pipeline_object = get_pipeline_by_name(pipeline_objects, 'Histone ChIP-seq')
        if pipeline_object:
            if target_name in ['H3K9me3-human', 'H3K9me3-mouse']:
                if read_depth < 45000000:
                    if 'assembly' in file_to_check:
                        detail = 'Alignment file {} '.format(file_to_check['@id']) + \
                            'produced by {} '.format(pipeline_object['title']) + \
                            'pipeline ( {} ) using the {} assembly '.format(
                                pipeline_object['@id'],
                                file_to_check['assembly']) + \
                            'has {} '.format(read_depth) + \
                            'mapped reads. ' + \
                            'The minimum ENCODE standard for each replicate in a ChIP-seq ' + \
                            'experiment targeting {} and investigated as '.format(target_name) + \
                            'a broad histone mark is 40 million mapped reads. ' + \
                            'The recommended value is > 45 million, but > 40 million is ' + \
                            'acceptable. (See /data-standards/chip-seq/ )'
                    else:
                        detail = 'Alignment file {} '.format(file_to_check['@id']) + \
                            'produced by {} '.format(pipeline_object['title']) + \
                            'pipeline ( {} ) '.format(pipeline_object['@id']) + \
                            'has {} '.format(read_depth) + \
                            'mapped reads. ' + \
                            'The minimum ENCODE standard for each replicate in a ChIP-seq ' + \
                            'experiment targeting {} and investigated as '.format(target_name) + \
                            'a broad histone mark is 40 million mapped reads. ' + \
                            'The recommended value is > 45 million, but > 40 million is ' + \
                            'acceptable. (See /data-standards/chip-seq/ )'
                    if read_depth >= 40000000:
                        yield AuditFailure('low read depth',
                                           detail, level='WARNING')
                    elif read_depth >= 5000000 and read_depth < 40000000:
                        yield AuditFailure('insufficient read depth',
                                           detail, level='NOT_COMPLIANT')
                    elif read_depth < 5000000:
                        yield AuditFailure('extremely low read depth',
                                           detail, level='WARNING')
            else:
                if 'assembly' in file_to_check:
                    detail = 'Alignment file {} '.format(file_to_check['@id']) + \
                        'produced by {} '.format(pipeline_object['title']) + \
                        'pipeline ( {} ) using the {} assembly '.format(
                            pipeline_object['@id'],
                            file_to_check['assembly']) + \
                        'has {} '.format(read_depth) + \
                        'usable fragments. ' + \
                        'The minimum ENCODE standard for each replicate in a ChIP-seq ' + \
                        'experiment targeting {} and investigated as '.format(target_name) + \
                        'a broad histone mark is 20 million usable fragments. ' + \
                        'The recommended value is > 45 million, but > 40 million is ' + \
                        'acceptable. (See /data-standards/chip-seq/ )'
                else:
                    detail = 'Alignment file {} '.format(file_to_check['@id']) + \
                        'produced by {} '.format(pipeline_object['title']) + \
                        'pipeline ( {} ) '.format(pipeline_object['@id']) + \
                        'has {} '.format(read_depth) + \
                        'usable fragments. ' + \
                        'The minimum ENCODE standard for each replicate in a ChIP-seq ' + \
                        'experiment targeting {} and investigated as '.format(target_name) + \
                        'a broad histone mark is 20 million usable fragments. ' + \
                        'The recommended value is > 45 million, but > 40 million is ' + \
                        'acceptable. (See /data-standards/chip-seq/ )'

                if read_depth >= 40000000 and read_depth < marks['broad']:
                    yield AuditFailure('low read depth',
                                       detail, level='WARNING')
                elif read_depth < 40000000 and read_depth >= 5000000:
                    yield AuditFailure('insufficient read depth',
                                       detail, level='NOT_COMPLIANT')
                elif read_depth < 5000000:
                    yield AuditFailure('extremely low read depth',
                                       detail, level='ERROR')
    elif 'narrow histone mark' in target_investigated_as and \
            standards_version != 'modERN':
        pipeline_object = get_pipeline_by_name(pipeline_objects, 'Histone ChIP-seq')
        if pipeline_object:
            if 'assembly' in file_to_check:
                detail = 'Alignment file {} '.format(file_to_check['@id']) + \
                    'produced by {} '.format(pipeline_object['title']) + \
                    'pipeline ( {} ) using the {} assembly '.format(
                        pipeline_object['@id'],
                        file_to_check['assembly']) + \
                    'has {} '.format(read_depth) + \
                    'usable fragments. ' + \
                    'The minimum ENCODE standard for each replicate in a ChIP-seq ' + \
                    'experiment targeting {} and investigated as '.format(target_name) + \
                    'a narrow histone mark is 10 million usable fragments. ' + \
                    'The recommended value is > 20 million, but > 10 million is ' + \
                    'acceptable. (See /data-standards/chip-seq/ )'               
            else:
                detail = 'Alignment file {} '.format(file_to_check['@id']) + \
                    'produced by {} '.format(pipeline_object['title']) + \
                    'pipeline ( {} ) '.format(pipeline_object['@id']) + \
                    'has {} '.format(read_depth) + \
                    'usable fragments. ' + \
                    'The minimum ENCODE standard for each replicate in a ChIP-seq ' + \
                    'experiment targeting {} and investigated as '.format(target_name) + \
                    'a narrow histone mark is 10 million usable fragments. ' + \
                    'The recommended value is > 20 million, but > 10 million is ' + \
                    'acceptable. (See /data-standards/chip-seq/ )'
            if read_depth >= 10000000 and read_depth < marks['narrow']:
                yield AuditFailure('low read depth', detail, level='WARNING')
            elif read_depth < 10000000 and read_depth >= 5000000:
                yield AuditFailure('insufficient read depth',
                                   detail, level='NOT_COMPLIANT')
            elif read_depth < 5000000:
                yield AuditFailure('extremely low read depth',
                                   detail, level='ERROR')
    else:
        if pipeline_title == 'Transcription factor ChIP-seq pipeline (modERN)':
            if read_depth < modERN_cutoff:
                detail = 'modERN processed alignment file {} has {} '.format(file_to_check['@id'],
                                                                             read_depth) + \
                    'usable fragments. Replicates for ChIP-seq ' + \
                    'assays and target {} '.format(target_name) + \
                    'investigated as transcription factor require ' + \
                    '{} usable fragments, according to '.format(modERN_cutoff) + \
                    'the standards defined by the modERN project.'
                yield AuditFailure('insufficient read depth',
                                   detail, level='NOT_COMPLIANT')
        else:
            pipeline_object = get_pipeline_by_name(pipeline_objects,
                                                   'Transcription factor ChIP-seq')
            if pipeline_object:
                if 'assembly' in file_to_check:
                    detail = 'Alignment file {} '.format(file_to_check['@id']) + \
                        'produced by {} '.format(pipeline_object['title']) + \
                        'pipeline ( {} ) using the {} assembly '.format(
                        pipeline_object['@id'],
                        file_to_check['assembly']) + \
                        'has {} '.format(read_depth) + \
                        'usable fragments. ' + \
                        'The minimum ENCODE standard for each replicate in a ChIP-seq ' + \
                        'experiment targeting {} and investigated as '.format(target_name) + \
                        'a transcription factor is 10 million usable fragments. ' + \
                        'The recommended value is > 20 million, but > 10 million is ' + \
                        'acceptable. (See /data-standards/chip-seq/ )'
                else:
                    detail = 'Alignment file {} '.format(file_to_check['@id']) + \
                        'produced by {} '.format(pipeline_object['title']) + \
                        'pipeline ( {} ) '.format(pipeline_object['@id']) + \
                        'has {} '.format(read_depth) + \
                        'usable fragments. ' + \
                        'The minimum ENCODE standard for each replicate in a ChIP-seq ' + \
                        'experiment targeting {} and investigated as '.format(target_name) + \
                        'a transcription factor is 10 million usable fragments. ' + \
                        'The recommended value is > 20 million, but > 10 million is ' + \
                        'acceptable. (See /data-standards/chip-seq/ )'
                if read_depth >= 10000000 and read_depth < marks['narrow']:
                    yield AuditFailure('low read depth', detail, level='WARNING')
                elif read_depth < 10000000 and read_depth >= 3000000:
                    yield AuditFailure('insufficient read depth',
                                       detail, level='NOT_COMPLIANT')
                elif read_depth < 3000000:
                    yield AuditFailure('extremely low read depth',
                                       detail, level='ERROR')


def check_file_read_depth(file_to_check,
                          read_depth,
                          upper_threshold,
                          middle_threshold,
                          lower_threshold,
                          assay_term_name,
                          pipeline_title,
                          pipeline,
                          standards_link):
    if read_depth is False:
        detail = 'Alignment file {} has no read depth information.'.format(
            file_to_check['@id'])
        yield AuditFailure('missing read depth', detail, level='INTERNAL_ACTION')
        return

    if read_depth is not False:
        second_half_of_detail = 'The minimum ENCODE standard for each replicate in a ' + \
            '{} assay is {} aligned reads. '.format(assay_term_name, middle_threshold) + \
            'The recommended value is > {}. '.format(upper_threshold) + \
            '(See {} )'.format(standards_link)
        if middle_threshold == upper_threshold:
            second_half_of_detail = 'The minimum ENCODE standard for each replicate in a ' + \
                '{} assay is {} aligned reads. '.format(assay_term_name, middle_threshold) + \
                '(See {} )'.format(standards_link)
        if 'assembly' in file_to_check:
            detail = 'Alignment file {} produced by {} '.format(file_to_check['@id'],
                                                                pipeline_title) + \
                     'pipeline ( {} ) using the {} assembly has {} aligned reads. '.format(
                         pipeline['@id'], file_to_check['assembly'], read_depth) + \
                     second_half_of_detail
        else:
            detail = 'Alignment file {} produced by {} '.format(file_to_check['@id'],
                                                                pipeline_title) + \
                     'pipeline ( {} ) has {} aligned reads. '.format(pipeline['@id'], read_depth) + \
                     second_half_of_detail
        if read_depth >= middle_threshold and read_depth < upper_threshold:
            yield AuditFailure('low read depth', detail, level='WARNING')
            return
        elif read_depth >= lower_threshold and read_depth < middle_threshold:
            yield AuditFailure('insufficient read depth', detail,
                               level='NOT_COMPLIANT')
        elif read_depth < lower_threshold:
            yield AuditFailure('extremely low read depth', detail,
                               level='ERROR')
            return


def check_file_platform(file_to_check, excluded_platforms):
    if 'platform' not in file_to_check:
        detail = 'Reads file {} missing platform'.format(file_to_check['@id'])
        yield AuditFailure('missing platform', detail, level='WARNING')
    elif file_to_check['platform'] in excluded_platforms:
        detail = 'Reads file {} has not compliant '.format(file_to_check['@id']) + \
                 'platform (SOLiD) {}.'.format(file_to_check['platform'])
        yield AuditFailure('not compliant platform', detail, level='WARNING')


def check_file_read_length_chip(file_to_check, upper_threshold_length,
                                medium_threshold_length,
                                lower_threshold_length):
    if 'read_length' not in file_to_check:
        detail = 'Reads file {} missing read_length'.format(file_to_check['@id'])
        yield AuditFailure('missing read_length', detail, level='NOT_COMPLIANT')
        return

    read_length = file_to_check['read_length']
    detail = 'Fastq file {} '.format(file_to_check['@id']) + \
             'has read length of {}bp. '.format(read_length) + \
             'For mapping accuracy ENCODE standards recommend that sequencing reads should ' + \
             'be at least {}bp long. (See /data-standards/chip-seq/ )'.format(
                 upper_threshold_length)
    if read_length < lower_threshold_length:
        yield AuditFailure('extremely low read length', detail, level='ERROR')
    elif read_length >= lower_threshold_length and read_length < medium_threshold_length:
        yield AuditFailure('insufficient read length', detail, level='NOT_COMPLIANT')
    elif read_length >= medium_threshold_length and read_length < upper_threshold_length:
        yield AuditFailure('low read length', detail, level='WARNING')
    return


def check_file_read_length_rna(file_to_check, threshold_length, pipeline_title, standard_link):
    if 'read_length' not in file_to_check:
        detail = 'Reads file {} missing read_length'.format(file_to_check['@id'])
        yield AuditFailure('missing read_length', detail, level='NOT_COMPLIANT')
        return
    read_length = file_to_check['read_length']
    if read_length < threshold_length:
        detail = 'Fastq file {} '.format(file_to_check['@id']) + \
                 'has read length of {}bp. '.format(read_length) + \
                 'ENCODE uniform processing pipelines ({}) '.format(pipeline_title) + \
                 'require sequencing reads to be at least {}bp long. (See {} )'.format(
                     threshold_length,
                     standard_link)

        yield AuditFailure('insufficient read length', detail,
                           level='NOT_COMPLIANT')
    return

def get_organism_name(reps):
    for rep in reps:
        if rep['status'] not in ['replaced', 'revoked', 'deleted'] and \
           'library' in rep and \
           rep['library']['status'] not in ['replaced', 'revoked', 'deleted'] and \
           'biosample' in rep['library'] and \
           rep['library']['biosample']['status'] not in ['replaced', 'revoked', 'deleted']:
            if 'organism' in rep['library']['biosample']:
                return rep['library']['biosample']['organism']['name']
    return False


def scan_files_for_file_format_output_type(files_to_scan, f_format, f_output_type):
    files_to_return = []
    for f in files_to_scan:
        if 'file_format' in f and f['file_format'] == f_format and \
           'output_type' in f and f['output_type'] == f_output_type and \
           f['status'] not in ['replaced', 'revoked', 'deleted', 'archived']:
            files_to_return.append(f)
    return files_to_return


def scanFilesForOutputType(files_to_scan, o_type):
    files_to_return = []
    for f in files_to_scan:
        if 'output_type' in f and f['output_type'] == o_type and \
           f['status'] not in ['replaced', 'revoked', 'deleted']:
            files_to_return.append(f)
    return files_to_return


def scanFilesForPipelineTitle_yes_chipseq(alignment_files, pipeline_titles):
    for f in alignment_files:
        if 'file_format' in f and f['file_format'] == 'bam' and \
           f['status'] not in ['replaced', 'revoked', 'deleted'] and \
           f['lab'] in ['/labs/encode-processing-pipeline/', '/labs/kevin-white/'] and \
           'analysis_step_version' in f and \
           'analysis_step' in f['analysis_step_version'] and \
           'pipelines' in f['analysis_step_version']['analysis_step']:
            pipelines = f['analysis_step_version']['analysis_step']['pipelines']
            for p in pipelines:
                if p['title'] in pipeline_titles:
                    return p['title']
    return False


def scanFilesForPipelineTitle_not_chipseq(files_to_scan, assemblies, pipeline_titles):
    for f in files_to_scan:
        if 'file_format' in f and f['file_format'] == 'bam' and \
           f['status'] not in ['replaced', 'revoked', 'deleted'] and \
           'assembly' in f and f['assembly'] in assemblies and \
           f['lab'] == '/labs/encode-processing-pipeline/' and \
           'analysis_step_version' in f and \
           'analysis_step' in f['analysis_step_version'] and \
           'pipelines' in f['analysis_step_version']['analysis_step']:
            pipelines = f['analysis_step_version']['analysis_step']['pipelines']
            for p in pipelines:
                if p['title'] in pipeline_titles:
                    return p['title']
    return False


def get_pipeline_objects(files):
    added_pipelines = []
    pipelines_to_return = []
    for inspected_file in files:
        if 'analysis_step_version' in inspected_file and \
           'analysis_step' in inspected_file['analysis_step_version'] and \
           'pipelines' in inspected_file['analysis_step_version']['analysis_step']:
            for p in inspected_file['analysis_step_version']['analysis_step']['pipelines']:
                if p['title'] not in added_pipelines:
                    added_pipelines.append(p['title'])
                    pipelines_to_return.append(p)
    return pipelines_to_return


def get_pipeline_by_name(pipeline_objects, pipeline_title):
    for pipe in pipeline_objects:
        if pipe['title'] == pipeline_title:
            return pipe
    return None


def getPipelines(alignment_files):
    pipelines = set()
    for alignment_file in alignment_files:
        if 'analysis_step_version' in alignment_file and \
           'analysis_step' in alignment_file['analysis_step_version'] and \
           'pipelines' in alignment_file['analysis_step_version']['analysis_step']:
            for p in alignment_file['analysis_step_version']['analysis_step']['pipelines']:
                pipelines.add(p['title'])
    return pipelines


@audit_checker('Experiment', frame=['original_files', 'target',
                                    'original_files.analysis_step_version',
                                    'original_files.analysis_step_version.analysis_step',
                                    'original_files.analysis_step_version.analysis_step.pipelines',
                                    'replicates', 'replicates.library'],
               condition=rfa('ENCODE3'))
def audit_experiment_needs_pipeline(value, system):

    if value['status'] not in ['released', 'ready for review']:
        return

    if 'assay_term_name' not in value:
        return

    if value['assay_term_name'] not in ['whole-genome shotgun bisulfite sequencing',
                                        'ChIP-seq',
                                        'RNA-seq',
                                        'shRNA knockdown followed by RNA-seq',
                                        'siRNA knockdown followed by RNA-seq',
                                        'RAMPAGE']:
        return

    if 'original_files' not in value or len(value['original_files']) == 0:
        #  possible ERROR to throw
        return

    pipelines_dict = {'WGBS': ['WGBS single-end pipeline', 'WGBS single-end pipeline - version 2',
                               'WGBS paired-end pipeline'],
                      'RNA-seq-long-paired': ['RNA-seq of long RNAs (paired-end, stranded)'],
                      'RNA-seq-long-single': ['RNA-seq of long RNAs (single-end, unstranded)'],
                      'RNA-seq-short': ['Small RNA-seq single-end pipeline'],
                      'RAMPAGE': ['RAMPAGE (paired-end, stranded)'],
                      'ChIP': ['Histone ChIP-seq']}

    if value['assay_term_name'] == 'whole-genome shotgun bisulfite sequencing':
        if scanFilesForPipeline(value['original_files'], pipelines_dict['WGBS']) is False:
            detail = 'Experiment {} '.format(value['@id']) + \
                     ' needs to be processed by WGBS pipeline.'
            raise AuditFailure('needs pipeline run', detail, level='INTERNAL_ACTION')
        else:
            return

    if 'replicates' not in value:
        return

    file_size_range = 0

    size_flag = False

    for rep in value['replicates']:
        if 'library' in rep:
            if 'size_range' in rep['library']:
                file_size_range = rep['library']['size_range']
                size_flag = True
                break

    if size_flag is False:
        return

    run_type = 'unknown'

    for f in value['original_files']:
        if f['status'] not in ['deleted', 'replaced', 'revoked'] and 'run_type' in f:
            run_type = f['run_type']
            break

    if run_type == 'unknown':
        return

    if value['assay_term_name'] == 'RAMPAGE' and \
       run_type == 'paired-ended' and \
       file_size_range == '>200':
        if scanFilesForPipeline(value['original_files'], pipelines_dict['RAMPAGE']) is False:
            detail = 'Experiment {} '.format(value['@id']) + \
                     'needs to be processed by pipeline {}.'.format(pipelines_dict['RAMPAGE'][0])
            raise AuditFailure('needs pipeline run', detail, level='INTERNAL_ACTION')
        else:
            return

    if value['assay_term_name'] in ['RNA-seq', 'shRNA knockdown followed by RNA-seq',
                                    'siRNA knockdown followed by RNA-seq'] and \
       run_type == 'single-ended' and \
       file_size_range == '>200':
        if scanFilesForPipeline(value['original_files'],
                                pipelines_dict['RNA-seq-long-single']) is False:
            detail = 'Experiment {} '.format(value['@id']) + \
                     'needs to be processed by ' + \
                     'pipeline {}.'.format(pipelines_dict['RNA-seq-long-single'][0])
            raise AuditFailure('needs pipeline run', detail, level='INTERNAL_ACTION')
        else:
            return

    if value['assay_term_name'] in ['RNA-seq', 'shRNA knockdown followed by RNA-seq'
                                    'siRNA knockdown followed by RNA-seq'] and \
       run_type == 'paired-ended' and \
       file_size_range == '>200':
        if scanFilesForPipeline(value['original_files'],
                                pipelines_dict['RNA-seq-long-paired']) is False:
            detail = 'Experiment {} '.format(value['@id']) + \
                     'needs to be processed by ' + \
                     'pipeline {}.'.format(pipelines_dict['RNA-seq-long-paired'][0])
            raise AuditFailure('needs pipeline run', detail, level='INTERNAL_ACTION')
        else:
            return

    if value['assay_term_name'] == 'RNA-seq' and \
       run_type == 'single-ended' and \
       file_size_range == '<200':
        if scanFilesForPipeline(value['original_files'],
                                pipelines_dict['RNA-seq-short']) is False:
            detail = 'Experiment {} '.format(value['@id']) + \
                     'needs to be processed by ' + \
                     'pipeline {}.'.format(pipelines_dict['RNA-seq-short'][0])
            raise AuditFailure('needs pipeline run', detail, level='INTERNAL_ACTION')
        else:
            return

    investigated_as_histones = False

    if 'target' in value and 'histone modification' in value['target']['investigated_as']:
        investigated_as_histones = True

    if value['assay_term_name'] == 'ChIP-seq' and investigated_as_histones is True:
        if scanFilesForPipeline(value['original_files'],
                                pipelines_dict['ChIP']) is False:
            detail = 'Experiment {} '.format(value['@id']) + \
                     'needs to be processed by ' + \
                     'pipeline {}.'.format(pipelines_dict['ChIP'])
            raise AuditFailure('needs pipeline run', detail, level='INTERNAL_ACTION')
        else:
            return
    return


def scanFilesForPipeline(files_to_scan, pipeline_title_list):
    for f in files_to_scan:
        if 'analysis_step_version' not in f:
            continue
        else:
            if 'analysis_step' not in f['analysis_step_version']:
                continue
            else:
                if 'pipelines' not in f['analysis_step_version']['analysis_step']:
                    continue
                else:
                    pipelines = f['analysis_step_version']['analysis_step']['pipelines']
                    for p in pipelines:
                        if p['title'] in pipeline_title_list:
                            return True
    return False


def get_biosamples(experiment):
    accessions_set = set()
    biosamples_list = []
    if 'replicates' in experiment:
            for rep in experiment['replicates']:
                if ('library' in rep) and ('biosample' in rep['library']):
                    biosample = rep['library']['biosample']
                    if biosample['accession'] not in accessions_set:
                        accessions_set.add(biosample['accession'])
                        biosamples_list.append(biosample)
    return biosamples_list


@audit_checker('experiment', frame=['replicates',
                                    'replicates.library',
                                    'replicates.library.biosample'])
def audit_experiment_internal_tag(value, system):

    if value['status'] in ['deleted', 'replaced']:
        return

    experimental_tags = []
    if 'internal_tags' in value:
        experimental_tags = value['internal_tags']

    updated_experimental_tags = []
    for tag in experimental_tags:
        if tag in ['ENTEx', 'SESCC']:
            updated_experimental_tags.append(tag)

    experimental_tags = updated_experimental_tags
    biosamples = get_biosamples(value)
    bio_tags = set()

    for biosample in biosamples:
        if 'internal_tags' in biosample:
            for tag in biosample['internal_tags']:
                if tag in ['ENTEx', 'SESCC']:
                    bio_tags.add(tag)
                    if experimental_tags == []:
                        detail = 'This experiment contains a ' + \
                                 'biosample {} '.format(biosample['@id']) + \
                                 'with internal tag {}, '.format(tag) + \
                                 'while the experiment has  ' + \
                                 'no internal_tags specified.'
                        yield AuditFailure('inconsistent internal tags',
                                           detail, level='INTERNAL_ACTION')
                    elif experimental_tags != [] and tag not in experimental_tags:
                        detail = 'This experiment contains a ' + \
                                 'biosample {} '.format(biosample['@id']) + \
                                 'with internal tag {} '.format(tag) + \
                                 'that is not specified in experimental ' + \
                                 'list of internal_tags {}.'.format(experimental_tags)
                        yield AuditFailure('inconsistent internal tags',
                                           detail, level='INTERNAL_ACTION')

    if len(bio_tags) == 0 and len(experimental_tags) > 0:
        for biosample in biosamples:
            detail = 'This experiment contains a ' + \
                     'biosample {} without internal tags '.format(biosample['@id']) + \
                     'belonging to internal tags {} '.format(experimental_tags) + \
                     'of the experiment.'
            yield AuditFailure('inconsistent internal tags',
                               detail, level='INTERNAL_ACTION')

    for biosample in biosamples:
        if len(bio_tags) > 0 and ('internal_tags' not in biosample or
                                  biosample['internal_tags'] == []):
            detail = 'This experiment contains a ' + \
                     'biosample {} with no internal tags '.format(biosample['@id']) + \
                     'belonging to internal tags {} '.format(list(bio_tags)) + \
                     'other biosamples are assigned.'
            yield AuditFailure('inconsistent internal tags',
                               detail, level='INTERNAL_ACTION')
        elif len(bio_tags) > 0 and biosample['internal_tags'] != []:
            for x in bio_tags:
                if x not in biosample['internal_tags']:
                    detail = 'This experiment contains a ' + \
                             'biosample {} without internal tag '.format(biosample['@id']) + \
                             '{} belonging to internal tags {} '.format(x, list(bio_tags)) + \
                             'other biosamples are assigned.'
                    yield AuditFailure('inconsistent internal tags',
                                       detail, level='INTERNAL_ACTION')


def is_gtex_experiment(experiment_to_check):
    for rep in experiment_to_check['replicates']:
        if ('library' in rep) and ('biosample' in rep['library']) and \
           ('donor' in rep['library']['biosample']):
            if rep['library']['biosample']['donor']['accession'] in gtexDonorsList:
                return True
    return False


@audit_checker('experiment', frame=['replicates',
                                    'replicates.library',
                                    'replicates.library.biosample',
                                    'replicates.library.biosample.donor'])
def audit_experiment_gtex_biosample(value, system):
    '''
    GTEx experiments should include biosample(s) from the same tissue and same donor
    The number of biosamples could be > 1.
    '''
    if value['status'] in ['deleted', 'replaced']:
        return

    if len(value['replicates']) < 2:
        return

    if is_gtex_experiment(value) is False:
        return

    donors_set = set()
    tissues_set = set()

    for rep in value['replicates']:
        if ('library' in rep) and ('biosample' in rep['library']):
            biosampleObject = rep['library']['biosample']
            if ('donor' in biosampleObject):
                donors_set.add(biosampleObject['donor']['accession'])
                tissues_set.add(biosampleObject['biosample_term_name'])

    if len(donors_set) > 1:
        detail = 'GTEx experiment {} '.format(value['@id']) + \
                 'contains {} '.format(len(donors_set)) + \
                 'donors, while according to HRWG decision it should have a single donor.'
        yield AuditFailure('invalid modelling of GTEx experiment ', detail, level='INTERNAL_ACTION')

    if len(tissues_set) > 1:
        detail = 'GTEx experiment {} '.format(value['@id']) + \
                 'was performed using  {} '.format(len(tissues_set)) + \
                 'tissue types, while according to HRWG decision it should have ' + \
                 'been perfomed using a single tissue type.'
        yield AuditFailure('invalid modelling of GTEx experiment ', detail, level='INTERNAL_ACTION')

    return


@audit_checker('Experiment', frame=['object'])
def audit_experiment_geo_submission(value, system):
    if value['status'] not in ['released']:
        return
    if 'assay_term_id' in value and \
       value['assay_term_id'] in ['NTR:0000612',
                                  'OBI:0001923',
                                  'OBI:0002044']:
        return
    submitted_flag = False
    detail = 'Experiment {} '.format(value['@id']) + \
             'is released, but was not submitted to GEO.'
    if 'dbxrefs' in value and value['dbxrefs'] != []:
        for entry in value['dbxrefs']:
            if entry.startswith('GEO:'):
                submitted_flag = True
    if submitted_flag is False:
        detail = 'Experiment {} '.format(value['@id']) + \
                 'is released, but is not submitted to GEO.'
        yield AuditFailure('experiment not submitted to GEO', detail, level='INTERNAL_ACTION')
    return


@audit_checker('experiment', frame=['object'])
def audit_experiment_biosample_term_id(value, system):
    if value['status'] in ['deleted', 'replaced', 'revoked']:
        return
    # excluding Bind-n-Seq because they dont have biosamples
    if 'assay_term_name' in value and value['assay_term_name'] == 'RNA Bind-n-Seq':
        return

    if value['status'] not in ['preliminary', 'proposed']:
        if 'biosample_term_id' not in value:
            detail = 'Experiment {} '.format(value['@id']) + \
                     'has no biosample_term_id'
            yield AuditFailure('experiment missing biosample_term_id', detail, level='INTERNAL_ACTION')
        if 'biosample_type' not in value:
            detail = 'Experiment {} '.format(value['@id']) + \
                     'has no biosample_type'
            yield AuditFailure('experiment missing biosample_type', detail, level='INTERNAL_ACTION')
    return


@audit_checker('experiment',
               frame=['replicates', 'original_files', 'original_files.replicate'])
def audit_experiment_consistent_sequencing_runs(value, system):
    if value['status'] in ['deleted', 'replaced', 'revoked']:
        return
    if 'replicates' not in value:
        return
    if len(value['replicates']) == 0:
        return
    if 'assay_term_name' not in value:  # checked in audit_experiment_assay
        return

    if value.get('assay_term_name') not in ['ChIP-seq', 'DNase-seq']:
        return

    replicate_pairing_statuses = {}
    replicate_read_lengths = {}

    for file_object in value['original_files']:
        if file_object['status'] in ['deleted', 'replaced', 'revoked', 'archived']:
            continue
        if file_object['file_format'] == 'fastq':
            if 'replicate' in file_object:
                bio_rep_number = file_object['replicate']['biological_replicate_number']

                if 'read_length' in file_object:
                    if bio_rep_number not in replicate_read_lengths:
                        replicate_read_lengths[bio_rep_number] = set()
                    replicate_read_lengths[bio_rep_number].add(file_object['read_length'])

                if 'run_type' in file_object:
                    if bio_rep_number not in replicate_pairing_statuses:
                        replicate_pairing_statuses[bio_rep_number] = set()
                    replicate_pairing_statuses[bio_rep_number].add(file_object['run_type'])

    for key in replicate_read_lengths:
        if len(replicate_read_lengths[key]) > 1:
            upper_value = max(list(replicate_read_lengths[key]))
            lower_value = min(list(replicate_read_lengths[key]))
            if ((upper_value - lower_value) > 2):
                detail = 'Biological replicate {} '.format(key) + \
                         'in experiment {} '.format(value['@id']) + \
                         'has mixed sequencing read lengths {}.'.format(replicate_read_lengths[key])
                yield AuditFailure('mixed read lengths',
                                   detail, level='WARNING')

    for key in replicate_pairing_statuses:
        if len(replicate_pairing_statuses[key]) > 1:
            detail = 'Biological replicate {} '.format(key) + \
                     'in experiment {} '.format(value['@id']) + \
                     'has mixed endedness {}.'.format(replicate_pairing_statuses[key])
            yield AuditFailure('mixed run types',
                               detail, level='WARNING')

    keys = list(replicate_read_lengths.keys())

    if len(keys) > 1:
        for index_i in range(len(keys)):
            for index_j in range(index_i+1, len(keys)):
                i_lengths = list(replicate_read_lengths[keys[index_i]])
                j_lengths = list(replicate_read_lengths[keys[index_j]])

                i_max = max(i_lengths)
                i_min = min(i_lengths)
                j_max = max(j_lengths)
                j_min = min(j_lengths)

                diff_flag = False
                if (i_max - j_min) > 2:
                    diff_flag = True
                if (j_max - i_min) > 2:
                    diff_flag = True

                if diff_flag is True:
                    detail = 'Biological replicate {} '.format(keys[index_i]) + \
                             'in experiment {} '.format(value['@id']) + \
                             'has sequencing read lengths {} '.format(i_lengths) + \
                             ' that differ from replicate {},'.format(keys[index_j]) + \
                             ' which has {} sequencing read lengths.'.format(j_lengths)
                    yield AuditFailure('mixed read lengths',
                                       detail, level='WARNING')

    keys = list(replicate_pairing_statuses.keys())
    if len(keys) > 1:
        for index_i in range(len(keys)):
            for index_j in range(index_i+1, len(keys)):
                i_pairs = replicate_pairing_statuses[keys[index_i]]
                j_pairs = replicate_pairing_statuses[keys[index_j]]
                diff_flag = False
                for entry in i_pairs:
                    if entry not in j_pairs:
                        diff_flag = True
                for entry in j_pairs:
                    if entry not in i_pairs:
                        diff_flag = True
                if diff_flag is True:
                    detail = 'Biological replicate {} '.format(keys[index_i]) + \
                             'in experiment {} '.format(value['@id']) + \
                             'has endedness {} '.format(i_pairs) + \
                             ' that differ from replicate {},'.format(keys[index_j]) + \
                             ' which has {}.'.format(j_pairs)
                    yield AuditFailure('mixed run types',
                                       detail, level='WARNING')

    return


@audit_checker('experiment',
               frame=['award', 'replicates', 'original_files', 'original_files.replicate'],
               condition=rfa("ENCODE3", "modERN", "ENCODE2", "GGR", "Roadmap",
                             "ENCODE", "modENCODE", "MODENCODE", "ENCODE2-Mouse"))
def audit_experiment_replicate_with_no_files(value, system):
    if 'internal_tags' in value and 'DREAM' in value['internal_tags']:
        return

    if value['status'] in ['deleted', 'replaced', 'revoked', 'proposed', 'preliminary']:
        return
    if 'replicates' not in value:
        return
    if len(value['replicates']) == 0:
        return
    if 'assay_term_name' not in value:  # checked in audit_experiment_assay
        return

    seq_assay_flag = False
    if value['assay_term_name'] in seq_assays:
        seq_assay_flag = True

    rep_dictionary = {}
    rep_numbers = {}
    for rep in value['replicates']:
        rep_dictionary[rep['@id']] = []
        rep_numbers[rep['@id']] = (rep['biological_replicate_number'],rep['technical_replicate_number'])

    for file_object in value['original_files']:
        if file_object['status'] in ['deleted', 'replaced', 'revoked']:
            continue
        if 'replicate' in file_object:
            file_replicate = file_object['replicate']
            if file_replicate['@id'] in rep_dictionary:
                rep_dictionary[file_replicate['@id']].append(file_object['output_category'])

    audit_level = 'ERROR'
    if value['award']['rfa'] in ["ENCODE2", "Roadmap",
                                 "modENCODE", "MODENCODE", "ENCODE2-Mouse"]:
        audit_level = 'INTERNAL_ACTION'

    for key in rep_dictionary.keys():

        if len(rep_dictionary[key]) == 0:
            detail = 'This experiment contains a replicate ' + \
                     '[{},{}] {} without any associated files.'.format(
                         rep_numbers[key][0],
                         rep_numbers[key][1],
                         key)

            yield AuditFailure('missing raw data in replicate', detail, level=audit_level)
        else:
            if seq_assay_flag is True:
                if 'raw data' not in rep_dictionary[key]:
                    detail = 'This experiment contains a replicate ' + \
                             '[{},{}] {} without raw data associated files.'.format(
                                 rep_numbers[key][0],
                                 rep_numbers[key][1],
                                 key)
                    yield AuditFailure('missing raw data in replicate',
                                       detail, level=audit_level)
    return


@audit_checker('experiment', frame='object')
def audit_experiment_release_date(value, system):
    '''
    Released experiments need release date.
    This should eventually go to schema
    '''
    if value['status'] in ['released', 'revoked'] and 'date_released' not in value:
        detail = 'Experiment {} is released or revoked and requires a value in date_released'.format(value['@id'])
        raise AuditFailure('missing date_released', detail, level='INTERNAL_ACTION')


@audit_checker('experiment',
               frame=['replicates', 'award', 'target',
                      'replicates.library',
                      'replicates.library.biosample',
                      'replicates.library.biosample.donor'],
               condition=rfa("ENCODE3", "modERN", "GGR",
                             "ENCODE", "modENCODE", "MODENCODE", "ENCODE2-Mouse"))
def audit_experiment_replicated(value, system):
    '''
    Experiments in ready for review state should be replicated. If not,
    wranglers should check with lab as to why before release.
    '''
    if value['status'] not in ['released', 'ready for review']:
        return
    '''
    Excluding single cell isolation experiments from the replication requirement
    Excluding RNA-bind-and-Seq from the replication requirment
    '''
    if value['assay_term_name'] in ['single cell isolation followed by RNA-seq',
                                    'RNA Bind-n-Seq']:
        return
    '''
    Excluding GTEX experiments from the replication requirement
    '''
    if is_gtex_experiment(value) is True:
        return

    if 'target' in value:
        target = value['target']
        if 'control' in target['investigated_as']:
            return

    num_bio_reps = set()
    for rep in value['replicates']:
        num_bio_reps.add(rep['biological_replicate_number'])

    if len(num_bio_reps) <= 1:
        # different levels of severity for different rfas
        if value['award']['rfa'] in ['ENCODE3', 'GGR']:
            detail = 'This experiment is expected to be replicated, but ' + \
                     'contains only one listed biological replicate.'
            raise AuditFailure('unreplicated experiment', detail, level='NOT_COMPLIANT')


@audit_checker('experiment', frame=['replicates', 'replicates.library'])
def audit_experiment_replicates_with_no_libraries(value, system):
    if value['status'] in ['deleted', 'replaced', 'revoked', 'proposed']:
        return
    if len(value['replicates']) == 0:
        return
    for rep in value['replicates']:
        if 'library' not in rep:
            detail = 'Experiment {} has a replicate {}, that has no library associated with'.format(
                value['@id'],
                rep['@id'])
            yield AuditFailure('replicate with no library', detail, level='ERROR')
    return


@audit_checker('experiment', frame=['replicates',
                                    'replicates.library',
                                    'replicates.library.biosample'])
def audit_experiment_isogeneity(value, system):

    if value['status'] in ['deleted', 'replaced', 'revoked']:
        return

    if len(value['replicates']) < 2:
        return

    if value.get('replication_type') is None:
        detail = 'In experiment {} the replication_type cannot be determined'.format(value['@id'])
        yield AuditFailure('undetermined replication_type', detail, level='INTERNAL_ACTION')

    biosample_dict = {}
    biosample_age_set = set()
    biosample_sex_set = set()
    biosample_donor_set = set()

    for rep in value['replicates']:
        if 'library' in rep:
            if 'biosample' in rep['library']:
                biosampleObject = rep['library']['biosample']
                biosample_dict[biosampleObject['accession']] = biosampleObject
                biosample_age_set.add(biosampleObject.get('age_display'))
                biosample_sex_set.add(biosampleObject.get('sex'))
                biosample_donor_set.add(biosampleObject.get('donor'))
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

    if len(biosample_donor_set) > 1:
        donors_list = str(list(biosample_donor_set)).replace('\'', ' ')
        detail = 'Replicates of this experiment were prepared using biosamples ' + \
                 'from different strains {}.'.format(donors_list)
        yield AuditFailure('inconsistent donor', detail, level='ERROR')

    if len(biosample_age_set) > 1:
        ages_list = str(list(biosample_age_set)).replace('\'', ' ')
        detail = 'Replicates of this experiment were prepared using biosamples ' + \
                 'of different ages {}.'.format(ages_list)
        yield AuditFailure('inconsistent age', detail, level='NOT_COMPLIANT')

    if len(biosample_sex_set) > 1:
        sexes_list = str(list(biosample_sex_set)).replace('\'', ' ')
        detail = 'Replicates of this experiment were prepared using biosamples ' + \
                 'of different sexes {}.'.format(sexes_list)
        yield AuditFailure('inconsistent sex', detail, level='NOT_COMPLIANT')
    return


@audit_checker('experiment', frame=['replicates', 'replicates.library'])
def audit_experiment_technical_replicates_same_library(value, system):
    if value['status'] in ['deleted', 'replaced', 'revoked']:
        return
    biological_replicates_dict = {}
    for rep in value['replicates']:
        bio_rep_num = rep['biological_replicate_number']
        if 'library' in rep:
            library = rep['library']
            if bio_rep_num not in biological_replicates_dict:
                biological_replicates_dict[bio_rep_num] = []
            if library['accession'] in biological_replicates_dict[bio_rep_num]:
                detail = 'Experiment {} has '.format(value['@id']) + \
                         'different technical replicates associated with the same library'
                raise AuditFailure('sequencing runs labeled as technical replicates', detail,
                                   level='INTERNAL_ACTION')
            else:
                biological_replicates_dict[bio_rep_num].append(library['accession'])


@audit_checker('experiment', frame=['replicates', 'award',
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
                                       detail, level='INTERNAL_ACTION')
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


@audit_checker('experiment', frame=['replicates', 'replicates.library'],
               condition=rfa("ENCODE3", "modERN", "GGR",
                             "ENCODE", "ENCODE2-Mouse", "Roadmap"))
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

    if 'assay_term_id' is None:
        # This means we need to add an assay to the enum list. It should not happen
        # though since the term enum list is limited.
        detail = 'Experiment {} is missing assay_term_id'.format(value['@id'])
        yield AuditFailure('missing assay information', detail, level='ERROR')
        return

    ontology = system['registry']['ontology']
    term_id = value.get('assay_term_id')
    term_name = value.get('assay_term_name')

    if term_id.startswith('NTR:'):
        detail = 'Assay_term_id is a New Term Request ({} - {})'.format(term_id, term_name)
        yield AuditFailure('NTR assay', detail, level='INTERNAL_ACTION')

        if term_name != NTR_assay_lookup[term_id]:
            detail = 'Experiment has a mismatch between assay_term_name "{}" and assay_term_id "{}"'.format(
                term_name,
                term_id,
            )
            yield AuditFailure('mismatched assay_term_name', detail, level='INTERNAL_ACTION')
            return

    elif term_id not in ontology:
        detail = 'Assay_term_id {} is not found in cached version of ontology'.format(term_id)
        yield AuditFailure('assay_term_id not in ontology', term_id, level='INTERNAL_ACTION')
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
        yield AuditFailure('mismatched assay_term_name', detail, level='INTERNAL_ACTION')
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
    if value['assay_term_name'] in ['RNA Bind-n-Seq',
                                    'shRNA knockdown followed by RNA-seq',
                                    'siRNA knockdown followed by RNA-seq',
                                    'CRISPR genome editing followed by RNA-seq']:
        return

    # Check that target of experiment matches target of antibody
    for rep in value['replicates']:
        if 'antibody' not in rep:
            detail = '{} assays require an antibody specification. '.format(value['assay_term_name']) + \
                     'In replicate [{},{}] {}, the antibody needs to be specified.'.format(
                rep['biological_replicate_number'],
                rep['technical_replicate_number'],
                rep['@id']
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
                antibody_targets = []
                for antibody_target in antibody['targets']:
                    antibody_targets.append(antibody_target.get('name'))
                    if target['name'] == antibody_target.get('name'):
                        target_matches = True
                if not target_matches:
                    antibody_targets_string = str(antibody_targets).replace('\'', '')
                    detail = 'The target of the experiment is {}, '.format(target['name']) + \
                             'but it is not present in the experiment\'s antibody {} '.format(antibody['@id']) + \
                             'target list {}.'.format(antibody_targets_string)
                    yield AuditFailure('inconsistent target', detail, level='ERROR')


@audit_checker('experiment', frame=['award', 'target', 'possible_controls'],
               condition=rfa("ENCODE3", "modERN", "ENCODE2", "modENCODE",
                             "ENCODE", "ENCODE2-Mouse", "Roadmap"))
def audit_experiment_control(value, system):
    '''
    Certain assay types (ChIP-seq, ...) require possible controls with a matching biosample.
    Of course, controls do not require controls.
    '''

    if value['status'] in ['deleted', 'proposed', 'replaced']:
        return

    # Currently controls are only be required for ChIP-seq
    if value.get('assay_term_name') not in controlRequiredAssayList:
        return

    # We do not want controls
    if 'target' in value and 'control' in value['target']['investigated_as']:
        return

    audit_level = 'ERROR'
    if value.get('assay_term_name') in ['CAGE',
                                        'RAMPAGE'] or \
       value['award']['rfa'] in ["ENCODE2",
                                 "Roadmap",
                                 "modENCODE",
                                 "ENCODE2-Mouse"]:
        audit_level = 'NOT_COMPLIANT'
    if value['possible_controls'] == []:
        detail = 'possible_controls is a list of experiment(s) that can ' + \
                 'serve as analytical controls for a given experiment. ' + \
                 '{} experiments require a value in possible_controls. '.format(
                     value['assay_term_name']) + \
                 'This experiment should be associated with at least one control ' + \
                 'experiment, but has no specified values in the possible_controls list.'
        raise AuditFailure('missing possible_controls', detail, level=audit_level)

    for control in value['possible_controls']:
        if control.get('biosample_term_id') != value.get('biosample_term_id'):
            detail = 'The specified control {} for this experiment is on {}, '.format(
                control['@id'],
                control.get('biosample_term_name')) + \
                'but this experiment is done on {}.'.format(value['biosample_term_name'])
            raise AuditFailure('inconsistent control', detail, level='ERROR')


@audit_checker('experiment', frame=['possible_controls',
                                    'possible_controls.original_files',
                                    'possible_controls.original_files.platform',
                                    'original_files',
                                    'original_files.platform'])
def audit_experiment_platforms_mismatches(value, system):
    if value['status'] in ['deleted', 'replaced']:
        return
    if 'original_files' not in value or \
       value['original_files'] == []:
        return
    platforms = get_platforms_used_in_experiment(value)
    if len(platforms) > 1:
        platforms_string = str(list(platforms)).replace('\'', '')
        detail = 'This experiment ' + \
                 'contains data produced on incompatible ' + \
                 'platforms {}.'.format(platforms_string)
        yield AuditFailure('inconsistent platforms', detail, level='WARNING')
    elif len(platforms) == 1:
        platform_term_name = list(platforms)[0]
        if 'possible_controls' in value and \
           value['possible_controls'] != []:
            for control in value['possible_controls']:
                control_platforms = get_platforms_used_in_experiment(control)
                if len(control_platforms) > 1:
                    control_platforms_string = str(list(control_platforms)).replace('\'', '')
                    detail = 'possible_controls is a list of experiment(s) that can serve ' + \
                             'as analytical controls for a given experiment. ' + \
                             'Experiment {} found in possible_controls list of this experiment '.format(control['@id']) + \
                             'contains data produced on platform(s) {} '.format(control_platforms_string) + \
                             'which are not compatible with platform {} '.format(platform_term_name) + \
                             'used in this experiment.'
                    yield AuditFailure('inconsistent platforms', detail, level='WARNING')
                elif len(control_platforms) == 1 and \
                        list(control_platforms)[0] != platform_term_name:
                    detail = 'possible_controls is a list of experiment(s) that can serve ' + \
                             'as analytical controls for a given experiment. ' + \
                             'Experiment {} found in possible_controls list of this experiment '.format(control['@id']) + \
                             'contains data produced on platform {} '.format(list(control_platforms)[0]) + \
                             'which is not compatible with platform {} '.format(platform_term_name) + \
                             'used in this experiment.'
                    yield AuditFailure('inconsistent platforms', detail, level='WARNING')
    return


def get_platforms_used_in_experiment(experiment):
    platforms = set()
    if 'original_files' not in experiment or \
       experiment['original_files'] == []:
        return platforms

    for f in experiment['original_files']:
        if f['output_category'] == 'raw data' and \
           'platform' in f and \
           f['status'] not in ['deleted', 'archived', 'replaced']:
            # collapsing interchangable platforms
            if f['platform']['term_name'] in ['HiSeq 2000', 'HiSeq 2500']:
                platforms.add('HiSeq 2000/2500')
            elif f['platform']['term_name'] in ['Illumina Genome Analyzer IIx',
                                                'Illumina Genome Analyzer IIe',
                                                'Illumina Genome Analyzer II']:
                platforms.add('Illumina Genome Analyzer II/e/x')
            else:
                platforms.add(f['platform']['term_name'])
    return platforms


@audit_checker('experiment', frame=['target',
                                    'possible_controls',
                                    'replicates', 'replicates.antibody',
                                    'possible_controls.replicates',
                                    'possible_controls.replicates.antibody',
                                    'possible_controls.target'],
               condition=rfa('ENCODE3', 'Roadmap'))
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


@audit_checker('experiment', frame=['replicates', 'replicates.library'],
               condition=rfa("ENCODE3",
                             "modERN",
                             "ENCODE",
                             "ENCODE2-Mouse",
                             "Roadmap"))
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
            detail = 'Library {} is in '.format(lib['@id']) + \
                     'an RNA-seq experiment and has size_range >200. ' +\
                     'It requires a value for spikeins_used'
            yield AuditFailure('missing spikeins', detail, level='NOT_COMPLIANT')
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
        return

    if term_id.startswith('NTR:'):
        detail = '{} has an NTR biosample {} - {}'.format(value['@id'], term_id, term_name)
        yield AuditFailure('NTR biosample', detail, level='INTERNAL_ACTION')
    else:
        biosample_prefix = term_id.split(':')[0]
        if 'biosample_type' in value and \
           biosample_prefix not in biosampleType_ontologyPrefix[term_type]:
            detail = 'Experiment {} has '.format(value['@id']) + \
                     'a biosample of type {} '.format(term_type) + \
                     'with biosample_term_id {} '.format(value['biosample_term_id']) + \
                     'that is not one of ' + \
                     '{}'.format(biosampleType_ontologyPrefix[term_type])
            yield AuditFailure('experiment with biosample term-type mismatch', detail,
                               level='INTERNAL_ACTION')

        elif term_id not in ontology:
            detail = 'Experiment {} has term_id {} which is not in ontology'.format(
                value['@id'], term_id)
            yield AuditFailure('term_id not in ontology', term_id, level='INTERNAL_ACTION')
        else:
            ontology_name = ontology[term_id]['name']
            if ontology_name != term_name and term_name not in ontology[term_id]['synonyms']:
                detail = 'Experiment {} has a mismatch between biosample term_id ({}) '.format(
                    value['@id'],
                    term_id) + \
                    'and term_name ({}), ontology term_name for term_id {} '.format(
                        term_name, term_id) + \
                    'is {}.'.format(ontology_name)
                yield AuditFailure('inconsistent ontology term', detail, level='ERROR')

    if 'replicates' in value:
        for rep in value['replicates']:
            if 'library' not in rep:
                continue

            lib = rep['library']
            if 'biosample' not in lib:
                detail = '{} is missing biosample, expecting one of type {}'.format(
                    lib['@id'],
                    term_name
                    )
                yield AuditFailure('missing biosample', detail, level='ERROR')
                continue

            biosample = lib['biosample']
            bs_type = biosample.get('biosample_type')
            bs_name = biosample.get('biosample_term_name')
            bs_id = biosample.get('biosample_term_id')

            if bs_type != term_type:
                detail = 'Experiment {} '.format(value['@id']) + \
                         'contains a library {} '.format(lib['@id']) + \
                         'prepared from biosample type \"{}\", '.format(bs_type) + \
                         'while experiment\'s biosample type is \"{}\".'.format(term_type)
                yield AuditFailure('inconsistent library biosample', detail, level='ERROR')

            if bs_name != term_name:
                detail = 'Experiment {} '.format(value['@id']) + \
                         'contains a library {} '.format(lib['@id']) + \
                         'prepared from biosample {}, '.format(bs_name) + \
                         'while experiment\'s biosample is {}.'.format(term_name)
                yield AuditFailure('inconsistent library biosample', detail, level='ERROR')

            if bs_id != term_id:
                detail = 'Experiment {} '.format(value['@id']) + \
                         'contains a library {} '.format(lib['@id']) + \
                         'prepared from biosample with an id \"{}\", '.format(bs_id) + \
                         'while experiment\'s biosample id is \"{}\".'.format(term_id)
                yield AuditFailure('inconsistent library biosample', detail, level='ERROR')


@audit_checker(
    'experiment',
    frame=[
        'target',
        'replicates',
        'replicates.antibody',
        'replicates.antibody.targets',
        'replicates.antibody.characterizations',
        'replicates.antibody.lot_reviews'
        'replicates.antibody.lot_reviews.organisms',
        'replicates.library',
        'replicates.library.biosample',
        'replicates.library.biosample.organism',
    ],
    condition=rfa('ENCODE3', 'modERN'))
def audit_experiment_antibody_characterized(value, system):
    '''Check that biosample in the experiment has been characterized for the given antibody.'''

    if value['status'] in ['deleted', 'proposed', 'preliminary']:
        return

    if value.get('assay_term_name') not in targetBasedAssayList:
        return

    if 'target' not in value:
        return

    target = value['target']
    if 'control' in target['investigated_as']:
        return

    if value['assay_term_name'] in ['RNA Bind-n-Seq', 'shRNA knockdown followed by RNA-seq',
                                    'siRNA knockdown followed by RNA-seq']:
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
        antibody_targets = antibody['targets']
        ab_targets_investigated_as = set()
        sample_match = False

        if not antibody['characterizations']:
            detail = '{} has not yet been characterized in any cell type or tissue in {}.'.format(
                antibody['@id'], organism)
            yield AuditFailure('uncharacterized antibody', detail, level='NOT_COMPLIANT')
            return

        for t in antibody_targets:
            for i in t['investigated_as']:
                ab_targets_investigated_as.add(i)

        # We only want the audit raised if the organism in lot reviews matches that of the biosample
        # and if has not been characterized to standards. Otherwise, it doesn't apply and we
        # shouldn't raise a stink

        if 'histone modification' in ab_targets_investigated_as:
            for lot_review in antibody['lot_reviews']:
                if organism == lot_review['organisms'][0]:
                    sample_match = True
                    if lot_review['status'] == 'characterized to standards with exemption':
                        detail = '{} has been characterized '.format(antibody['@id']) + \
                                 'to the standard with exemption for {}'.format(organism)
                        yield AuditFailure('antibody characterized with exemption',
                                           detail, level='WARNING')
                    elif lot_review['status'] == 'awaiting characterization':
                        detail = '{} has not yet been characterized in '.format(antibody['@id']) + \
                            'any cell type or tissue in {}'.format(organism)
                        yield AuditFailure('uncharacterized antibody',
                                           detail, level='NOT_COMPLIANT')
                    elif lot_review['status'] in ['not characterized to standards', 'pending dcc review']:
                        if lot_review['detail'] in ['Awaiting submission of primary characterization(s).',
                                                    'Awaiting submission of secondary characterization(s).',
                                                    'One or more characterization(s) is pending review.',
                                                    'Pending review of a secondary characterization.']:
                            detail = '{} has characterization attempts '.format(antibody['@id']) + \
                                     'but does not have the full complement of characterizations ' + \
                                     'meeting the standard in {}: {}'.format(
                                organism, lot_review['detail'])
                            yield AuditFailure('partially characterized antibody',
                                               detail, level='NOT_COMPLIANT')
                        else:
                            detail = '{} has not been '.format(antibody['@id']) + \
                                'characterized to the standard for {}: {}'.format(organism, lot_review['detail'])
                            yield AuditFailure('antibody not characterized to standard', detail,
                                               level='NOT_COMPLIANT')
                    else:
                        # This should only leave the characterized to standards case
                        pass
        else:
            biosample_term_id = value['biosample_term_id']
            biosample_term_name = value['biosample_term_name']
            experiment_biosample = (biosample_term_id, organism)

            for lot_review in antibody['lot_reviews']:
                biosample_key = (lot_review['biosample_term_id'], lot_review['organisms'][0])
                if experiment_biosample == biosample_key:
                    sample_match = True
                    if lot_review['status'] == 'characterized to standards with exemption':
                        detail = '{} has been characterized to the '.format(antibody['@id']) + \
                            'standard with exemption for {} in {}'.format(biosample_term_name,
                                                                          organism)
                        yield AuditFailure('antibody characterized with exemption', detail,
                                           level='WARNING')
                    elif lot_review['status'] == 'awaiting characterization':
                        detail = '{} has not been characterized at al for {} in {}'.format(
                            antibody['@id'], biosample_term_name, organism)
                        yield AuditFailure('uncharacterized antibody',
                                           detail, level='NOT_COMPLIANT')
                    elif lot_review['status'] in ['not characterized to standards', 'pending dcc review']:
                        if lot_review['detail'] in ['Awaiting submission of primary characterization(s).',
                                                    'Awaiting submission of secondary characterization(s).',
                                                    'One or more characterization(s) is pending review.',
                                                    'Pending review of a secondary characterization.']:
                            detail = '{} has characterization attempts '.format(antibody['@id']) + \
                                     'but does not have the full complement of characterizations ' + \
                                     'meeting the standard in {}: {}'.format(
                                organism, lot_review['detail'])
                            yield AuditFailure('partially characterized antibody',
                                               detail, level='NOT_COMPLIANT')
                        else:
                            detail = '{} has not been '.format(antibody['@id']) + \
                                'characterized to the standard for {}: {}'.format(organism, lot_review['detail'])
                            yield AuditFailure('antibody not characterized to standard', detail,
                                               level='NOT_COMPLIANT')
                    else:
                        # This should only leave the characterized to standards case
                        pass

            # The only characterization present is a secondary or an incomplete primary that
            # has no characterization_reviews since we don't know what the biosample is
            if not sample_match:
                detail = '{} has characterization attempts '.format(antibody['@id']) + \
                    'but does not have the full complement of characterizations ' + \
                    'meeting the standard in this cell type and organism: Awaiting ' + \
                    'submission of primary characterization(s).'.format()
                yield AuditFailure('partially characterized antibody', detail,
                                   level='NOT_COMPLIANT')


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

    RNAs = ['RNA',
            'polyadenylated mRNA',
            'miRNA']

    for rep in value['replicates']:
        if 'library' not in rep:
            continue
        lib = rep['library']
        if (lib['nucleic_acid_term_name'] in RNAs) and ('size_range' not in lib):
            detail = 'Metadata of RNA library {} lacks information on '.format(rep['library']['@id']) + \
                     'the size range of fragments used to construct the library.'
            yield AuditFailure('missing RNA fragment size', detail, level='NOT_COMPLIANT')


@audit_checker(
    'experiment',
    frame=[
        'target',
        'replicates',
        'replicates.library',
        'replicates.library.biosample',
        'replicates.library.biosample.constructs',
        'replicates.library.biosample.constructs.target',
        'replicates.library.biosample.donor',
        'replicates.library.biosample.model_organism_donor_constructs',
        'replicates.library.biosample.model_organism_donor_constructs.target'])
def audit_missing_construct(value, system):

    if value['status'] in ['deleted', 'replaced', 'proposed', 'revoked']:
        return

    if 'target' not in value:
        return

    '''
    Note that this audit only deals with tagged constructs for now and does not check
    genetic_modifications where tagging information could also be specified. Constructs
    should get absorbed by genetic_modifications in the future and this audit would need
    to be re-written.

    Also, the audit does not cover whether or not the biosamples in possible_controls also
    have the same construct. In some cases, they legitimately don't, e.g. HEK-ZNFs
    '''
    target = value['target']
    if 'recombinant protein' not in target['investigated_as']:
        return
    else:
        biosamples = get_biosamples(value)
        missing_construct = list()
        tag_mismatch = list()

        if 'biosample_type' not in value:
            detail = '{} is missing biosample_type'.format(value['@id'])
            yield AuditFailure('missing biosample_type', detail, level='ERROR')

        for biosample in biosamples:
            if (biosample['biosample_type'] != 'whole organisms') and \
               (not biosample['constructs']):
                missing_construct.append(biosample)
            elif (biosample['biosample_type'] == 'whole organisms') and \
                    ('model_organism_donor_constructs' not in biosample):
                    missing_construct.append(biosample)
            elif (biosample['biosample_type'] != 'whole organisms') and biosample['constructs']:
                for construct in biosample['constructs']:
                    if construct['target']['name'] != target['name']:
                        tag_mismatch.append(construct)
            elif (biosample['biosample_type'] == 'whole organisms') and \
                    ('model_organism_donor_constructs' in biosample):
                        for construct in biosample['model_organism_donor_constructs']:
                            if construct['target']['name'] != target['name']:
                                tag_mismatch.append(construct)
            else:
                pass

        if missing_construct:
            for b in missing_construct:
                if 'donor' in b:
                    detail = 'Recombinant protein target {} requires '.format(value['target']['@id']) + \
                        'a fusion protein construct associated with the biosample {} '.format(b['@id']) + \
                        'or donor {} (for whole organism biosamples) to specify '.format(b['donor']['@id']) + \
                        'the relevant tagging details.'
                else:
                    detail = 'Recombinant protein target {} requires '.format(value['target']['@id']) + \
                        'a fusion protein construct associated with the biosample {} '.format(b['@id']) + \
                        'to specify the relevant tagging details.'
                yield AuditFailure('missing tag construct', detail, level='WARNING')

        # Continue audit because only some linked biosamples may have missing constructs, not all.
        if tag_mismatch:
            for c in tag_mismatch:
                detail = 'The target of this assay {} does not'.format(value['target']['@id']) + \
                    ' match that of the linked construct {}, {}.'.format(c['@id'],
                                                                         c['target']['@id'])
                yield AuditFailure('mismatched construct target', detail, level='ERROR')
