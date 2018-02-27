from snovault import (
    AuditFailure,
    audit_checker,
)
from .gtex_data import gtexDonorsList
from .standards_data import pipelines_with_read_depth, minimal_read_depth_requirements

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
    'CRISPRi followed by RNA-seq'
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
    'CRISPRi followed by RNA-seq'
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


def audit_experiment_chipseq_control_read_depth(value, system, files_structure):
    # relevant only for ChIP-seq
    if value.get('assay_term_id') != 'OBI:0000716':
        return

    if value.get('target') and 'name' in value.get('target'):
        target_name = value['target']['name']
        target_investigated_as = value['target']['investigated_as']
        if target_name not in ['Control-human', 'Control-mouse']:
            for alignment_file in files_structure.get('alignments').values():
                # initially was for file award
                if not alignment_file.get('award') or \
                    alignment_file.get('award')['rfa'] not in [
                        'ENCODE3',
                        'ENCODE4',
                        'ENCODE2-Mouse',
                        'ENCODE2',
                        'ENCODE',
                        'Roadmap']:
                    continue
                if alignment_file.get('lab') not in ['/labs/encode-processing-pipeline/']:
                    continue
                derived_from_files = list(
                    get_derived_from_files_set([alignment_file], files_structure, 'fastq', True))
                if not derived_from_files:
                    continue
                control_bam = get_control_bam(
                    alignment_file,
                    'ChIP-seq read mapping',
                    derived_from_files,
                    files_structure)
                if control_bam is not False:
                    control_depth = get_chip_seq_bam_read_depth(control_bam)
                    control_target = get_target_name(derived_from_files)
                    if control_depth is not False and control_target is not False:
                        yield from check_control_read_depth_standards(
                            control_bam,
                            control_depth,
                            control_target,
                            True,
                            target_name,
                            target_investigated_as)
    return


def check_control_read_depth_standards(value,
                                       read_depth,
                                       target_name,
                                       is_control_file,
                                       control_to_target,
                                       target_investigated_as):
    marks = pipelines_with_read_depth['ChIP-seq read mapping']
    # treat this file as control_bam - raising insufficient control read depth
    if is_control_file is True:
        if target_name not in ['Control-human', 'Control-mouse']:
            detail = 'Control alignment file {} '.format(value['@id']) + \
                     'has a target {} that is neither '.format(target_name) + \
                     'Control-human nor Control-mouse.'
            yield AuditFailure('inconsistent target of control experiment', detail, level='WARNING')
            return

        if control_to_target == 'empty':
            return

        # control_to_target in broad_peaks_targets:
        elif 'broad histone mark' in target_investigated_as:
            if 'assembly' in value:
                detail = 'Control alignment file {} mapped to {} assembly has {} '.format(
                    value['@id'],
                    value['assembly'],
                    read_depth) + \
                    'usable fragments. ' + \
                    'The minimum ENCODE standard for a control of ChIP-seq assays targeting broad ' + \
                    'histone mark {} '.format(control_to_target) + \
                    'is 35 million usable fragments, the recommended number of usable ' + \
                    'fragments is > 45 million. (See /data-standards/chip-seq/ )'
            else:
                detail = 'Control alignment file {} has {} '.format(
                    value['@id'],
                    read_depth) + \
                    'usable fragments. ' + \
                    'The minimum ENCODE standard for a control of ChIP-seq assays targeting broad ' + \
                    'histone mark {} '.format(control_to_target) + \
                    'is 35 million usable fragments, the recommended number of usable ' + \
                    'fragments is > 45 million. (See /data-standards/chip-seq/ )'
            if read_depth >= marks['broad']['minimal'] and read_depth < marks['broad']['recommended']:
                yield AuditFailure('control low read depth', detail, level='WARNING')
            elif read_depth >= marks['broad']['low'] and read_depth < marks['broad']['minimal']:
                yield AuditFailure('control insufficient read depth', detail, level='NOT_COMPLIANT')
            elif read_depth < marks['broad']['low']:
                yield AuditFailure('control extremely low read depth', detail, level='ERROR')
        elif 'narrow histone mark' in target_investigated_as:  # else:
            if 'assembly' in value:
                detail = 'Control alignment file {} mapped to {} assembly has {} '.format(
                    value['@id'],
                    value['assembly'],
                    read_depth) + \
                    'usable fragments. ' + \
                    'The minimum ENCODE standard for a control of ChIP-seq assays targeting narrow ' + \
                    'histone mark {} '.format(control_to_target) + \
                    'is 10 million usable fragments, the recommended number of usable ' + \
                    'fragments is > 20 million. (See /data-standards/chip-seq/ )'
            else:
                detail = 'Control alignment file {} has {} '.format(
                    value['@id'],
                    read_depth) + \
                    'usable fragments. ' + \
                    'The minimum ENCODE standard for a control of ChIP-seq assays targeting narrow ' + \
                    'histone mark {} '.format(control_to_target) + \
                    'is 10 million usable fragments, the recommended number of usable ' + \
                    'fragments is > 20 million. (See /data-standards/chip-seq/ )'
            if read_depth >= marks['narrow']['minimal'] and read_depth < marks['narrow']['recommended']:
                yield AuditFailure('control low read depth', detail, level='WARNING')
            elif read_depth >= marks['narrow']['low'] and read_depth < marks['narrow']['minimal']:
                yield AuditFailure('control insufficient read depth', detail, level='NOT_COMPLIANT')
            elif read_depth < marks['narrow']['low']:
                yield AuditFailure('control extremely low read depth', detail, level='ERROR')
        else:
            if 'assembly' in value:
                detail = 'Control alignment file {} mapped to {} assembly has {} '.format(
                    value['@id'],
                    value['assembly'],
                    read_depth) + \
                    'usable fragments. ' + \
                    'The minimum ENCODE standard for a control of ChIP-seq assays targeting ' + \
                    '{} and investigated as a transcription factor '.format(control_to_target) + \
                    'is 10 million usable fragments, the recommended number of usable ' + \
                    'fragments is > 20 million. (See /data-standards/chip-seq/ )'
            else:
                detail = 'Control alignment file {} has {} '.format(
                    value['@id'],
                    read_depth) + \
                    'usable fragments. ' + \
                    'The minimum ENCODE standard for a control of ChIP-seq assays targeting ' + \
                    '{} and investigated as a transcription factor '.format(control_to_target) + \
                    'is 10 million usable fragments, the recommended number of usable ' + \
                    'fragments is > 20 million. (See /data-standards/chip-seq/ )'
            if read_depth >= marks['TF']['minimal'] and read_depth < marks['TF']['recommended']:
                yield AuditFailure('control low read depth', detail, level='WARNING')
            elif read_depth >= marks['TF']['low'] and read_depth < marks['TF']['minimal']:
                yield AuditFailure('control insufficient read depth', detail, level='NOT_COMPLIANT')
            elif read_depth < marks['TF']['low']:
                yield AuditFailure('control extremely low read depth', detail, level='ERROR')
    return


def audit_experiment_mixed_libraries(value, system, excluded_types):
    '''
    Experiments should not have mixed libraries nucleic acids
    '''
    if value['status'] in ['deleted', 'replaced']:
        return

    if 'replicates' not in value:
        return

    nucleic_acids = set()

    for rep in value['replicates']:
        if rep.get('status') not in excluded_types and \
           'library' in rep and rep['library'].get('status') not in excluded_types:
            if 'nucleic_acid_term_name' in rep['library']:
                nucleic_acids.add(rep['library']['nucleic_acid_term_name'])

    if len(nucleic_acids) > 1:
        detail = 'Experiment {} '.format(value['@id']) + \
                 'contains libraries with mixed nucleic acids {} '.format(
                     nucleic_acids)
        yield AuditFailure('mixed libraries', detail, level='INTERNAL_ACTION')
    return


def audit_experiment_pipeline_assay_details(value, system, files_structure):
    for pipeline in get_pipeline_objects(files_structure.get('original_files').values()):
        if value.get('assay_term_name') not in pipeline['assay_term_names']:
            detail = 'This experiment ' + \
                'contains file(s) associated with ' + \
                'pipeline {} '.format(pipeline['@id']) + \
                'which assay_term_names list does not include experiments\'s assay_term_name.'
            yield AuditFailure('inconsistent assay_term_name', detail, level='INTERNAL_ACTION')
    return


# def audit_experiment_missing_processed_files(value, system): removed from v54


def audit_experiment_missing_unfiltered_bams(value, system, files_structure):
    if value.get('assay_term_id') != 'OBI:0000716':  # not a ChIP-seq
        return

    # if there are no bam files - we don't know what pipeline, exit
    if len(files_structure.get('alignments').values()) == 0:
        return

    if 'ChIP-seq read mapping' in get_pipeline_titles(
            get_pipeline_objects(files_structure.get('alignments').values())):
        for filtered_file in files_structure.get('alignments').values():
            if has_only_raw_files_in_derived_from(filtered_file, files_structure) and \
               has_no_unfiltered(filtered_file,
                                 files_structure.get('unfiltered_alignments').values()):

                detail = 'Experiment {} contains biological replicate '.format(value['@id']) + \
                         '{} '.format(filtered_file['biological_replicates']) + \
                         'with a filtered alignments file {}, mapped to '.format(
                             filtered_file['@id']) + \
                         'a {} assembly, '.format(filtered_file['assembly']) + \
                         'but has no unfiltered alignments file.'
                yield AuditFailure('missing unfiltered alignments', detail, level='INTERNAL_ACTION')
    return


def audit_experiment_with_uploading_files(value, system, files_structure):
    if files_structure.get('original_files'):
        for file_object in files_structure.get('original_files').values():
            category = None
            if file_object['status'] in ['upload failed', 'content error']:
                category = 'file validation error'
            elif file_object['status'] == 'uploading':
                category = 'file in uploading state'
            if category:
                detail = ('Experiment {} contains a file {} '
                          'with the status {}.'.format(value['@id'],
                                                       file_object['@id'],
                                                       file_object['status']))
                yield AuditFailure(category, detail, level='WARNING')

    return


def audit_experiment_out_of_date_analysis(value, system, files_structure):
    valid_assay_term_names = [
        'ChIP-seq',
        'DNase-seq',
        'genetic modification followed by DNase-seq',
    ]
    assay_name = value['assay_term_name']
    if assay_name not in valid_assay_term_names:
        return

    if len(files_structure.get('alignments').values()) == 0 and \
       len(files_structure.get('unfiltered_alignments').values()) == 0 and \
       len(files_structure.get('transcriptome_alignments').values()) == 0:
        return  # probably needs pipeline, since there are no processed files

    file_types = ['alignments', 'unfiltered_alignments',
                  'transcriptome_alignments']
    for file_type in file_types:
        for bam_file in files_structure.get(file_type).values():
            if bam_file.get('lab') == '/labs/encode-processing-pipeline/' and bam_file.get('derived_from'):  
                if is_outdated_bams_replicate(bam_file, files_structure, assay_name):
                    assembly_detail = ' '
                    if bam_file.get('assembly'):
                        assembly_detail = ' for {} assembly '.format(
                            bam_file['assembly'])
                    detail = 'Experiment {} '\
                             'alignment file {}{}'\
                             'is out of date.'.format(
                                value['@id'],
                                bam_file['@id'],
                                assembly_detail)
                    yield AuditFailure('out of date analysis', detail, level='INTERNAL_ACTION')
    return


def audit_experiment_standards_dispatcher(value, system, files_structure):
    if not check_award_condition(value, ['ENCODE4',
                                         'ENCODE3',
                                         'ENCODE2-Mouse',
                                         'ENCODE2',
                                         'ENCODE',
                                         'Roadmap']):
        return
    '''
    Dispatcher function that will redirect to other functions that would
    deal with specific assay types standards
    '''
    if value.get('status') in ['revoked', 'deleted', 'replaced']:
        return
    if value.get('assay_term_name') not in ['DNase-seq', 'RAMPAGE', 'RNA-seq', 'ChIP-seq', 'CAGE',
                                            'shRNA knockdown followed by RNA-seq',
                                            'siRNA knockdown followed by RNA-seq',
                                            'CRISPRi followed by RNA-seq',
                                            'CRISPR genome editing followed by RNA-seq',
                                            'single cell isolation followed by RNA-seq',
                                            'whole-genome shotgun bisulfite sequencing',
                                            'genetic modification followed by DNase-seq']:
        return
    if not value.get('original_files'):
        return
    if 'replicates' not in value:
        return

    num_bio_reps = set()
    for rep in value['replicates']:
        num_bio_reps.add(rep['biological_replicate_number'])

    if len(num_bio_reps) < 1:
        return

    organism_name = get_organism_name(
        value['replicates'], files_structure.get('excluded_types'))  # human/mouse
    if organism_name == 'human':
        desired_assembly = 'GRCh38'
        desired_annotation = 'V24'
    else:
        if organism_name == 'mouse':
            desired_assembly = 'mm10'
            desired_annotation = 'M4'
        else:
            return

    standards_version = 'ENC3'

    if value['assay_term_name'] in ['DNase-seq', 'genetic modification followed by DNase-seq']:

        yield from check_experiment_dnase_seq_standards(
            value,
            files_structure,
            desired_assembly,
            desired_annotation,
            ' /data-standards/dnase-seq/ ')
        return

    if value['assay_term_name'] in ['RAMPAGE', 'RNA-seq', 'CAGE',
                                    'shRNA knockdown followed by RNA-seq',
                                    'siRNA knockdown followed by RNA-seq',
                                    'CRISPRi followed by RNA-seq',
                                    'CRISPR genome editing followed by RNA-seq',
                                    'single cell isolation followed by RNA-seq']:
        yield from check_experiment_rna_seq_standards(
            value,
            files_structure,
            desired_assembly,
            desired_annotation,
            standards_version)
        return

    if value['assay_term_name'] == 'ChIP-seq':
        yield from check_experiment_chip_seq_standards(
            value,
            files_structure,
            standards_version)

    if standards_version == 'ENC3' and \
            value['assay_term_name'] == 'whole-genome shotgun bisulfite sequencing':

        yield from check_experiment_wgbs_encode3_standards(
            value,
            files_structure,
            organism_name,
            desired_assembly)
        return


def audit_modERN_experiment_standards_dispatcher(value, system, files_structure):

    if not check_award_condition(value, ['modERN']):
        return
    '''
    Dispatcher function that will redirect to other functions that would
    deal with specific assay types standards. This version is for the modERN project
    '''

    if value['status'] in ['revoked', 'deleted', 'replaced']:
        return
    if value.get('assay_term_name') != 'ChIP-seq':
        return
    if not files_structure.get('original_files').values():
        return
    if 'replicates' not in value:
        return

    yield from check_experiment_chip_seq_standards(value,
                                                   files_structure,
                                                   'modERN')
    return


def check_experiment_dnase_seq_standards(experiment,
                                         files_structure,
                                         desired_assembly,
                                         desired_annotation,
                                         link_to_standards):
    fastq_files = files_structure.get('fastq_files').values()
    alignment_files = files_structure.get('alignments').values()
    signal_files = files_structure.get('signal_files').values()

    pipeline_title = scanFilesForPipelineTitle_not_chipseq(
        alignment_files,
        ['GRCh38', 'mm10'],
        ['DNase-HS pipeline single-end - Version 2',
         'DNase-HS pipeline paired-end - Version 2'])
    if pipeline_title is False:
        return
    for f in fastq_files:
        yield from check_file_read_length_rna(
            f, 36,
            pipeline_title,
            link_to_standards)

    pipelines = get_pipeline_objects(alignment_files)

    if pipelines is not None and len(pipelines) > 0:
        samtools_flagstat_metrics = get_metrics(alignment_files,
                                                'SamtoolsFlagstatsQualityMetric',
                                                desired_assembly)

        if samtools_flagstat_metrics is not None and \
                len(samtools_flagstat_metrics) > 0:
            for metric in samtools_flagstat_metrics:
                if 'mapped' in metric and 'quality_metric_of' in metric:
                    alignment_file = files_structure.get(
                        'alignments')[metric['quality_metric_of'][0]]
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
                        yield AuditFailure('low read depth', detail, level='WARNING')
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

        alignments_assemblies = {}
        for alignment_file in alignment_files:
            if 'assembly' in alignment_file:
                alignments_assemblies[alignment_file['accession']
                                      ] = alignment_file['assembly']

        # duplication rate audit was removed from v54

        signal_assemblies = {}
        for signal_file in signal_files:
            if 'assembly' in signal_file:
                signal_assemblies[signal_file['accession']
                                  ] = signal_file['assembly']

        hotspot_quality_metrics = get_metrics(alignment_files,
                                              'HotspotQualityMetric',
                                              desired_assembly)
        if hotspot_quality_metrics is not None and \
           len(hotspot_quality_metrics) > 0:
            for metric in hotspot_quality_metrics:
                if "SPOT1 score" in metric:
                    file_names = []
                    for f in metric['quality_metric_of']:
                        file_names.append(f.split('/')[2])
                    file_names_string = str(file_names).replace('\'', ' ')
                    detail = "Signal Portion of Tags (SPOT) is a measure of enrichment, " + \
                             "analogous to the commonly used fraction of reads in peaks metric. " + \
                             "ENCODE processed alignment files {} ".format(file_names_string) + \
                             "produced by {} ".format(pipelines[0]['title']) + \
                             "( {} ) ".format(pipelines[0]['@id']) + \
                             assemblies_detail(extract_assemblies(alignments_assemblies, file_names)) + \
                             "have a SPOT1 score of {0:.2f}. ".format(metric["SPOT1 score"]) + \
                             "According to ENCODE standards, " + \
                             "SPOT1 score of 0.4 or higher is considered a product of high quality " + \
                             "data. " + \
                             "Any sample with a SPOT1 score <0.3 should be targeted for replacement " + \
                             "with a higher quality sample, and a " + \
                             "SPOT1 score of 0.25 is considered minimally acceptable " + \
                             "for rare and hard to find primary tissues. (See {} )".format(
                                 link_to_standards)

                    if 0.25 <= metric["SPOT1 score"] < 0.4:
                        yield AuditFailure('low spot score', detail, level='WARNING')
                    elif metric["SPOT1 score"] < 0.25:
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
                        file_names.append(f.split('/')[2])
                    file_names_string = str(file_names).replace('\'', ' ')
                    detail = 'Replicate concordance in DNase-seq expriments is measured by ' + \
                        'calculating the Pearson correlation between signal quantification ' + \
                        'of the replicates. ' + \
                        'ENCODE processed signal files {} '.format(file_names_string) + \
                        'produced by {} '.format(pipelines[0]['title']) + \
                        '( {} ) '.format(pipelines[0]['@id']) + \
                        assemblies_detail(extract_assemblies(signal_assemblies, file_names)) + \
                        'have a Pearson correlation of {0:.2f}. '.format(metric['Pearson correlation']) + \
                        'According to ENCODE standards, in an {} '.format(experiment['replication_type']) + \
                        'assay a Pearson correlation value > {} '.format(threshold) + \
                        'is recommended. (See {} )'.format(
                            link_to_standards)

                    if metric['Pearson correlation'] < threshold:
                        yield AuditFailure('insufficient replicate concordance',
                                           detail, level='NOT_COMPLIANT')
    return


def check_experiment_rna_seq_standards(value,
                                       files_structure,
                                       desired_assembly,
                                       desired_annotation,
                                       standards_version):

    fastq_files = files_structure.get('fastq_files').values()
    alignment_files = files_structure.get('alignments').values()
    gene_quantifications = files_structure.get(
        'gene_quantifications_files').values()

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
        yield from check_file_read_length_rna(f, 50,
                                              pipeline_title,
                                              standards_links[pipeline_title])

        yield from check_file_platform(f, ['OBI:0002024', 'OBI:0000696'])

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
        yield from check_experiment_cage_rampage_standards(
            value,
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
            standards_links[pipeline_title])
    elif pipeline_title in ['Small RNA-seq single-end pipeline']:
        upper_limit = 30000000
        medium_limit = 20000000
        lower_limit = 1000000
        yield from check_experiment_small_rna_standards(
            value,
            fastq_files,
            alignment_files,
            pipeline_title,
            gene_quantifications,
            desired_assembly,
            desired_annotation,
            upper_limit,
            medium_limit,
            lower_limit,
            standards_links[pipeline_title])

    elif pipeline_title in ['RNA-seq of long RNAs (paired-end, stranded)',
                            'RNA-seq of long RNAs (single-end, unstranded)']:
        upper_limit = 30000000
        medium_limit = 20000000
        lower_limit = 1000000
        yield from check_experiment_long_rna_standards(
            value,
            fastq_files,
            alignment_files,
            pipeline_title,
            gene_quantifications,
            desired_assembly,
            desired_annotation,
            upper_limit,
            medium_limit,
            lower_limit,
            standards_links[pipeline_title])
    return


def check_experiment_wgbs_encode3_standards(experiment,
                                            files_structure,
                                            organism_name,
                                            desired_assembly):

    alignment_files = files_structure.get('alignments').values()
    fastq_files = files_structure.get('fastq_files').values()
    cpg_quantifications = files_structure.get('cpg_quantifications').values()

    if fastq_files == []:
        return

    yield from check_wgbs_read_lengths(fastq_files, organism_name, 130, 100)

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

    bismark_metrics = get_metrics(
        cpg_quantifications, 'BismarkQualityMetric', desired_assembly)
    cpg_metrics = get_metrics(
        cpg_quantifications, 'CpgCorrelationQualityMetric', desired_assembly)

    samtools_metrics = get_metrics(cpg_quantifications,
                                   'SamtoolsFlagstatsQualityMetric',
                                   desired_assembly)

    yield from check_wgbs_coverage(
        samtools_metrics,
        pipeline_title,
        min(read_lengths),
        organism_name,
        get_pipeline_objects(alignment_files))

    yield from check_wgbs_pearson(cpg_metrics, 0.8, pipeline_title)

    yield from check_wgbs_lambda(bismark_metrics, 1, pipeline_title)

    return


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
    return


def check_experiment_chip_seq_standards(
        experiment,
        files_structure,
        standards_version):

    fastq_files = files_structure.get('fastq_files').values()
    alignment_files = files_structure.get('alignments').values()
    idr_peaks_files = files_structure.get('optimal_idr_peaks').values()

    upper_limit_read_length = 50
    medium_limit_read_length = 36
    lower_limit_read_length = 26
    for f in fastq_files:
        yield from check_file_read_length_chip(
            f,
            upper_limit_read_length,
            medium_limit_read_length,
            lower_limit_read_length)

    pipeline_title = scanFilesForPipelineTitle_yes_chipseq(
        alignment_files,
        ['ChIP-seq read mapping',
            'Transcription factor ChIP-seq pipeline (modERN)']
    )
    if pipeline_title is False:
        return

    for f in alignment_files:
        target = get_target(experiment)
        if target is False:
            return

        read_depth = get_file_read_depth_from_alignment(f, target, 'ChIP-seq')

        yield from check_file_chip_seq_read_depth(f, target, read_depth, standards_version)
        yield from check_file_chip_seq_library_complexity(f)
    if 'replication_type' not in experiment or experiment['replication_type'] == 'unreplicated':
        return

    idr_metrics = get_metrics(idr_peaks_files, 'IDRQualityMetric')
    yield from check_idr(idr_metrics, 2, 2)
    return


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

    yield from check_experiment_ERCC_spikeins(experiment, pipeline_title)

    pipelines = get_pipeline_objects(alignment_files)
    if pipelines is not None and len(pipelines) > 0:
        for f in alignment_files:

            if 'assembly' in f and f['assembly'] == desired_assembly:

                read_depth = get_file_read_depth_from_alignment(f,
                                                                get_target(
                                                                    experiment),
                                                                'long RNA')

                if experiment['assay_term_name'] in ['shRNA knockdown followed by RNA-seq',
                                                     'siRNA knockdown followed by RNA-seq',
                                                     'CRISPRi followed by RNA-seq',
                                                     'CRISPR genome editing followed by RNA-seq']:
                    yield from check_file_read_depth(
                        f, read_depth, 10000000, 10000000, 1000000,
                        experiment['assay_term_name'],
                        pipeline_title,
                        pipelines[0],
                        standards_link)
                elif experiment['assay_term_name'] in ['single cell isolation followed by RNA-seq']:
                    yield from check_file_read_depth(
                        f, read_depth, 5000000, 5000000, 500000,
                        experiment['assay_term_name'],
                        pipeline_title,
                        pipelines[0],
                        standards_link)
                else:
                    yield from check_file_read_depth(
                        f, read_depth,
                        upper_limit_read_depth,
                        medium_limit_read_depth,
                        lower_limit_read_depth,
                        experiment['assay_term_name'],
                        pipeline_title,
                        pipelines[0],
                        standards_link)

    if 'replication_type' not in experiment:
        return

    mad_metrics = get_metrics(gene_quantifications,
                              'MadQualityMetric',
                              desired_assembly,
                              desired_annotation)

    if experiment['assay_term_name'] != 'single cell isolation followed by RNA-seq':
        yield from check_spearman(
            mad_metrics, experiment['replication_type'],
            0.9, 0.8, pipeline_title)
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
                                                                get_target(
                                                                    experiment),
                                                                'small RNA')

                yield from check_file_read_depth(
                    f, read_depth,
                    upper_limit_read_depth,
                    medium_limit_read_depth,
                    lower_limit_read_depth,
                    experiment['assay_term_name'],
                    pipeline_title,
                    pipelines[0],
                    standards_link)

    if 'replication_type' not in experiment:
        return

    mad_metrics = get_metrics(gene_quantifications,
                              'MadQualityMetric',
                              desired_assembly,
                              desired_annotation)

    yield from check_spearman(
        mad_metrics, experiment['replication_type'],
        0.9, 0.8, 'Small RNA-seq single-end pipeline')
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
                                                                get_target(
                                                                    experiment),
                                                                experiment['assay_term_name'])
                yield from check_file_read_depth(
                    f, read_depth,
                    upper_limit_read_depth,
                    middle_limit_read_depth,
                    lower_limit_read_depth,
                    experiment['assay_term_name'],
                    pipeline_title,
                    pipelines[0],
                    standards_link)

    if 'replication_type' not in experiment:
        return

    mad_metrics = get_metrics(gene_quantifications,
                              'MadQualityMetric',
                              desired_assembly,
                              desired_annotation)

    yield from check_spearman(
        mad_metrics, experiment['replication_type'],
        0.9, 0.8, 'RAMPAGE (paired-end, stranded)')
    return


def check_idr(metrics, rescue, self_consistency):
    for m in metrics:
        if 'rescue_ratio' in m and 'self_consistency_ratio' in m:
            rescue_r = m['rescue_ratio']
            self_r = m['self_consistency_ratio']
            if rescue_r > rescue and self_r > self_consistency:
                file_names = []
                for f in m['quality_metric_of']:
                    file_names.append(f)
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
                    file_names.append(f)
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
    return


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
    return


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
                if s.get('files'):
                    for f in s.get('files'):
                        if (
                                ('/files/ENCFF001RTP/' == f) or
                                ('/files/ENCFF001RTO/' == f and
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
    return


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
                    file_names.append(f)
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
    return


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

    pbc1_detail = 'PBC1 (PCR Bottlenecking Coefficient 1, M1/M_distinct) ' + \
                  'is the ratio of the number of genomic ' + \
                  'locations where exactly one read maps uniquely (M1) to the number of ' + \
                  'genomic locations where some reads map (M_distinct). ' + \
                  'A PBC1 value in the range 0 - 0.5 is severe bottlenecking, 0.5 - 0.8 ' + \
                  'is moderate bottlenecking, 0.8 - 0.9 is mild bottlenecking, and > 0.9 ' + \
                  'is no bottlenecking. PBC1 value > 0.9 is recommended, but > 0.8 is ' + \
                  'acceptable. '

    pbc2_detail = 'PBC2 (PCR Bottlenecking Coefficient 2, M1/M2) is the ratio of the number of ' + \
                  'genomic locations where exactly one read maps uniquely (M1) to the number of genomic ' + \
                  'locations where two reads map uniquely (M2). ' + \
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
                    'was generated from a library with NRF value of {0:.2f}.'.format(
                        NRF_value)
                yield AuditFailure('moderate library complexity', detail,
                                   level='WARNING')
        if 'PBC1' in metric:
            PBC1_value = float(metric['PBC1'])
            if PBC1_value < 0.5:
                detail = pbc1_detail + 'ENCODE processed alignment file {} '.format(
                    alignment_file['@id']) + \
                    'was generated from a library with PBC1 value of {0:.2f}.'.format(
                        PBC1_value)
                yield AuditFailure('severe bottlenecking', detail,
                                   level='NOT_COMPLIANT')
            elif PBC1_value >= 0.5 and PBC1_value < 0.9:
                detail = pbc1_detail + 'ENCODE processed alignment file {} '.format(
                    alignment_file['@id']) + \
                    'was generated from a library with PBC1 value of {0:.2f}.'.format(
                        PBC1_value)
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
                    'was generated from a library with PBC2 value of {0:.2f}.'.format(
                        PBC2_value)
                yield AuditFailure('severe bottlenecking', detail,
                                   level='NOT_COMPLIANT')
            elif PBC2_value >= 1 and PBC2_value < 10:
                detail = pbc2_detail + 'ENCODE processed alignment file {} '.format(
                    alignment_file['@id']) + \
                    'was generated from a library with PBC2 value of {0:.2f}.'.format(
                        PBC2_value)
                yield AuditFailure('mild to moderate bottlenecking', detail,
                                   level='WARNING')
    return


def check_wgbs_coverage(samtools_metrics,
                        pipeline_title,
                        read_length,
                        organism,
                        pipeline_objects):
    for m in samtools_metrics:
        if 'mapped' in m:
            mapped_reads = m['mapped']
            if organism == 'mouse':
                coverage = float(mapped_reads * read_length) / 2800000000.0
            elif organism == 'human':
                coverage = float(mapped_reads * read_length) / 3300000000.0
            detail = ('Replicate of experiment processed by {} ( {} ) '
                      'has a coverage of {}X. '
                      'The minimum ENCODE standard coverage for each replicate in '
                      'a WGBS assay is 25X and the recommended value '
                      'is > 30X (See /data-standards/wgbs/ )').format(
                          pipeline_title,
                          pipeline_objects[0]['@id'],
                          int(coverage))
            if coverage < 5:
                yield AuditFailure('extremely low coverage',
                                   detail,
                                   level='ERROR')
            elif coverage < 25:
                yield AuditFailure('insufficient coverage',
                                   detail,
                                   level='NOT_COMPLIANT')
            elif coverage < 30:
                yield AuditFailure('low coverage',
                                   detail,
                                   level='WARNING')
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
    return


def check_wgbs_lambda(bismark_metrics, threshold, pipeline_title):
    for metric in bismark_metrics:
        cpg_string = metric.get('lambda C methylated in CpG context')
        chg_string = metric.get('lambda C methylated in CHG context')
        chh_string = metric.get('lambda C methylated in CHH context')
        if (cpg_string and chg_string and chh_string):
            lambdaCpG = float(cpg_string[:-1])
            lambdaCHG = float(chg_string[:-1])
            lambdaCHH = float(chh_string[:-1])
            if (lambdaCpG > 1 and lambdaCHG > 1 and lambdaCHH > 1) or \
            (((lambdaCpG * 0.25) + (lambdaCHG * 0.25) + (lambdaCHH * 0.5)) > 1):
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
        ['ChIP-seq read mapping',
         'Transcription factor ChIP-seq pipeline (modERN)'])

    if pipeline_title is False:
        return
    pipeline_objects = get_pipeline_objects([file_to_check])

    marks = pipelines_with_read_depth['ChIP-seq read mapping']
    modERN_cutoff = pipelines_with_read_depth[
        'Transcription factor ChIP-seq pipeline (modERN)']
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
            if read_depth >= marks['narrow']['recommended'] and read_depth < marks['broad']['recommended']:
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
                yield AuditFailure('insufficient read depth for broad peaks control', detail, level='INTERNAL_ACTION')
            if read_depth < marks['narrow']['recommended']:
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
                if read_depth >= marks['narrow']['minimal']:
                    yield AuditFailure('low read depth', detail, level='WARNING')
                elif read_depth >= marks['narrow']['low'] and read_depth < marks['narrow']['minimal']:
                    yield AuditFailure('insufficient read depth',
                                       detail, level='NOT_COMPLIANT')
                else:
                    yield AuditFailure('extremely low read depth',
                                       detail, level='ERROR')
    elif 'broad histone mark' in target_investigated_as and \
            standards_version != 'modERN':  # target_name in broad_peaks_targets:
        pipeline_object = get_pipeline_by_name(
            pipeline_objects, 'ChIP-seq read mapping')
        if pipeline_object:
            if target_name in ['H3K9me3-human', 'H3K9me3-mouse']:
                if read_depth < marks['broad']['recommended']:
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
                            'a broad histone mark is 35 million mapped reads. ' + \
                            'The recommended value is > 45 million, but > 35 million is ' + \
                            'acceptable. (See /data-standards/chip-seq/ )'
                    else:
                        detail = 'Alignment file {} '.format(file_to_check['@id']) + \
                            'produced by {} '.format(pipeline_object['title']) + \
                            'pipeline ( {} ) '.format(pipeline_object['@id']) + \
                            'has {} '.format(read_depth) + \
                            'mapped reads. ' + \
                            'The minimum ENCODE standard for each replicate in a ChIP-seq ' + \
                            'experiment targeting {} and investigated as '.format(target_name) + \
                            'a broad histone mark is 35 million mapped reads. ' + \
                            'The recommended value is > 45 million, but > 35 million is ' + \
                            'acceptable. (See /data-standards/chip-seq/ )'
                    if read_depth >= marks['broad']['minimal']:
                        yield AuditFailure('low read depth',
                                           detail, level='WARNING')
                    elif read_depth >= 100 and read_depth < marks['broad']['minimal']:
                        yield AuditFailure('insufficient read depth',
                                           detail, level='NOT_COMPLIANT')
                    elif read_depth < 100:
                        yield AuditFailure('extremely low read depth',
                                           detail, level='ERROR')
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
                        'The recommended value is > 45 million, but > 35 million is ' + \
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
                        'The recommended value is > 45 million, but > 35 million is ' + \
                        'acceptable. (See /data-standards/chip-seq/ )'

                if read_depth >= marks['broad']['minimal'] and read_depth < marks['broad']['recommended']:
                    yield AuditFailure('low read depth',
                                       detail, level='WARNING')
                elif read_depth < marks['broad']['minimal'] and read_depth >= marks['broad']['low']:
                    yield AuditFailure('insufficient read depth',
                                       detail, level='NOT_COMPLIANT')
                elif read_depth < marks['broad']['low']:
                    yield AuditFailure('extremely low read depth',
                                       detail, level='ERROR')
    elif 'narrow histone mark' in target_investigated_as and \
            standards_version != 'modERN':
        pipeline_object = get_pipeline_by_name(
            pipeline_objects, 'ChIP-seq read mapping')
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
            if read_depth >= marks['narrow']['minimal'] and read_depth < marks['narrow']['recommended']:
                yield AuditFailure('low read depth', detail, level='WARNING')
            elif read_depth < marks['narrow']['minimal'] and read_depth >= marks['narrow']['low']:
                yield AuditFailure('insufficient read depth',
                                   detail, level='NOT_COMPLIANT')
            elif read_depth < marks['narrow']['low']:
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
                                                   'ChIP-seq read mapping')
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
                if read_depth >= marks['TF']['minimal'] and read_depth < marks['TF']['recommended']:
                    yield AuditFailure('low read depth', detail, level='WARNING')
                elif read_depth < marks['TF']['minimal'] and read_depth >= marks['TF']['low']:
                    yield AuditFailure('insufficient read depth',
                                       detail, level='NOT_COMPLIANT')
                elif read_depth < marks['TF']['low']:
                    yield AuditFailure('extremely low read depth',
                                       detail, level='ERROR')
    return


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
        elif read_depth >= lower_threshold and read_depth < middle_threshold:
            yield AuditFailure('insufficient read depth', detail,
                               level='NOT_COMPLIANT')
        elif read_depth < lower_threshold:
            yield AuditFailure('extremely low read depth', detail,
                               level='ERROR')
    return


def check_file_platform(file_to_check, excluded_platforms):
    if 'platform' not in file_to_check:
        return
    elif file_to_check['platform'] in excluded_platforms:
        detail = 'Reads file {} has not compliant '.format(file_to_check['@id']) + \
                 'platform (SOLiD) {}.'.format(file_to_check['platform'])
        yield AuditFailure('not compliant platform', detail, level='WARNING')
    return


def check_file_read_length_chip(file_to_check,
                                upper_threshold_length,
                                medium_threshold_length,
                                lower_threshold_length):
    if 'read_length' not in file_to_check:
        detail = 'Reads file {} missing read_length'.format(
            file_to_check['@id'])
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
        detail = 'Reads file {} missing read_length'.format(
            file_to_check['@id'])
        yield AuditFailure('missing read_length', detail, level='NOT_COMPLIANT')
        return
    if file_to_check.get('read_length') < threshold_length:
        detail = 'Fastq file {} '.format(file_to_check['@id']) + \
                 'has read length of {}bp. '.format(file_to_check.get('read_length')) + \
                 'ENCODE uniform processing pipelines ({}) '.format(pipeline_title) + \
                 'require sequencing reads to be at least {}bp long. (See {} )'.format(
                     threshold_length,
                     standard_link)

        yield AuditFailure('insufficient read length', detail,
                           level='NOT_COMPLIANT')
    return


def audit_experiment_internal_tag(value, system, excluded_types):

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
                                 'list of internal_tags {}.'.format(
                                     experimental_tags)
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
    return


def audit_experiment_geo_submission(value, system, excluded_types):
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


def audit_experiment_status(value, system, files_structure):
    if value['status'] not in ['started']:
        return
    assay_term_name = value.get('assay_term_name')
    if assay_term_name not in minimal_read_depth_requirements:
        return
    award_rfa = value.get('award', {}).get('rfa')
    if award_rfa == 'modERN':
        return
    if award_rfa == 'modENCODE' and assay_term_name != 'ChIP-seq':
        return
    replicates = value.get('replicates')
    if not replicates:
        return
    replicates_set = set()
    submitted_replicates = set()
    replicates_reads = {}
    bio_rep_reads = {}
    replicates_bio_index = {}
    for replicate in replicates:
        if replicate.get('status') not in ['deleted']:
            replicate_id = replicate.get('@id')
            replicates_set.add(replicate_id)
            replicates_reads[replicate_id] = 0
            replicates_bio_index[replicate_id] = replicate.get('biological_replicate_number')
            bio_rep_reads[replicates_bio_index[replicate_id]] = 0

    erroneous_status = ['uploading', 'content error', 'upload failed']
    for fastq_file in files_structure.get('fastq_files').values():
        if fastq_file.get('status') not in erroneous_status:
            file_replicate = fastq_file.get('replicate')
            read_count = fastq_file.get('read_count')
            if read_count and file_replicate:
                replicate_id = file_replicate.get('@id')
                submitted_replicates.add(replicate_id)
                if replicate_id in replicates_reads:
                    run_type = fastq_file.get('run_type')
                    if run_type and run_type == 'paired-ended':
                        read_count == read_count/2
                    replicates_reads[replicate_id] += read_count
                    bio_rep_reads[replicates_bio_index[replicate_id]] += read_count


    if replicates_set and not replicates_set - submitted_replicates:
        part_of_detail = 'replicate'
        if award_rfa == 'modENCODE':
            key = 'modENCODE-chip'
        else:
            key = assay_term_name
            if assay_term_name in [
                    'DNase-seq',
                    'genetic modification followed by DNase-seq',
                    'ChIP-seq']:
                replicates_reads = bio_rep_reads
                part_of_detail = 'biological replicate'

        for rep in replicates_reads:
            if replicates_reads[rep] < minimal_read_depth_requirements[key]:
                detail = ('The cumulative number of reads in '
                            '{} {} of experiment {} is {}. That is lower then '
                            'the minimal expected read depth of {} '
                            'for this type of assay.').format(
                                part_of_detail,
                                rep,
                                value['@id'],
                                replicates_reads[rep],
                                minimal_read_depth_requirements[key]
                            )
                yield AuditFailure('low read count',
                                    detail, level='WARNING')


def audit_experiment_consistent_sequencing_runs(value, system, files_structure):
    if value['status'] in ['deleted', 'replaced', 'revoked']:
        return

    if not value.get('replicates'):
        return

    assay_term_name = value.get('assay_term_name')

    if assay_term_name not in [
            'ChIP-seq',
            'DNase-seq',
            'genetic modification followed by DNase-seq']:
        return

    replicate_pairing_statuses = {}
    replicate_read_lengths = {}

    for file_object in files_structure.get('fastq_files').values():
        if 'replicate' in file_object:
            bio_rep_number = file_object['replicate']['biological_replicate_number']

            if 'read_length' in file_object:
                if bio_rep_number not in replicate_read_lengths:
                    replicate_read_lengths[bio_rep_number] = set()
                replicate_read_lengths[bio_rep_number].add(
                    file_object['read_length'])

            # run type consistency is relevant only for ChIP-seq
            if assay_term_name == 'ChIP-seq' and 'run_type' in file_object:
                if bio_rep_number not in replicate_pairing_statuses:
                    replicate_pairing_statuses[bio_rep_number] = set()
                replicate_pairing_statuses[bio_rep_number].add(
                    file_object['run_type'])

    length_threshold = 2
    # different length threshold for DNase-seq and genetic modification followed by DNase-seq
    if value.get("assay_term_id") in ["OBI:0001853", "NTR:0004774"]:
        length_threshold = 9
    for key in replicate_read_lengths:
        if len(replicate_read_lengths[key]) > 1:
            upper_value = max(list(replicate_read_lengths[key]))
            lower_value = min(list(replicate_read_lengths[key]))
            if (upper_value - lower_value) > length_threshold:
                detail = 'Biological replicate {} '.format(key) + \
                         'in experiment {} '.format(value['@id']) + \
                         'has mixed sequencing read lengths {}.'.format(
                             replicate_read_lengths[key])
                yield AuditFailure('mixed read lengths',
                                   detail, level='WARNING')

    keys = list(replicate_read_lengths.keys())

    if len(keys) > 1:
        for index_i in range(len(keys)):
            for index_j in range(index_i + 1, len(keys)):
                i_lengths = list(replicate_read_lengths[keys[index_i]])
                j_lengths = list(replicate_read_lengths[keys[index_j]])

                i_max = max(i_lengths)
                i_min = min(i_lengths)
                j_max = max(j_lengths)
                j_min = min(j_lengths)

                diff_flag = False
                if (i_max - j_min) > length_threshold:
                    diff_flag = True
                if (j_max - i_min) > length_threshold:
                    diff_flag = True

                if diff_flag is True:
                    detail = 'Biological replicate {} '.format(keys[index_i]) + \
                             'in experiment {} '.format(value['@id']) + \
                             'has sequencing read lengths {} '.format(i_lengths) + \
                             ' that differ from replicate {},'.format(keys[index_j]) + \
                             ' which has {} sequencing read lengths.'.format(
                                 j_lengths)
                    yield AuditFailure('mixed read lengths',
                                       detail, level='WARNING')

    # run type consistency is relevant only for ChIP-seq
    if assay_term_name == 'ChIP-seq':  
        for key in replicate_pairing_statuses:
            if len(replicate_pairing_statuses[key]) > 1:
                detail = 'Biological replicate {} '.format(key) + \
                        'in experiment {} '.format(value['@id']) + \
                        'has mixed endedness {}.'.format(
                            replicate_pairing_statuses[key])
                yield AuditFailure('mixed run types',
                                detail, level='WARNING')

        

        keys = list(replicate_pairing_statuses.keys())
        if len(keys) > 1:
            for index_i in range(len(keys)):
                for index_j in range(index_i + 1, len(keys)):
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


def audit_experiment_replicate_with_no_files(value, system, files_structure):
    if 'internal_tags' in value and 'DREAM' in value['internal_tags']:
        return

    if value['status'] in ['deleted', 'replaced', 'revoked']:
        return
    if not value.get('replicates'):
        return

    seq_assay_flag = False
    if value['assay_term_name'] in seq_assays:
        seq_assay_flag = True

    rep_dictionary = {}
    rep_numbers = {}
    excluded_statuses = files_structure.get('excluded_types')
    excluded_statuses += ['deleted', 'replaced']

    for rep in value.get('replicates'):
        if rep['status'] in excluded_statuses:
            continue
        rep_dictionary[rep['@id']] = []
        rep_numbers[rep['@id']] = (rep['biological_replicate_number'],
                                   rep['technical_replicate_number'])

    for file_object in files_structure.get('original_files').values():
        file_replicate = file_object.get('replicate')
        if file_replicate:
            if file_replicate['@id'] in rep_dictionary:
                rep_dictionary[file_replicate['@id']].append(
                    file_object['output_category'])

    audit_level = 'ERROR'

    if check_award_condition(value, ["ENCODE2", "Roadmap",
                                     "modENCODE", "MODENCODE", "ENCODE2-Mouse"]):
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


def audit_experiment_replicated(value, system, excluded_types):
    if not check_award_condition(value, [
            'ENCODE4', 'ENCODE3', 'GGR']):
        return
    '''
    Experiments in ready for review state should be replicated. If not,
    wranglers should check with lab as to why before release.
    '''
    if value['status'] not in ['released', 'ready for review']:
        return
    '''
    Excluding single cell isolation experiments from the replication requirement
    Excluding RNA-bind-and-Seq from the replication requirment
    Excluding genetic modification followed by DNase-seq from the replication requirement
    '''
    if value['assay_term_name'] in ['single cell isolation followed by RNA-seq',
                                    'RNA Bind-n-Seq',
                                    'genetic modification followed by DNase-seq']:
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
        detail = 'This experiment is expected to be replicated, but ' + \
            'contains only one listed biological replicate.'
        yield AuditFailure('unreplicated experiment', detail, level='NOT_COMPLIANT')
    return


def audit_experiment_replicates_with_no_libraries(value, system, excluded_types):
    if value['status'] in ['deleted', 'replaced', 'revoked']:
        return
    if len(value['replicates']) == 0:
        return
    for rep in value['replicates']:
        if rep.get('status') not in excluded_types and 'library' not in rep:
            detail = 'Experiment {} has a replicate {}, that has no library associated with'.format(
                value['@id'],
                rep['@id'])
            yield AuditFailure('replicate with no library', detail, level='ERROR')
    return


def audit_experiment_isogeneity(value, system, excluded_types):
    if value['status'] in ['deleted', 'replaced', 'revoked']:
        return
    if len(value['replicates']) < 2:
        return
    if value.get('replication_type') is None:
        detail = 'In experiment {} the replication_type cannot be determined'.format(
            value['@id'])
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
                biosample_species = biosampleObject.get('organism')
                if biosampleObject.get('donor'):
                    biosample_donor_set.add(
                        biosampleObject.get('donor')['@id'])
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


def audit_experiment_technical_replicates_same_library(value, system, excluded_types):
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
                yield AuditFailure('sequencing runs labeled as technical replicates', detail,
                                   level='INTERNAL_ACTION')
                return
            else:
                biological_replicates_dict[bio_rep_num].append(
                    library['accession'])
    return


def audit_experiment_replicates_biosample(value, system, excluded_types):
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
                    yield AuditFailure('biological replicates with identical biosample',
                                       detail, level='INTERNAL_ACTION')
                    return
                else:
                    biosamples_list.append(biosample['accession'])

            else:
                if biosample['accession'] != biological_replicates_dict[bio_rep_num] and \
                   assay_name != 'single cell isolation followed by RNA-seq':
                    detail = 'Experiment {} has technical replicates \
                              associated with the different biosamples'.format(
                        value['@id'])
                    yield AuditFailure('technical replicates with not identical biosample',
                                       detail, level='ERROR')
                    return
    return


def audit_experiment_documents(value, system, excluded_types):
    if not check_award_condition(value, [
            "ENCODE3", "modERN", "GGR", "ENCODE4",
            "ENCODE", "ENCODE2-Mouse", "Roadmap"]):
        return
    '''
    Experiments should have documents.  Protocol documents or some sort of document.
    '''
    if value['status'] in ['deleted', 'replaced']:
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
        yield AuditFailure('missing documents', detail, level='NOT_COMPLIANT')
    return


def audit_experiment_target(value, system, excluded_types):
    '''
    Certain assay types (ChIP-seq, ...) require valid targets and the replicate's
    antibodies should match.
    '''

    if value['status'] in ['deleted']:
        return

    if value.get('assay_term_name') not in targetBasedAssayList:
        return

    if 'target' not in value:
        detail = '{} experiments require a target'.format(
            value['assay_term_name'])
        yield AuditFailure('missing target', detail, level='ERROR')
        return

    target = value['target']
    if 'control' in target['investigated_as']:
        return

    # Some assays don't need antibodies
    if value['assay_term_name'] in ['RNA Bind-n-Seq',
                                    'shRNA knockdown followed by RNA-seq',
                                    'siRNA knockdown followed by RNA-seq',
                                    'CRISPRi followed by RNA-seq',
                                    'CRISPR genome editing followed by RNA-seq']:
        return

    # Check that target of experiment matches target of antibody
    for rep in value['replicates']:
        if 'antibody' not in rep:
            detail = '{} assays require an antibody specification. '.format(
                value['assay_term_name']) + \
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
                    detail = '{} is not to tagged protein'.format(
                        antibody['@id'])
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
                    antibody_targets_string = str(
                        antibody_targets).replace('\'', '')
                    detail = 'The target of the experiment is {}, '.format(target['name']) + \
                             'but it is not present in the experiment\'s antibody {} '.format(
                                 antibody['@id']) + \
                             'target list {}.'.format(antibody_targets_string)
                    yield AuditFailure('inconsistent target', detail, level='ERROR')
    return


def audit_experiment_control(value, system, excluded_types):
    if not check_award_condition(value, [
            "ENCODE3", "ENCODE4", "modERN", "ENCODE2", "modENCODE",
            "ENCODE", "ENCODE2-Mouse", "Roadmap"]):
        return

    '''
    Certain assay types (ChIP-seq, ...) require possible controls with a matching biosample.
    Of course, controls do not require controls.
    '''

    if value['status'] in ['deleted', 'replaced']:
        return

    # Currently controls are only be required for ChIP-seq
    if value.get('assay_term_name') not in controlRequiredAssayList:
        return

    # single cell RNA-seq in E4 do not require controls (ticket WOLD-6)
    if value.get('assay_term_name') == 'single cell isolation followed by RNA-seq' and \
            check_award_condition(value, ["ENCODE4"]):
        return

    # We do not want controls
    if 'target' in value and 'control' in value['target']['investigated_as']:
        return

    audit_level = 'ERROR'
    if value.get('assay_term_name') in ['CAGE',
                                        'RAMPAGE'] or \
        check_award_condition(value, ["ENCODE2",
                                      "Roadmap",
                                      "modENCODE",
                                      "ENCODE2-Mouse"]):
        audit_level = 'NOT_COMPLIANT'
    if value['possible_controls'] == []:
        detail = 'possible_controls is a list of experiment(s) that can ' + \
                 'serve as analytical controls for a given experiment. ' + \
                 '{} experiments require a value in possible_controls. '.format(
                     value['assay_term_name']) + \
                 'This experiment should be associated with at least one control ' + \
                 'experiment, but has no specified values in the possible_controls list.'
        yield AuditFailure('missing possible_controls', detail, level=audit_level)
        return

    for control in value['possible_controls']:
        if control.get('biosample_term_id') != value.get('biosample_term_id'):
            detail = 'The specified control {} for this experiment is on {}, '.format(
                control['@id'],
                control.get('biosample_term_name')) + \
                'but this experiment is done on {}.'.format(
                    value['biosample_term_name'])
            yield AuditFailure('inconsistent control', detail, level='ERROR')
    return


def audit_experiment_platforms_mismatches(value, system, files_structure):
    if value['status'] in ['deleted', 'replaced']:
        return

    # do not apply the audit to DNase-seq and genetic modification followed by DNase-seq
    if value.get("assay_term_id") in ["OBI:0001853", "NTR:0004774"]:
        return

    if not files_structure.get('original_files'):
        return

    platforms = get_platforms_used_in_experiment(files_structure)
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
                if control.get('original_files'):
                    control_platforms = get_platforms_used_in_experiment(
                        create_files_mapping(control.get('original_files'), files_structure.get('excluded_types')))
                    if len(control_platforms) > 1:
                        control_platforms_string = str(
                            list(control_platforms)).replace('\'', '')
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


def audit_experiment_ChIP_control(value, system, files_structure):
    if not check_award_condition(value, [
            'ENCODE3', 'ENCODE4', 'Roadmap']):
        return

    if value['status'] in ['deleted', 'replaced', 'revoked']:
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
            yield AuditFailure('invalid possible_control', detail, level='ERROR')
            return

        if not control.get('replicates'):
            continue

        if 'antibody' in control.get('replicates')[0]:
            num_IgG_controls += 1

    # If all of the possible_control experiments are mock IP control experiments
    if num_IgG_controls == len(value['possible_controls']):
        if value.get('assay_term_name') == 'ChIP-seq':
            # The binding group agreed that ChIP-seqs all should have an input control.
            detail = 'Experiment {} is ChIP-seq and requires at least one input control, as agreed upon by the binding group. {} is not an input control'.format(
                value['@id'],
                control['@id'])
            yield AuditFailure('missing input control', detail, level='NOT_COMPLIANT')
    return


def audit_experiment_spikeins(value, system, excluded_types):
    if not check_award_condition(value, [
            "ENCODE3",
            "ENCODE4",
            "modERN",
            "ENCODE",
            "ENCODE2-Mouse",
            "Roadmap"]):
        return
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
    return


def audit_experiment_biosample_term(value, system, excluded_types):
    if value['status'] in ['deleted', 'replaced']:
        return

    if value.get('biosample_type') == 'cell-free sample':
        return

    ontology = system['registry']['ontology']
    term_id = value.get('biosample_term_id')
    term_type = value.get('biosample_type')
    term_name = value.get('biosample_term_name')

    if 'biosample_term_name' not in value:
        detail = '{} is missing biosample_term_name'.format(value['@id'])
        yield AuditFailure('missing biosample_term_name', detail, level='ERROR')
    # The type and term name should be put into dependencies

    if term_id.startswith('NTR:'):
        detail = '{} has an NTR biosample {} - {}'.format(
            value['@id'], term_id, term_name)
        yield AuditFailure('NTR biosample', detail, level='INTERNAL_ACTION')
    else:
        if term_id not in ontology:
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
                         'while experiment\'s biosample type is \"{}\".'.format(
                             term_type)
                yield AuditFailure('inconsistent library biosample', detail, level='ERROR')

            if bs_name != term_name:
                detail = 'Experiment {} '.format(value['@id']) + \
                         'contains a library {} '.format(lib['@id']) + \
                         'prepared from biosample {}, '.format(bs_name) + \
                         'while experiment\'s biosample is {}.'.format(
                             term_name)
                yield AuditFailure('inconsistent library biosample', detail, level='ERROR')

            if bs_id != term_id:
                detail = 'Experiment {} '.format(value['@id']) + \
                         'contains a library {} '.format(lib['@id']) + \
                         'prepared from biosample with an id \"{}\", '.format(bs_id) + \
                         'while experiment\'s biosample id is \"{}\".'.format(
                             term_id)
                yield AuditFailure('inconsistent library biosample', detail, level='ERROR')
    return


def audit_experiment_antibody_characterized(value, system, excluded_types):
    '''Check that biosample in the experiment has been characterized for the given antibody.'''
    if not check_award_condition(value, [
            'ENCODE4', 'ENCODE3', 'modERN']):
        return

    if value['status'] in ['deleted']:
        return

    if value.get('assay_term_name') not in targetBasedAssayList:
        return

    target = value.get('target')
    if not target:
        return

    if 'control' in target['investigated_as']:
        return

    if value['assay_term_name'] in ['RNA Bind-n-Seq',
                                    'shRNA knockdown followed by RNA-seq',
                                    'siRNA knockdown followed by RNA-seq',
                                    'CRISPRi followed by RNA-seq']:
        return

    for rep in value['replicates']:
        antibody = rep.get('antibody')
        lib = rep.get('library')

        if not antibody or not lib:
            continue

        biosample = lib.get('biosample')
        if not biosample:
            continue

        organism = biosample.get('organism')
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
                                 'to the standard with exemption for {}'.format(
                                     organism)
                        yield AuditFailure('antibody characterized with exemption',
                                           detail, level='WARNING')
                    elif lot_review['status'] == 'awaiting characterization':
                        detail = '{} has not yet been characterized in '.format(antibody['@id']) + \
                            'any cell type or tissue in {}'.format(organism)
                        yield AuditFailure('uncharacterized antibody',
                                           detail, level='NOT_COMPLIANT')
                    elif lot_review['status'] in ['not characterized to standards', 'not pursued']:
                        detail = '{} has not been '.format(antibody['@id']) + \
                            'characterized to the standard for {}: {}'.format(
                                organism, lot_review['detail'])
                        yield AuditFailure('antibody not characterized to standard', detail,
                                           level='NOT_COMPLIANT')
                    elif lot_review['status'] in ['pending dcc review',
                                                  'partially characterized']:
                        detail = '{} has characterization attempts '.format(antibody['@id']) + \
                                 'but does not have the full complement of characterizations ' + \
                                 'meeting the standard in {}: {}'.format(
                                     organism, lot_review['detail'])
                        yield AuditFailure('partially characterized antibody',
                                           detail, level='NOT_COMPLIANT')
                    else:
                        # This should only leave the characterized to standards case
                        pass
        else:
            biosample_term_id = value['biosample_term_id']
            biosample_term_name = value['biosample_term_name']
            experiment_biosample = (biosample_term_id, organism)

            for lot_review in antibody['lot_reviews']:
                biosample_key = (
                    lot_review['biosample_term_id'], lot_review['organisms'][0])
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
                    elif lot_review['status'] in ['partially characterized', 'pending dcc review']:
                        detail = '{} has characterization attempts '.format(antibody['@id']) + \
                                 'but does not have the full complement of characterizations ' + \
                                 'meeting the standard in {}: {}'.format(
                                     organism, lot_review['detail'])
                        yield AuditFailure('partially characterized antibody',
                                           detail, level='NOT_COMPLIANT')
                    elif lot_review['status'] in ['not characterized to standards', 'not pursued']:
                        detail = '{} has not been '.format(antibody['@id']) + \
                                 'characterized to the standard for {}: {}'.format(
                                     organism, lot_review['detail'])
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
    return


def audit_experiment_library_biosample(value, system, excluded_types):
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
    return


def audit_library_RNA_size_range(value, system, excluded_types):
    '''
    An RNA library should have a size_range specified.
    This needs to accomodate the rfa
    '''
    if value['status'] in ['deleted', 'replaced']:
        return

    if value.get('assay_term_name') == 'transcription profiling by array assay':
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
    return


# if experiment target is recombinant protein, the biosamples should have at
# least one GM in the applied_modifications that is an insert with tagging purpose
# and a target that matches experiment target
def audit_missing_modification(value, system, excluded_types):
    if value['status'] in ['deleted', 'replaced', 'revoked']:
        return

    if 'target' not in value:
        return

    '''
    The audit does not cover whether or not the biosamples in possible_controls also
    have the same construct. In some cases, they legitimately don't, e.g. HEK-ZNFs
    '''
    target = value['target']
    if 'recombinant protein' not in target['investigated_as']:
        return
    else:
        biosamples = get_biosamples(value)
        missing_construct = list()

        for biosample in biosamples:
            if biosample.get('applied_modifications'):
                match_flag = False
                for modification in biosample.get('applied_modifications'):
                    if modification.get('modified_site_by_target_id'):
                        gm_target = modification.get(
                            'modified_site_by_target_id')
                        if modification.get('purpose') == 'tagging' and \
                           gm_target['@id'] == target['@id']:
                            match_flag = True
                if not match_flag:
                    missing_construct.append(biosample)
            else:
                missing_construct.append(biosample)

        if missing_construct:
            for b in missing_construct:
                detail = 'Recombinant protein target {} requires '.format(target['@id']) + \
                    'a genetic modification associated with the biosample {} '.format(b['@id']) + \
                    'to specify the relevant tagging details.'
                yield AuditFailure('inconsistent genetic modification tags', detail, level='ERROR')
    return


def audit_experiment_mapped_read_length(value, system, files_structure):
    if value.get('assay_term_id') != 'OBI:0000716':  # not a ChIP-seq
        return
    for peaks_file in files_structure.get('peaks_files').values():
        if peaks_file.get('lab') == '/labs/encode-processing-pipeline/':
            derived_from_bams = get_derived_from_files_set(
                [peaks_file], files_structure, 'bam', True)
            #derived_from_bams = get_derived_from_files_set([peaks_file], 'bam', True)
            read_lengths_set = set()
            for bam_file in derived_from_bams:
                if bam_file.get('lab') == '/labs/encode-processing-pipeline/':
                    mapped_read_length = get_mapped_length(
                        bam_file, files_structure)
                    if mapped_read_length:
                        read_lengths_set.add(mapped_read_length)
                    else:
                        detail = 'Experiment {} '.format(value['@id']) + \
                                 'contains an alignments .bam file {} '.format(bam_file['@id']) + \
                                 'that lacks mapped reads length information.'
                        yield AuditFailure('missing mapped reads lengths', detail,
                                           level='INTERNAL_ACTION')
            if len(read_lengths_set) > 1:
                if max(read_lengths_set) - min(read_lengths_set) >= 7:
                    detail = 'Experiment {} '.format(value['@id']) + \
                             'contains a processed .bed file {} '.format(peaks_file['@id']) + \
                             'that was derived from alignments files with inconsistent mapped ' + \
                             'reads lengths {}.'.format(
                                 sorted(list(read_lengths_set)))
                    yield AuditFailure('inconsistent mapped reads lengths',
                                       detail, level='INTERNAL_ACTION')
    return


#######################
# utilities
#######################

def extract_assemblies(assemblies, file_names):
    to_return = set()
    for f_name in file_names:
        if f_name in assemblies:
            to_return.add(assemblies[f_name])
    return sorted(list(to_return))


def assemblies_detail(assemblies):
    assemblies_detail = ''
    if assemblies:
        if len(assemblies) > 1:
            assemblies_detail = "for {} assemblies ".format(
                str(assemblies).replace('\'', ' '))
        else:
            assemblies_detail = "for {} assembly ".format(
                assemblies[0])
    return assemblies_detail


def get_mapped_length(bam_file, files_structure):
    mapped_length = bam_file.get('mapped_read_length')
    if mapped_length:
        return mapped_length
    derived_from_fastqs = get_derived_from_files_set(
        [bam_file], files_structure, 'fastq', True)
    for f in derived_from_fastqs:
        length = f.get('read_length')
        if length:
            return length
    return None


def get_control_bam(experiment_bam, pipeline_name, derived_from_fastqs, files_structure):
    #  get representative FASTQ file
    if not derived_from_fastqs:
        return False
    control_fastq = False
    for entry in derived_from_fastqs:
        if entry.get('dataset') == experiment_bam.get('dataset') and \
           'controlled_by' in entry and len(entry['controlled_by']) > 0:
            # getting representative FASTQ
            control_fastq = entry['controlled_by'][0]
            break
    # get representative FASTQ from control
    if control_fastq is False:
        return False
    else:
        if 'original_files' not in control_fastq['dataset']:
            return False

        control_bam = False
        control_files_structure = create_files_mapping(control_fastq['dataset'].get('original_files'),
                                                       files_structure.get('excluded_types'))

        for control_file in control_files_structure.get('alignments').values():
            if 'assembly' in control_file and 'assembly' in experiment_bam and \
               control_file['assembly'] == experiment_bam['assembly']:
                #  we have BAM file, now we have to make sure it was created by pipeline
                #  with similar pipeline_name

                is_same_pipeline = False
                if has_pipelines(control_file) is True:
                    for pipeline in \
                            control_file['analysis_step_version']['analysis_step']['pipelines']:
                        if pipeline['title'] == pipeline_name:
                            is_same_pipeline = True
                            break

                if is_same_pipeline is True and \
                   'derived_from' in control_file and \
                   len(control_file['derived_from']) > 0:
                    derived_list = list(
                        get_derived_from_files_set([control_file], control_files_structure, 'fastq', True))

                    for entry in derived_list:
                        if entry['accession'] == control_fastq['accession']:
                            control_bam = control_file
                            break
        return control_bam


def has_pipelines(bam_file):
    if 'analysis_step_version' not in bam_file:
        return False
    if 'analysis_step' not in bam_file['analysis_step_version']:
        return False
    if 'pipelines' not in bam_file['analysis_step_version']['analysis_step']:
        return False
    return True


def get_target_name(derived_from_fastqs):
    if not derived_from_fastqs:
        return False

    control_fastq = False
    for entry in derived_from_fastqs:
        if 'controlled_by' in entry and len(entry['controlled_by']) > 0:
            # getting representative FASTQ
            control_fastq = entry['controlled_by'][0]
            break
    if control_fastq and 'target' in control_fastq['dataset'] and \
       'name' in control_fastq['dataset']['target']:
        return control_fastq['dataset']['target']['name']
    return False


def get_target(experiment):
    if 'target' in experiment:
        return experiment['target']
    return False


def get_organism_name(reps, excluded_types):
    excluded_types += ['deleted', 'replaced']
    for rep in reps:
        if rep['status'] not in excluded_types and \
           'library' in rep and \
           rep['library']['status'] not in excluded_types and \
           'biosample' in rep['library'] and \
           rep['library']['biosample']['status'] not in excluded_types:
            if 'organism' in rep['library']['biosample']:
                return rep['library']['biosample']['organism'].split('/')[2]
    return False


def scanFilesForPipelineTitle_not_chipseq(files_to_scan, assemblies, pipeline_titles):
    for f in files_to_scan:
        if 'file_format' in f and f['file_format'] == 'bam' and \
           f['status'] not in ['replaced', 'deleted'] and \
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


def get_pipeline_by_name(pipeline_objects, pipeline_title):
    for pipe in pipeline_objects:
        if pipe['title'] == pipeline_title:
            return pipe
    return None


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


def get_file_read_depth_from_alignment(alignment_file, target, assay_name):

    if alignment_file.get('output_type') in ['transcriptome alignments',
                                             'unfiltered alignments']:
        return False

    if alignment_file.get('lab') not in ['/labs/encode-processing-pipeline/', '/labs/kevin-white/']:
        return False

    quality_metrics = alignment_file.get('quality_metrics')

    if not quality_metrics:
        return False

    if assay_name in ['RAMPAGE', 'CAGE',
                      'small RNA',
                      'long RNA']:
        for metric in quality_metrics:
            if 'Uniquely mapped reads number' in metric and \
               'Number of reads mapped to multiple loci' in metric:
                unique = metric['Uniquely mapped reads number']
                multi = metric['Number of reads mapped to multiple loci']
                return unique + multi

    elif assay_name in ['ChIP-seq']:
        if target is not False and \
           'name' in target and target['name'] in ['H3K9me3-human', 'H3K9me3-mouse']:
            # exception (mapped)
            for metric in quality_metrics:
                if 'processing_stage' in metric and \
                    metric['processing_stage'] == 'unfiltered' and \
                        'mapped' in metric:
                    if "read1" in metric and "read2" in metric:
                        return int(metric['mapped'] / 2)
                    else:
                        return int(metric['mapped'])
        else:
            # not exception (useful fragments)
            for metric in quality_metrics:
                if ('total' in metric) and \
                   (('processing_stage' in metric and metric['processing_stage'] == 'filtered') or
                        ('processing_stage' not in metric)):
                    if "read1" in metric and "read2" in metric:
                        return int(metric['total'] / 2)
                    else:
                        return int(metric['total'])
    return False


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


def get_read_lengths_wgbs(fastq_files):
    list_of_lengths = []
    for f in fastq_files:
        if 'read_length' in f:
            list_of_lengths.append(f['read_length'])
    return list_of_lengths


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


def get_chip_seq_bam_read_depth(bam_file):
    if bam_file['status'] in ['deleted', 'replaced']:
        return False

    if bam_file['file_format'] != 'bam' or \
        bam_file['output_type'] not in ['alignments', 'redacted alignments']:
        return False

    # Check to see if bam is from ENCODE or modERN pipelines
    if bam_file['lab'] not in ['/labs/encode-processing-pipeline/', '/labs/kevin-white/']:
        return False

    if has_pipelines(bam_file) is False:
        return False

    quality_metrics = bam_file.get('quality_metrics')

    if (quality_metrics is None) or (quality_metrics == []):
        return False

    read_depth = 0

    for metric in quality_metrics:
        if ('total' in metric and
                (('processing_stage' in metric and metric['processing_stage'] == 'filtered') or
                 ('processing_stage' not in metric))):
            if "read1" in metric and "read2" in metric:
                read_depth = int(metric['total'] / 2)
            else:
                read_depth = metric['total']
            break

    if read_depth == 0:
        return False

    return read_depth


def create_files_mapping(files_list, excluded):
    to_return = {'original_files': {},
                 'fastq_files': {},
                 'alignments': {},
                 'unfiltered_alignments': {},
                 'transcriptome_alignments': {},
                 'peaks_files': {},
                 'gene_quantifications_files': {},
                 'signal_files': {},
                 'optimal_idr_peaks': {},
                 'cpg_quantifications': {},
                 'contributing_files': {},
                 'excluded_types': excluded}
    if files_list:
        for file_object in files_list:
            if file_object['status'] not in excluded:
                to_return['original_files'][file_object['@id']] = file_object

                file_format = file_object.get('file_format')
                file_output = file_object.get('output_type')

                if file_format and file_format == 'fastq' and \
                        file_output and file_output == 'reads':
                    to_return['fastq_files'][file_object['@id']] = file_object

                if file_format and file_format == 'bam' and \
                        file_output and (
                            file_output == 'alignments' or
                            file_output and file_output == 'redacted alignments'):
                    to_return['alignments'][file_object['@id']] = file_object

                if file_format and file_format == 'bam' and \
                        file_output and (
                            file_output == 'unfiltered alignments' or
                            file_output == 'redacted unfiltered alignments'):
                    to_return['unfiltered_alignments'][file_object['@id']
                                                       ] = file_object

                if file_format and file_format == 'bam' and \
                        file_output and file_output == 'transcriptome alignments':
                    to_return['transcriptome_alignments'][file_object['@id']
                                                          ] = file_object

                if file_format and file_format == 'bed' and \
                        file_output and file_output == 'peaks':
                    to_return['peaks_files'][file_object['@id']] = file_object

                if file_output and file_output == 'gene quantifications':
                    to_return['gene_quantifications_files'][file_object['@id']
                                                            ] = file_object

                if file_output and file_output == 'signal of unique reads':
                    to_return['signal_files'][file_object['@id']] = file_object

                if file_output and file_output == 'optimal idr thresholded peaks':
                    to_return['optimal_idr_peaks'][file_object['@id']
                                                   ] = file_object

                if file_output and file_output == 'methylation state at CpG':
                    to_return['cpg_quantifications'][file_object['@id']
                                                     ] = file_object
    return to_return


def get_contributing_files(files_list, excluded_types):
    to_return = {}
    if files_list:
        for file_object in files_list:
            if file_object['status'] not in excluded_types:
                to_return[file_object['@id']] = file_object
    return to_return


def scanFilesForPipelineTitle_yes_chipseq(alignment_files, pipeline_titles):

    if alignment_files:
        for f in alignment_files:
            if f.get('lab') in ['/labs/encode-processing-pipeline/', '/labs/kevin-white/'] and \
                'analysis_step_version' in f and \
                'analysis_step' in f['analysis_step_version'] and \
                    'pipelines' in f['analysis_step_version']['analysis_step']:
                pipelines = f['analysis_step_version']['analysis_step']['pipelines']
                for p in pipelines:
                    if p['title'] in pipeline_titles:
                        return p['title']
    return False


def get_derived_from_files_set(list_of_files, files_structure, file_format, object_flag):
    derived_from_set = set()
    derived_from_objects_list = []
    for file_object in list_of_files:
        if 'derived_from' in file_object:
            for derived_id in file_object['derived_from']:
                derived_object = files_structure.get(
                    'original_files').get(derived_id)
                if not derived_object:
                    derived_object = files_structure.get(
                        'contributing_files').get(derived_id)
                if derived_object and \
                   derived_object.get('file_format') == file_format and \
                   derived_object.get('accession') not in derived_from_set:
                    derived_from_set.add(derived_object.get('accession'))
                    if object_flag:
                        derived_from_objects_list.append(derived_object)
    if object_flag:
        return derived_from_objects_list
    return derived_from_set


def get_file_accessions(list_of_files):
    accessions_set = set()
    for file_object in list_of_files:
        accessions_set.add(file_object.get('accession'))
    return accessions_set


def is_outdated_bams_replicate(bam_file, files_structure, assay_name):
    # if derived_from contains accessions that were not in
    # original_files and not in contributing files - it is outdated!    
    for file_id in bam_file.get('derived_from'):
        if file_id not in files_structure.get('original_files') and \
           file_id not in files_structure.get('contributing_files'):
            return True

    derived_from_fastqs = get_derived_from_files_set(
        [bam_file], files_structure, 'fastq', True)

    # if there are no FASTQs we can not find our the replicate
    if len(derived_from_fastqs) == 0:
        return False

    derived_from_fastq_accessions = get_file_accessions(derived_from_fastqs)

    # for ChIP-seq we should consider biological replicates
    # for DNase we should consider technial replicates
    if assay_name != 'ChIP-seq':
        replicate_type = 'technical_replicates'
    else:
        replicate_type = 'biological_replicates'
    rep = bam_file.get(replicate_type)
    
    # number of replicates BAM file should belong to have to be one
    # in cases where it is more than one, there probably was replicates 
    # reorganization, that invalidates the analysis    
    if isinstance(rep, list) and len(rep) > 1:
        return True


    rep_type_fastqs = [
        f for f in files_structure.get('fastq_files').values()
        if replicate_type in f
    ]
    rep_set = set(rep)
    rep_fastqs = [
        f for f in rep_type_fastqs
        if any(e in rep_set for e in set(f[replicate_type]))
    ]

    replicate_fastq_accessions = get_file_accessions(rep_fastqs)
    for file_object in rep_fastqs:
        file_acc = file_object.get('accession')
        # for ChIP even one file out of pair is considerd uptodate
        if assay_name == 'ChIP-seq' and file_acc not in derived_from_fastq_accessions:
            paired_file_id = file_object.get('paired_with')
            if paired_file_id and paired_file_id.split('/')[2] not in derived_from_fastq_accessions:
                return True
            elif not paired_file_id:
                return True
        # for DNase all the files from tech. rep should be in the list of the derived_from
        elif assay_name != 'ChIP-seq' and file_acc not in derived_from_fastq_accessions:
            return True

    for f_accession in derived_from_fastq_accessions:
        if f_accession not in replicate_fastq_accessions:
            return True
    return False


def has_only_raw_files_in_derived_from(bam_file, files_structure):
    if 'derived_from' in bam_file:
        if bam_file['derived_from'] == []:
            return False
        for file_id in bam_file['derived_from']:
            file_object = files_structure.get('original_files').get('file_id')
            if file_object and \
               file_object['file_format'] not in ['fastq', 'tar', 'fasta']:
                return False
        return True
    else:
        return False


def has_no_unfiltered(filtered_bam, unfiltered_bams):
    if 'assembly' in filtered_bam:
        for file_object in unfiltered_bams:
            if 'assembly' in file_object:
                if file_object['assembly'] == filtered_bam['assembly'] and \
                   file_object['biological_replicates'] == filtered_bam['biological_replicates']:
                    derived_candidate = set()
                    derived_filtered = set()
                    if 'derived_from' in file_object:
                        for file_id in file_object['derived_from']:
                            derived_candidate.add(file_id)
                    if 'derived_from' in filtered_bam:
                        for file_id in filtered_bam['derived_from']:
                            derived_filtered.add(file_id)
                    if derived_candidate == derived_filtered:
                        return False
        return True
    return False


def get_platforms_used_in_experiment(files_structure_to_check):
    platforms = set()
    for file_object in files_structure_to_check.get('original_files').values():
        if file_object['output_category'] == 'raw data' and \
                'platform' in file_object:
            # collapsing interchangable platforms HiSeq2000/2500 and all Ilumina Genome Analyzers II/IIe/IIx
            if file_object['platform']['term_id'] in ['OBI:0002002', 'OBI:0002001']:
                platforms.add('Illumina HiSeq 2000/2500')
            elif file_object['platform']['term_id'] in ['OBI:0002000',
                                                        'OBI:0000703',
                                                        'OBI:0002027']:
                platforms.add('Illumina Genome Analyzer II/e/x')
            else:
                platforms.add(file_object['platform']['term_name'])
    return platforms


def get_pipeline_titles(pipeline_objects):
    to_return = set()
    for pipeline in pipeline_objects:
        to_return.add(pipeline.get('title'))
    return list(to_return)


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


def is_gtex_experiment(experiment_to_check):
    for rep in experiment_to_check['replicates']:
        if ('library' in rep) and ('biosample' in rep['library']) and \
           ('donor' in rep['library']['biosample']):
            if rep['library']['biosample']['donor']['accession'] in gtexDonorsList:
                return True
    return False


def check_award_condition(experiment, awards):
    return experiment.get('award') and experiment.get('award')['rfa'] in awards


function_dispatcher_without_files = {
    'audit_isogeneity': audit_experiment_isogeneity,
    'audit_replicate_biosample': audit_experiment_replicates_biosample,
    'audit_replicate_library': audit_experiment_technical_replicates_same_library,
    'audit_documents': audit_experiment_documents,
    'audit_replicate_without_libraries': audit_experiment_replicates_with_no_libraries,
    'audit_experiment_biosample': audit_experiment_biosample_term,
    'audit_library_biosample': audit_experiment_library_biosample,
    'audit_target': audit_experiment_target,
    'audit_mixed_libraries': audit_experiment_mixed_libraries,
    'audit_internal_tags': audit_experiment_internal_tag,
    'audit_geo_submission': audit_experiment_geo_submission,
    'audit_replication': audit_experiment_replicated,
    'audit_RNA_size': audit_library_RNA_size_range,
    'audit_missing_modifiction': audit_missing_modification,
    'audit_AB_characterization': audit_experiment_antibody_characterized,
    'audit_control': audit_experiment_control,
    'audit_spikeins': audit_experiment_spikeins
}

function_dispatcher_with_files = {
    'audit_consistent_sequencing_runs': audit_experiment_consistent_sequencing_runs,
    'audit_experiment_out_of_date': audit_experiment_out_of_date_analysis,
    'audit_replicate_no_files': audit_experiment_replicate_with_no_files,
    'audit_platforms': audit_experiment_platforms_mismatches,
    'audit_uploading_files': audit_experiment_with_uploading_files,
    'audit_pipeline_assay': audit_experiment_pipeline_assay_details,
    'audit_missing_unfiltered_bams': audit_experiment_missing_unfiltered_bams,
    'audit_modERN': audit_modERN_experiment_standards_dispatcher,
    'audit_read_length': audit_experiment_mapped_read_length,
    'audit_chip_control': audit_experiment_ChIP_control,
    'audit_read_depth_chip_control': audit_experiment_chipseq_control_read_depth,
    'audit_experiment_standards': audit_experiment_standards_dispatcher,
    'audit_submitted_status': audit_experiment_status
}


@audit_checker(
    'Experiment',
    frame=[
        'award',
        'target',
        'replicates',
        'replicates.library',
        'replicates.library.spikeins_used',
        'replicates.library.biosample',
        'replicates.library.biosample.applied_modifications',
        'replicates.library.biosample.applied_modifications.modified_site_by_target_id',
        'replicates.library.biosample.donor',
        'replicates.library.biosample.constructs',
        'replicates.library.biosample.constructs.target',
        'replicates.library.biosample.model_organism_donor_constructs',
        'replicates.library.biosample.model_organism_donor_constructs.target',
        'replicates.antibody',
        'replicates.antibody.targets',
        'replicates.antibody.lot_reviews',
        'possible_controls',
        'possible_controls.original_files',
        'possible_controls.original_files.platform',
        'possible_controls.target',
        'possible_controls.replicates',
        'possible_controls.replicates.antibody',
        'contributing_files',
        'original_files',
        'original_files.award',
        'original_files.quality_metrics',
        'original_files.platform',
        'original_files.replicate',
        'original_files.analysis_step_version',
        'original_files.analysis_step_version.analysis_step',
        'original_files.analysis_step_version.analysis_step.pipelines',
        'original_files.analysis_step_version.software_versions',
        'original_files.analysis_step_version.software_versions.software',
        'original_files.controlled_by',
        'original_files.controlled_by.dataset',
        'original_files.controlled_by.dataset.target',
        'original_files.controlled_by.dataset.original_files',
        'original_files.controlled_by.dataset.original_files.quality_metrics',
        'original_files.controlled_by.dataset.original_files.analysis_step_version',
        'original_files.controlled_by.dataset.original_files.analysis_step_version.analysis_step',
        'original_files.controlled_by.dataset.original_files.analysis_step_version.analysis_step.pipelines',
    ])
def audit_experiment(value, system):
    excluded_files = ['revoked', 'archived']
    if value.get('status') == 'revoked':
        excluded_files = []
    if value.get('status') == 'archived':
        excluded_files = ['revoked']
    files_structure = create_files_mapping(
        value.get('original_files'), excluded_files)
    files_structure['contributing_files'] = get_contributing_files(
        value.get('contributing_files'), excluded_files)

    for function_name in function_dispatcher_with_files.keys():
        yield from function_dispatcher_with_files[function_name](value, system, files_structure)

    excluded_types = excluded_files + ['deleted', 'replaced']
    for function_name in function_dispatcher_without_files.keys():
        yield from function_dispatcher_without_files[function_name](value, system, excluded_types)

    return


#  def audit_experiment_control_out_of_date_analysis(value, system):
#  removed due to https://encodedcc.atlassian.net/browse/ENCD-3460

# def create_pipeline_structures(files_to_scan, structure_type):
# condensed under https://encodedcc.atlassian.net/browse/ENCD-3493

# def check_structures(replicate_structures, control_flag, experiment):
# https://encodedcc.atlassian.net/browse/ENCD-3538

# def audit_experiment_gtex_biosample(value, system):
# https://encodedcc.atlassian.net/browse/ENCD-3538

# def audit_experiment_biosample_term_id(value, system): removed release 56
# http://redmine.encodedcc.org/issues/4900

# def audit_experiment_needs_pipeline(value, system): removed in release 56
# http://redmine.encodedcc.org/issues/4990
