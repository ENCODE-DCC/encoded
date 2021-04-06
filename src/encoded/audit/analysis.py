from snovault import (
    AuditFailure,
    audit_checker,
)
from .formatter import (
    audit_link,
    path_to_text,
)

from .standards_data import pipelines_with_read_depth, minimal_read_depth_requirements


'''
Utilities
'''


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


def get_target(experiment):
    if 'target' in experiment:
        return experiment['target']
    return False


def get_control_type(experiment):
    if 'control_type' in experiment:
        return experiment['control_type']
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
        if not tophat_flag and \
           f['lab'] == '/labs/encode-processing-pipeline/':
            list_to_return.append(f)
    return list_to_return


def get_metrics(files_list, metric_type):
    metrics_dict = {}
    for f in files_list:
        if 'quality_metrics' in f and len(f['quality_metrics']) > 0:
            for qm in f['quality_metrics']:
                if metric_type in qm['@type']:
                    if qm['uuid'] not in metrics_dict:
                        metrics_dict[qm['uuid']] = qm
    metrics = []
    for k in metrics_dict:
        metrics.append(metrics_dict[k])
    return metrics


def check_file_read_depth(
    file_to_check,
    read_depth,
    upper_threshold,
    middle_threshold,
    lower_threshold,
    assay_term_name,
    pipeline_title,
    pipeline,
    standards_link
):
    upper_threshold_detail_text = ''
    if middle_threshold != upper_threshold:
        upper_threshold_detail_text = f'The recommended value is > {upper_threshold}. '

    second_half_of_detail = (
        f"The minimum ENCODE standard for each replicate in a "
        f"{assay_term_name} assay is {middle_threshold} aligned reads. "
        f"{upper_threshold_detail_text}"
        f"(See {audit_link(f'ENCODE {assay_term_name} data standards', standards_link)} )"
    )

    assembly_text = ''
    if 'assembly' in file_to_check:
        assembly_text = f"using the {file_to_check['assembly']} assembly "
    detail = (
        f"Processed {file_to_check['output_type']} file "
        f"{audit_link(path_to_text(file_to_check['@id']), file_to_check['@id'])} "
        f"produced by {audit_link(pipeline_title, pipeline['@id'])} "
        f"{assembly_text}has {read_depth} aligned reads. {second_half_of_detail}"
    )
    if read_depth >= middle_threshold and read_depth < upper_threshold:
        yield AuditFailure('low read depth', detail, level='WARNING')
    elif read_depth >= lower_threshold and read_depth < middle_threshold:
        yield AuditFailure('insufficient read depth', detail,
                           level='NOT_COMPLIANT')
    elif read_depth < lower_threshold:
        yield AuditFailure('extremely low read depth', detail,
                           level='ERROR')
    return


def check_spearman(
    metrics,
    replication_type,
    isogenic_threshold,
    anisogenic_threshold,
    pipeline
):
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
                file_names_links = [audit_link(path_to_text(f), f) for f in file_names]
                detail = (
                    f'Replicate concordance in RNA-seq experiments is measured by '
                    f'calculating the Spearman correlation between gene quantifications '
                    f'of the replicates. '
                    f'ENCODE processed gene quantification files {", ".join(file_names_links)} '
                    f'have a Spearman correlation of {spearman_correlation:.2f}. '
                    f'According to ENCODE standards, in an {replication_type} '
                    f'assay analyzed using the {pipeline} pipeline, '
                    f'a Spearman correlation value > {threshold} '
                    f'is recommended.'
                )
                yield AuditFailure('low replicate concordance', detail, level='WARNING')
    return


def check_spearman_technical_replicates(
    metrics,
    pipeline,
    unreplicated_threshold
):
    for m in metrics:
        if 'Spearman correlation' in m:
            spearman_correlation = m['Spearman correlation']
            if spearman_correlation < unreplicated_threshold:
                file_names = []
                for f in m['quality_metric_of']:
                    file_names.append(f)
                file_names_links = ','.join((audit_link(path_to_text(f), f) for f in file_names))
                detail = (
                    f'Replicate concordance in RNA-seq experiments is measured by '
                    f'calculating the Spearman correlation between gene quantifications '
                    f'of the replicates. ENCODE processed gene quantification files '
                    f'{file_names_links} have a Spearman correlation of '
                    f'{spearman_correlation:.2f} comparing technical replicates. '
                    f'For isogenic biological replicates analyzed using the {pipeline} pipeline, '
                    f'ENCODE standards recommend a Spearman correlation value > 0.9.'
                )
                yield AuditFailure('low replicate concordance', detail, level='WARNING')
    return


def negative_coefficients(metric, coefficients, files_structure):
    for coefficient in coefficients:
        if coefficient in metric and metric[coefficient] < 0 and 'quality_metric_of' in metric:
            alignment_file = files_structure.get(
                'alignments')[metric['quality_metric_of'][0]]
            detail = (
                f"Alignment file {audit_link(path_to_text(alignment_file['@id']),alignment_file['@id'])} "
                f"has a negative {coefficient} value of {metric[coefficient]}. "
                f"The {coefficient} value is expected to be a positive number."
            )
            yield AuditFailure(f"negative {coefficient}", detail, level='ERROR')


def check_idr(metrics, rescue, self_consistency):
    for m in metrics:
        if 'rescue_ratio' in m and 'self_consistency_ratio' in m:
            rescue_r = m['rescue_ratio']
            self_r = m['self_consistency_ratio']

            if rescue_r > rescue and self_r > self_consistency:
                file_list = []
                for f in m['quality_metric_of']:
                    file_list.append(f)
                file_names_links = [audit_link(path_to_text(file), file) for file in file_list]
                detail = (
                    f"Replicate concordance in ChIP-seq experiments is measured by "
                    f"calculating IDR values (Irreproducible Discovery Rate). "
                    f"ENCODE processed IDR thresholded peaks files {', '.join(file_names_links)} "
                    f"have a rescue ratio of {rescue_r:.2f} and a "
                    f"self consistency ratio of {self_r:.2f}. "
                    f"According to ENCODE standards, having both rescue ratio "
                    f"and self consistency ratio values < 2 is recommended, but "
                    f"having only one of the ratio values < 2 is acceptable."
                )
                yield AuditFailure('insufficient replicate concordance', detail,
                                   level='NOT_COMPLIANT')
            elif (rescue_r <= rescue and self_r > self_consistency) or \
                 (rescue_r > rescue and self_r <= self_consistency):
                file_list = []
                for f in m['quality_metric_of']:
                    file_list.append(f)
                file_names_links = [audit_link(path_to_text(file), file) for file in file_list]
                detail = (
                    f"Replicate concordance in ChIP-seq experiments is measured by "
                    f"calculating IDR values (Irreproducible Discovery Rate). "
                    f"ENCODE processed IDR thresholded peaks files {', '.join(file_names_links)} "
                    f"have a rescue ratio of {rescue_r:.2f} and a "
                    f"self consistency ratio of {self_r:.2f}. "
                    f"According to ENCODE standards, having both rescue ratio "
                    f"and self consistency ratio values < 2 is recommended, but "
                    f"having only one of the ratio values < 2 is acceptable."
                )
                yield AuditFailure('borderline replicate concordance', detail,
                                   level='WARNING')
    return


def check_replicate_metric_dual_threshold(
    metrics,
    metric_name,
    audit_name,
    upper_limit,
    lower_limit,
    metric_description=None,
):
    """
    Generic function to handle audits on files from a single replicate with multiple thresholds
    """
    if not metric_description:
        metric_description = metric_name
    for metric in metrics:
        metric_value = metric.get(metric_name)
        files = metric['quality_metric_of']
        if metric_value and metric_value < upper_limit:
            level = 'WARNING'
            standards_severity = 'recommendations'
            audit_name_severity = 'borderline'
            if metric_value < lower_limit:
                level = 'NOT_COMPLIANT'
                standards_severity = 'requirements'
                audit_name_severity = 'insufficient'
            file_names_links = [audit_link(path_to_text(file), file) for file in files]
            detail = (
                f"Files {', '.join(file_names_links)} have {metric_description} "
                f"of {metric_value}, which is below ENCODE {standards_severity}. "
                f"According to ENCODE data standards, a number for this property "
                f"in a replicate of > {lower_limit:,} is required, "
                f"and > {upper_limit:,} is recommended."
            )
            yield AuditFailure('{} {}'.format(audit_name_severity, audit_name), detail, level=level)
    return


def create_files_mapping(files, excluded_files):
    to_return = {
        'alignments': {},
        'unfiltered_alignments': {},

        'normalized_signal_files': {},

        'idr_thresholded_peaks': {},
        'overlap_and_idr_peaks': {},
        'peaks_files': {},
        'preferred_default_idr_peaks': {},
        'pseudo_replicated_peaks_files': {},

        'cpg_quantifications': {},
        'gene_quantifications_files': {},
        'microRNA_quantifications_files': {},
        'transcript_quantifications_files': {},

        'chromatin_interaction_files': {},
    }
    for file_object in files:
        if file_object['status'] not in excluded_files and \
                'file_format' in file_object and \
                'output_type' in file_object:
            file_format = file_object.get('file_format')
            file_output = file_object.get('output_type')

            # Alignments
            if file_format == 'bam' and \
                    file_output and (
                        file_output == 'alignments' or
                        file_output and file_output == 'redacted alignments'):
                to_return['alignments'][file_object['@id']] = file_object
            if file_output == 'unfiltered alignments':
                to_return['unfiltered_alignments'][file_object['@id']] = file_object

            # Signal
            if file_output == 'read-depth normalized signal':
                to_return['normalized_signal_files'][file_object['@id']] = file_object

            # Peaks
            if file_output == 'IDR thresholded peaks':
                to_return['idr_thresholded_peaks'][file_object['@id']] = file_object

            if file_format == 'bed' and file_output in [
                'replicated peaks',
                'pseudoreplicated peaks',
                'conservative IDR thresholded peaks',
                'IDR thresholded peaks'
            ]:
                to_return['overlap_and_idr_peaks'][file_object['@id']] = file_object
            if file_format == 'bed' and file_output in [
                'peaks',
                'peaks and background as input for IDR'
            ]:
                to_return['peaks_files'][file_object['@id']] = file_object
            if file_output == 'optimal IDR thresholded peaks':
                to_return['preferred_default_idr_peaks'][file_object['@id']] = file_object
            if (
                file_object.get('preferred_default')
                and file_output == 'IDR thresholded peaks'
            ):
                to_return['preferred_default_idr_peaks'][
                    file_object['@id']
                ] = file_object
            if (file_format == 'bed' and file_output == 'pseudoreplicated peaks'):
                to_return['pseudo_replicated_peaks_files'][file_object['@id']] = file_object

            # Quantifications
            if file_output == 'methylation state at CpG':
                to_return['cpg_quantifications'][file_object['@id']] = file_object
            if file_output == 'gene quantifications':
                to_return['gene_quantifications_files'][file_object['@id']] = file_object
            if file_output == 'microRNA quantifications':
                to_return['microRNA_quantifications_files'][file_object['@id']] = file_object
            if file_output == 'transcript quantifications':
                to_return['transcript_quantifications_files'][file_object['@id']] = file_object

            # Other processed files
            if file_output in ['chromatin interactions', 'long range chromatin interactions']:
                to_return['chromatin_interaction_files'][file_object['@id']] = file_object

    return to_return


def audit_experiment_standards_dispatcher(value, system, files_structure):
    '''
    Dispatcher function that will redirect to other functions that would
    deal with specific assay types standards
    '''
    if len(value['datasets']) != 1:
        return
    if len(value['pipeline_award_rfas']) != 1:
        return
    if value['pipeline_award_rfas'][0] not in [
        'ENCODE4',
        'ENCODE3',
        'ENCODE2-Mouse',
        'ENCODE2',
        'ENCODE',
        'Roadmap',
        'modERN'
    ]:
        return
    # Allow White lab for Transcription factor ChIP-seq pipeline (modERN) and
    # Ruan lab for ChIA-PIPE
    if len(value['pipeline_labs']) != 1 or \
            value['pipeline_labs'][0] not in [
                '/labs/encode-processing-pipeline/',
                '/labs/kevin-white/',
                '/labs/yijun-ruan/'
    ]:
        return

    '''
    DNase-seq analyses
    '''
    if any(pipeline['title'] == 'DNase-seq pipeline' for pipeline in value['pipelines']):
        yield from check_analysis_dnase_seq_standards(
            value,
            files_structure,
            ['DNase-seq pipeline'],
            '/data-standards/dnase-seq-encode4/')
        return

    if any(pipeline['title'] in [
            'DNase-HS pipeline single-end - Version 2',
            'DNase-HS pipeline paired-end - Version 2']
            for pipeline in value['pipelines']):
        yield from check_analysis_dnase_seq_standards(
            value,
            files_structure,
            [
                'DNase-HS pipeline single-end - Version 2',
                'DNase-HS pipeline paired-end - Version 2',
                'DNase-HS pipeline (single-end)',
                'DNase-HS pipeline (paired-end)'
            ],
            '/data-standards/dnase-seq/')
        return

    '''
    RNA-seq analyses
    '''

    if any(pipeline['title'] == 'RAMPAGE (paired-end, stranded)' for pipeline in value['pipelines']):
        yield from check_analysis_cage_rampage_standards(
            value,
            files_structure,
            ['RAMPAGE (paired-end, stranded)'],
            '/data-standards/rampage/')
    if any(pipeline['title'] == 'Small RNA-seq single-end pipeline' for pipeline in value['pipelines']):
        yield from check_analysis_small_rna_standards(
            value,
            files_structure,
            ['Small RNA-seq single-end pipeline'],
            '/data-standards/rna-seq/small-rnas/')
    if any(pipeline['title'] in [
            'RNA-seq of long RNAs (paired-end, stranded)',
            'RNA-seq of long RNAs (single-end, unstranded)',
            'Bulk RNA-seq']
            for pipeline in value['pipelines']):
        yield from check_analysis_bulk_rna_standards(
            value,
            files_structure,
            [
                'RNA-seq of long RNAs (paired-end, stranded)',
                'RNA-seq of long RNAs (single-end, unstranded)',
                'Bulk RNA-seq'
            ],
            '/data-standards/rna-seq/long-rnas/'
        )
    if any(pipeline['title'] == 'microRNA-seq pipeline' for pipeline in value['pipelines']):
        yield from check_analysis_micro_rna_standards(
            value,
            files_structure,
            ['microRNA-seq pipeline'],
            '/microrna/microrna-seq-encode4/'
        )
    if any(pipeline['title'] == 'Long read RNA-seq pipeline' for pipeline in value['pipelines']):
        yield from check_analysis_long_read_rna_standards(
            value,
            files_structure,
            ['Long read RNA-seq pipeline'],
            '/rna-seq/long-read-rna-seq/'
        )

    '''
    ChIP-seq analyses
    '''

    if any(pipeline['title'] in [
            'ChIP-seq read mapping',
            'Histone ChIP-seq 2',
            'Histone ChIP-seq 2 (unreplicated)',
            'Transcription factor ChIP-seq 2',
            'Transcription factor ChIP-seq 2 (unreplicated)']
            for pipeline in value['pipelines']):
        yield from check_analysis_chip_seq_standards(
            value,
            files_structure,
            [
                'ChIP-seq read mapping',
                'Raw mapping with no filtration',
                'Pool and subsample alignments',
                'Histone ChIP-seq',
                'Histone ChIP-seq (unreplicated)',
                'Transcription factor ChIP-seq',
                'Transcription factor ChIP-seq (unreplicated)',
                'Histone ChIP-seq 2',
                'Histone ChIP-seq 2 (unreplicated)',
                'Transcription factor ChIP-seq 2',
                'Transcription factor ChIP-seq 2 (unreplicated)',
            ],
            '/data-standards/chip-seq/')

    if any(pipeline['title'] == 'Transcription factor ChIP-seq pipeline (modERN)' for pipeline in value['pipelines']):
        yield from check_analysis_modERN_chip_seq_standards(
            value,
            files_structure,
            ['Transcription factor ChIP-seq pipeline (modERN)'],
            '/')

    '''
    WGBS analyses
    '''
    if any(pipeline['title'] in [
            'WGBS single-end pipeline',
            'WGBS paired-end pipeline'] for pipeline in value['pipelines']):
        yield from check_analysis_wgbs_encode3_standards(
            value,
            files_structure,
            [
                'WGBS single-end pipeline',
                'WGBS paired-end pipeline'
            ],
            '/data-standards/wgbs/'
        )

    if any(pipeline['title'] == 'gemBS' for pipeline in value['pipelines']):
        yield from check_analysis_wgbs_encode4_standards(
            value,
            files_structure,
            ['gemBS'],
            '/data-standards/wgbs/'
        )

    '''
    ATAC-seq analyses
    '''

    if any(pipeline['title'] in [
            'ATAC-seq (replicated)',
            'ATAC-seq (unreplicated)'] for pipeline in value['pipelines']):
        yield from check_analysis_atac_encode4_qc_standards(
            value,
            files_structure,
            [
                'ATAC-seq (replicated)',
                'ATAC-seq (unreplicated)'
            ],
            '/atac-seq/')
        return

    '''
    ChIA-PET analyses
    '''
    if any(pipeline['title'] == 'Ruan Lab ChIA-PIPE Pipeline' for pipeline in value['pipelines']):
        yield from check_analysis_chiapet_encode4_qc_standards(
            value,
            files_structure,
            ['Ruan Lab ChIA-PIPE Pipeline'],
            '/')
        return


'''
DNase-seq audits
'''


def audit_dnase_footprints(value, system):
    if 'ENCODE4' not in value['pipeline_award_rfas']:
        return
    if all(
        pipeline['title'] != 'DNase-seq pipeline'
        for pipeline in value['pipelines']
    ):
        return

    has_footprints = False
    zero_footprints_reps = set()
    for f in value['files']:
        if f['output_type'] != 'footprints':
            continue
        has_footprints = True
        for qm in f['quality_metrics']:
            if 'footprint_count' in qm and qm['footprint_count'] == 0:
                zero_footprints_reps |= set(f['technical_replicates'])

    if not has_footprints:
        detail = (
            'Missing footprints in ENCODE4 DNase-seq '
            f'analysis {audit_link(path_to_text(value["@id"]), value["@id"])}'
        )
        yield AuditFailure('missing footprints', detail, level='ERROR')
        return

    # Assume at least one qm['footprint_count'] exists?
    for rep in zero_footprints_reps:
        detail = f'Replicate {rep} has no significant footprints detected.'
        yield AuditFailure(
            'missing footprints', detail, level='WARNING'
        )


def check_analysis_dnase_seq_standards(
    value,
    files_structure,
    expected_pipeline_titles,
    link_to_standards
):
    alignment_files = files_structure.get('alignments').values()
    signal_files = files_structure.get('normalized_signal_files').values()

    if value['assembly'] == 'hg19':
        return
    pipeline_titles = [pipeline['title'] for pipeline in value['pipelines']]
    if any(
        title not in expected_pipeline_titles
        for title in pipeline_titles
    ):
        return

    samtools_flagstat_metrics = get_metrics(alignment_files, 'SamtoolsFlagstatsQualityMetric')
    if samtools_flagstat_metrics is not None and \
            len(samtools_flagstat_metrics) > 0:

        for metric in samtools_flagstat_metrics:
            if 'mapped' in metric and 'quality_metric_of' in metric:
                alignment_file = files_structure.get(
                    'alignments')[metric['quality_metric_of'][0]]
                suffix = (
                    f"According to ENCODE standards, conventional "
                    f"DNase-seq profile requires a minimum of 20 million uniquely mapped "
                    f"reads to generate a reliable SPOT (Signal Portion of Tags) score. "
                    f"The recommended value is > 50 million. For deep, foot-printing depth "
                    f"DNase-seq 150-200 million uniquely mapped reads are recommended. "
                    f"(See {audit_link('ENCODE DNase-seq data standards', link_to_standards)})"
                )
                if 'assembly' in alignment_file:
                    assembly_detail_phrase = f'for {alignment_file["assembly"]} assembly '
                else:
                    assembly_detail_phrase = ''
                detail = (
                    f"Alignment file {audit_link(path_to_text(alignment_file['@id']), alignment_file['@id'])} "
                    f"produced by {pipeline_titles[0]} "
                    f"( {audit_link(path_to_text(value['pipelines'][0]['@id']), value['pipelines'][0]['@id'])} ) "
                    f"{assembly_detail_phrase}has {metric['mapped']} mapped reads. {suffix}"
                )

                if 20000000 <= metric['mapped'] < 50000000:
                    yield AuditFailure('low read depth', detail, level='WARNING')
                elif metric['mapped'] < 20000000:
                    yield AuditFailure('extremely low read depth', detail, level='ERROR')
    elif alignment_files is not None and len(alignment_files) > 0 and \
            (samtools_flagstat_metrics is None or
             len(samtools_flagstat_metrics) == 0):
        file_list = []
        for f in alignment_files:
            file_list.append(f['@id'])
        file_names_links = [audit_link(path_to_text(file), file) for file in file_list]
        detail = (
            f"Alignment files ( {', '.join(file_names_links)} ) "
            f"produced by {pipeline_titles[0]} "
            f"( {audit_link(path_to_text(value['pipelines'][0]['@id']), value['pipelines'][0]['@id'])} ) "
            f"lack read depth information."
        )
        yield AuditFailure('missing read depth', detail, level='INTERNAL_ACTION')

    alignments_assemblies = {}
    for alignment_file in alignment_files:
        if 'assembly' in alignment_file:
            alignments_assemblies[alignment_file['accession']] = alignment_file['assembly']

    signal_assemblies = {}
    for signal_file in signal_files:
        if 'assembly' in signal_file:
            signal_assemblies[signal_file['accession']] = signal_file['assembly']

    hotspot_quality_metrics = get_metrics(alignment_files, 'HotspotQualityMetric')
    if hotspot_quality_metrics is not None and \
       len(hotspot_quality_metrics) > 0:
        for metric in hotspot_quality_metrics:
            if 'spot1_score' in metric:
                file_names = []
                file_list = []
                for f in metric['quality_metric_of']:
                    file_names.append(f.split('/')[2])
                    file_list.append(f)
                file_names_links = [audit_link(path_to_text(file), file) for file in file_list]
                detail = (
                    f"Signal Portion of Tags (SPOT) is a measure of enrichment, "
                    f"analogous to the commonly used fraction of reads in peaks metric. "
                    f"ENCODE processed alignment files {', '.join(file_names_links)} "
                    f"produced by {value['pipelines'][0]['title']} "
                    f"({audit_link(path_to_text(value['pipelines'][0]['@id']), value['pipelines'][0]['@id'])}) "
                    f"{assemblies_detail(extract_assemblies(alignments_assemblies, file_names))} "
                    f"have a SPOT1 score of {metric['spot1_score']:.2f}. "
                    f"According to ENCODE standards, SPOT1 score of 0.4 or higher is considered "
                    f"a product of high quality data. "
                    f"Any sample with a SPOT1 score <0.3 should be targeted for replacement "
                    f"with a higher quality sample, and a "
                    f"SPOT1 score of 0.25 is considered minimally acceptable "
                    f"SPOT1 score of 0.25 is considered minimally acceptable "
                    f"for rare and hard to find primary tissues. (See "
                    f"{audit_link('ENCODE DNase-seq data standards', link_to_standards)})"
                )

                if 0.25 <= metric['spot1_score'] < 0.4:
                    yield AuditFailure('low spot score', detail, level='WARNING')
                elif metric['spot1_score'] < 0.25:
                    yield AuditFailure('extremely low spot score', detail, level='ERROR')

    replicated = [dataset['replication_type'] for dataset in value['datasets'] if 'replication_type' in dataset]
    if (len(replicated) == 1 and replicated[0] == 'unreplicated') or len(replicated) == 0:
        return

    signal_quality_metrics = get_metrics(signal_files, 'CorrelationQualityMetric')
    if signal_quality_metrics is not None and \
       len(signal_quality_metrics) > 0:
        threshold = 0.9
        if replicated[0] == 'anisogenic':
            threshold = 0.85
        for metric in signal_quality_metrics:
            if 'Pearson correlation' in metric:
                file_names = []
                file_list = []
                for f in metric['quality_metric_of']:
                    file_names.append(f.split('/')[2])
                    file_list.append(f)
                file_names_links = [audit_link(path_to_text(file), file) for file in file_list]
                detail = (
                    f"Replicate concordance in DNase-seq experiments is measured by "
                    f"calculating the Pearson correlation between signal quantification "
                    f"of the replicates. "
                    f"ENCODE processed signal files {', '.join(file_names_links)} produced by {value['pipelines'][0]['title']} "
                    f"({audit_link(path_to_text(value['pipelines'][0]['@id']), value['pipelines'][0]['@id'])}) "
                    f"{assemblies_detail(extract_assemblies(signal_assemblies, file_names))} "
                    f"have a Pearson correlation of {metric['Pearson correlation']:.2f}. "
                    f"According to ENCODE standards, in an {replicated[0]} "
                    f"assay a Pearson correlation value > {threshold} is recommended. "
                    f"(See {audit_link('ENCODE DNase-seq data standards', link_to_standards)} )"
                )
                if metric['Pearson correlation'] < threshold:
                    yield AuditFailure('insufficient replicate concordance',
                                       detail, level='NOT_COMPLIANT')
    return


'''
ChIP-seq audits
'''


def check_analysis_chip_seq_standards(
    value,
    files_structure,
    expected_pipeline_titles,
    link_to_standards
):
    if len(value['datasets']) != 1:
        return
    else:
        assay_term_name = value['datasets'][0]['assay_term_name']
        target = get_target(value['datasets'][0])
        control_type = get_control_type(value['datasets'][0])

    if not target and not control_type:
        return

    pipeline_titles = [pipeline['title'] for pipeline in value['pipelines']]
    if any(
        title not in expected_pipeline_titles
        for title in pipeline_titles
    ):
        return

    alignment_files = files_structure.get('alignments').values()
    unfiltered_alignment_files = files_structure.get('unfiltered_alignments').values()
    idr_peaks_files = files_structure.get('preferred_default_idr_peaks').values()

    # Check normalized strand cross-correlation and relative strand cross-correlation
    align_enrich_metrics = get_metrics(alignment_files, 'ChipAlignmentEnrichmentQualityMetric')
    if align_enrich_metrics is not None and len(align_enrich_metrics) > 0:
        for metric in align_enrich_metrics:
            yield from negative_coefficients(metric, ['NSC', 'RSC'], files_structure)

    # Check read depth
    # For ChIP-seq targeting H3K9me3 only, read depth should be checked in unfiltered alignments.
    if target and target['name'] in ['H3K9me3-human', 'H3K9me3-mouse']:
        files_to_check_for_read_depth = unfiltered_alignment_files
    else:
        files_to_check_for_read_depth = alignment_files
    for f in files_to_check_for_read_depth:
        read_depth = get_file_read_depth_from_alignment(f, target)
        yield from check_file_chip_seq_read_depth(
            file_to_check=f,
            assay_term_name=assay_term_name,
            pipeline_title=value['title'],
            control_type=control_type,
            target=target,
            read_depth=read_depth,
            link_to_standards=link_to_standards
        )

    # Check library_complexity
    for f in alignment_files:
        yield from check_file_chip_seq_library_complexity(f)

    # Check IDR
    replicated = value['datasets'][0]['replication_type'] if 'replication_type' in value['datasets'][0] else None
    if replicated == 'unreplicated' or replicated is None:
        return

    ListofMetrics = []
    ListofMetrics.extend([get_metrics(idr_peaks_files, 'IDRQualityMetric'), get_metrics(idr_peaks_files, 'ChipReplicationQualityMetric')])
    if ListofMetrics:
        for idr_metrics in ListofMetrics:
            yield from check_idr(idr_metrics, 2, 2)
    return


def check_analysis_modERN_chip_seq_standards(
    value,
    files_structure,
    expected_pipeline_titles,
    link_to_standards
):
    if len(value['datasets']) != 1 or len(value['pipelines']) != 1:
        return
    else:
        target = get_target(value['datasets'][0])
        control_type = get_control_type(value['datasets'][0])

    pipeline_title = value['pipelines'][0]['title']
    if pipeline_title not in expected_pipeline_titles:
        return

    alignment_files = files_structure.get('alignments').values()
    idr_peaks_files = files_structure.get('preferred_default_idr_peaks').values()

    for f in alignment_files:

        yield from check_file_chip_seq_library_complexity(f)

        read_depth = get_file_read_depth_from_alignment(f, target)
        yield from check_file_modERN_chip_seq_read_depth(
            file_to_check=f,
            pipeline_title=pipeline_title,
            control_type=control_type,
            target=target,
            read_depth=read_depth,
            link_to_standards=link_to_standards,
        )

    replicated = [dataset['replication_type'] for dataset in value['datasets'] if 'replication_type' in dataset]
    if (len(replicated) == 1 and replicated[0] == 'unreplicated') or len(replicated) == 0:
        return

    ListofMetrics = []
    ListofMetrics.extend([
        get_metrics(idr_peaks_files, 'IDRQualityMetric'),
        get_metrics(idr_peaks_files, 'ChipReplicationQualityMetric')
    ])
    if ListofMetrics:
        for idr_metrics in ListofMetrics:
            yield from check_idr(idr_metrics, 2, 2)
    return


def check_file_chip_seq_library_complexity(alignment_file):
    '''
    An alignment file from the ENCODE ChIP-seq processing pipeline
    should have minimal library complexity in accordance with the criteria
    '''
    if ('quality_metrics' not in alignment_file) or (alignment_file.get('quality_metrics') == []):
        return

    nrf_detail = (
        'NRF (Non Redundant Fraction) is equal to the result of the '
        'division of the number of reads after duplicates removal by '
        'the total number of reads. '
        'An NRF value in the range 0 - 0.5 is poor complexity, '
        '0.5 - 0.8 is moderate complexity, '
        'and > 0.8 high complexity. NRF value > 0.8 is recommended, '
        'but > 0.5 is acceptable.')

    pbc1_detail = (
        'PBC1 (PCR Bottlenecking Coefficient 1, M1/M_distinct) '
        'is the ratio of the number of genomic '
        'locations where exactly one read maps uniquely (M1) to the number of '
        'genomic locations where some reads map (M_distinct). '
        'A PBC1 value in the range 0 - 0.5 is severe bottlenecking, 0.5 - 0.8 '
        'is moderate bottlenecking, 0.8 - 0.9 is mild bottlenecking, and > 0.9 '
        'is no bottlenecking. PBC1 value > 0.9 is recommended, but > 0.8 is '
        'acceptable.')

    pbc2_detail = (
        'PBC2 (PCR Bottlenecking Coefficient 2, M1/M2) is the ratio of the number of '
        'genomic locations where exactly one read maps uniquely (M1) to the number of genomic '
        'locations where two reads map uniquely (M2). '
        'A PBC2 value in the range 0 - 1 is severe bottlenecking, 1 - 3 '
        'is moderate bottlenecking, 3 - 10 is mild bottlenecking, > 10 is '
        'no bottlenecking. PBC2 value > 10 is recommended, but > 3 is acceptable.')

    quality_metrics = alignment_file.get('quality_metrics')
    for metric in quality_metrics:  # ChIP-seq filter quality metric (modERN, ENCODE3), ChIP-seq library quality metric (ENCODE 4)
        if 'NRF' in metric:
            NRF_value = float(metric['NRF'])
            detail = (
                f"{nrf_detail} ENCODE processed {alignment_file['output_type']} file "
                f"{audit_link(path_to_text(alignment_file['@id']), alignment_file['@id'])} "
                f"was generated from a library with "
                f"NRF value of {NRF_value:.2f}."
            )
            if NRF_value < 0.5:
                yield AuditFailure('poor library complexity', detail,
                                   level='NOT_COMPLIANT')
            elif NRF_value >= 0.5 and NRF_value < 0.8:
                yield AuditFailure('moderate library complexity', detail,
                                   level='WARNING')
        if 'PBC1' in metric:
            PBC1_value = float(metric['PBC1'])
            detail = (
                f"{pbc1_detail} ENCODE processed {alignment_file['output_type']} file "
                f"{audit_link(path_to_text(alignment_file['@id']), alignment_file['@id'])} "
                f"was generated from a library with PBC1 value of {PBC1_value:.2f}."
            )
            if PBC1_value < 0.5:
                yield AuditFailure('severe bottlenecking', detail,
                                   level='NOT_COMPLIANT')
            elif PBC1_value >= 0.5 and PBC1_value < 0.9:
                yield AuditFailure('mild to moderate bottlenecking', detail,
                                   level='WARNING')
        if 'PBC2' in metric:
            PBC2_raw_value = metric['PBC2']
            if PBC2_raw_value == 'Infinity':
                PBC2_value = float('inf')
            else:
                PBC2_value = float(metric['PBC2'])
            detail = (
                f"{pbc2_detail} ENCODE processed {alignment_file['output_type']} file "
                f"{audit_link(path_to_text(alignment_file['@id']), alignment_file['@id'])} "
                f"was generated from a library with PBC2 value of {PBC2_value:.2f}."
            )
            if PBC2_value < 1:
                yield AuditFailure('severe bottlenecking', detail,
                                   level='NOT_COMPLIANT')
            elif PBC2_value >= 1 and PBC2_value < 10:
                yield AuditFailure('mild to moderate bottlenecking', detail,
                                   level='WARNING')
    return


def get_file_read_depth_from_alignment(alignment_file, target):
    quality_metrics = alignment_file.get('quality_metrics')

    if not quality_metrics:
        return False

    mapped_run_type = alignment_file.get('mapped_run_type', None)
    if target and \
            'name' in target and target['name'] in ['H3K9me3-human', 'H3K9me3-mouse']:
        # exception (mapped reads). Unfiltered bam QC metrics are used for H3K9me3 only
        for metric in quality_metrics:
            if 'mapped_reads' in metric:  # chip-alignment-quality-metrics (ENCODE 4)
                mappedReads = metric['mapped_reads']
            elif 'mapped' in metric:  # samtools-flagstats-quality-metrics (ENCODE 3)
                mappedReads = metric['mapped']
            if 'processing_stage' in metric and \
                metric['processing_stage'] == 'unfiltered' and \
                    ('mapped' in metric or 'mapped_reads' in metric):
                if mapped_run_type:
                    if mapped_run_type == 'paired-ended':
                        return int(mappedReads / 2)
                    else:
                        return int(mappedReads)
                else:
                    if ('read1' in metric and 'read2' in metric):
                        return int(mappedReads / 2)
                    else:
                        return int(mappedReads)

    else:
        # not exception (useful fragments). All marks other than H3K9me3
        if alignment_file.get('output_type') in [
                'unfiltered alignments',
                'redacted unfiltered alignments'
        ]:
            return False
        for metric in quality_metrics:
            if 'total_reads' in metric:  # chip-alignment-quality-metrics (ENCODE 4)
                totalReads = metric['total_reads']
            elif 'total' in metric:  # samtools-flagstats-quality-metrics (ENCODE 3)
                totalReads = metric['total']
            if ('total' in metric or 'total_reads' in metric) and \
               (('processing_stage' in metric and metric['processing_stage'] == 'filtered') or
                    ('processing_stage' not in metric)):
                if mapped_run_type:
                    if mapped_run_type == 'paired-ended':
                        return int(totalReads / 2)
                    else:
                        return int(totalReads)
                else:
                    if ('read1' in metric and 'read2' in metric):
                        return int(totalReads / 2)
                    else:
                        return int(totalReads)

    return False


def check_file_chip_seq_read_depth(
    file_to_check,
    assay_term_name,
    pipeline_title,
    control_type,
    target,
    read_depth,
    link_to_standards
):
    # added individual file pipeline validation due to the fact that one experiment may
    # have been mapped using 'Raw mapping' and also 'Histone ChIP-seq' - and there is no need to
    # check read depth on Raw files, while it is required for Histone

    marks = pipelines_with_read_depth['ChIP-seq read mapping']
    if not read_depth:
        detail = (
            f"ENCODE processed {file_to_check['output_type']} file "
            f"{audit_link(path_to_text(file_to_check['@id']), file_to_check['@id'])} "
            f"has no read depth information."
        )
        yield AuditFailure('missing read depth', detail, level='INTERNAL_ACTION')
        return

    if target and 'name' in target:
        target_name = target['name']
    elif control_type:
        target_name = control_type
    else:
        return

    if target and 'investigated_as' in target:
        target_investigated_as = target['investigated_as']
    elif control_type:
        target_investigated_as = [control_type]
    else:
        return

    if control_type == 'input library':
        if read_depth >= marks['narrow']['recommended'] and read_depth < marks['broad']['recommended']:
            assembly_detail_phrase = ''
            if 'assembly' in file_to_check:
                assembly_detail_phrase = f"mapped using {file_to_check['assembly']} assembly "
            detail = (
                f"Control {file_to_check['output_type']} file "
                f"{audit_link(path_to_text(file_to_check['@id']), file_to_check['@id'])} "
                f"{assembly_detail_phrase}has {read_depth} usable fragments. "
                f"The minimum ENCODE standard for a control of ChIP-seq assays targeting broad "
                f"histone marks is 20 million usable fragments, the recommended number of usable "
                f"fragments is > 45 million. "
                f"(See {audit_link('ENCODE ChIP-seq data standards', link_to_standards)})"
            )
            yield AuditFailure('insufficient read depth for broad peaks control', detail, level='INTERNAL_ACTION')
        if read_depth < marks['narrow']['recommended']:
            assembly_detail_phrase = ''
            if 'assembly' in file_to_check:
                assembly_detail_phrase = f"mapped using {file_to_check['assembly']} assembly "

            detail = (
                f"Control {file_to_check['output_type']} file "
                f"{audit_link(path_to_text(file_to_check['@id']), file_to_check['@id'])} "
                f"{assembly_detail_phrase}has {read_depth} usable fragments. "
                f"The minimum ENCODE standard for a control of ChIP-seq assays targeting broad "
                f"histone marks is 20 million usable fragments, the recommended number of usable "
                f"fragments is > 45 million. The minimum for a control of ChIP-seq assays "
                f"targeting narrow histone marks or transcription factors is "
                f"10 million usable fragments, the recommended number of usable fragments is "
                f"> 20 million. (See {audit_link('ENCODE ChIP-seq data standards', link_to_standards)})"
            )
            if read_depth >= marks['narrow']['minimal']:
                yield AuditFailure('low read depth', detail, level='WARNING')
            elif read_depth >= marks['narrow']['low'] and read_depth < marks['narrow']['minimal']:
                yield AuditFailure('insufficient read depth',
                                   detail, level='NOT_COMPLIANT')
            else:
                yield AuditFailure('extremely low read depth',
                                   detail, level='ERROR')
    elif 'broad histone mark' in target_investigated_as:
        if target_name in ['H3K9me3-human', 'H3K9me3-mouse'] and read_depth < marks['broad']['recommended']:
            detail = (
                f"Processed {file_to_check['output_type']} file "
                f"{audit_link(path_to_text(file_to_check['@id']), file_to_check['@id'])} "
                f"produced by {assay_term_name} {pipeline_title} pipeline "
                f"has {read_depth} mapped reads. "
                f"The minimum ENCODE standard for each replicate in a ChIP-seq "
                f"experiment targeting {target_name} and investigated as "
                f"a broad histone mark is 35 million mapped reads. "
                f"The recommended value is > 45 million, but > 35 million is "
                f"acceptable. (See {audit_link('ENCODE ChIP-seq data standards', link_to_standards)})"
            )
            if read_depth >= marks['broad']['minimal']:
                yield AuditFailure('low read depth', detail, level='WARNING')
            elif read_depth >= 100 and read_depth < marks['broad']['minimal']:
                yield AuditFailure('insufficient read depth', detail, level='NOT_COMPLIANT')
            elif read_depth < 100:
                yield AuditFailure('extremely low read depth', detail, level='ERROR')
        else:
            detail = (
                f"Processed {file_to_check['output_type']} file "
                f"{audit_link(path_to_text(file_to_check['@id']), file_to_check['@id'])} "
                f"produced by {assay_term_name} {pipeline_title} pipeline "
                f"has {read_depth} usable fragments. "
                f"The minimum ENCODE standard for each replicate in a ChIP-seq "
                f"experiment targeting {target_name} and investigated as "
                f"a broad histone mark is 20 million usable fragments. "
                f"The recommended value is > 45 million, but > 35 million is "
                f"acceptable. (See {audit_link('ENCODE ChIP-seq data standards', link_to_standards)})"
            )

            if read_depth >= marks['broad']['minimal'] and read_depth < marks['broad']['recommended']:
                yield AuditFailure('low read depth', detail, level='WARNING')
            elif read_depth < marks['broad']['minimal'] and read_depth >= marks['broad']['low']:
                yield AuditFailure('insufficient read depth', detail, level='NOT_COMPLIANT')
            elif read_depth < marks['broad']['low']:
                yield AuditFailure('extremely low read depth', detail, level='ERROR')
    elif 'narrow histone mark' in target_investigated_as:
        detail = (
            f"Processed {file_to_check['output_type']} file "
            f"{audit_link(path_to_text(file_to_check['@id']), file_to_check['@id'])} "
            f"produced by {assay_term_name} {pipeline_title} pipeline "
            f"has {read_depth} usable fragments. "
            f"The minimum ENCODE standard for each replicate in a ChIP-seq "
            f"experiment targeting {target_name} and investigated as "
            f"a narrow histone mark is 10 million usable fragments. "
            f"The recommended value is > 20 million, but > 10 million is "
            f"acceptable. (See {audit_link('ENCODE ChIP-seq data standards', link_to_standards)})"
        )
        if read_depth >= marks['narrow']['minimal'] and read_depth < marks['narrow']['recommended']:
            yield AuditFailure('low read depth', detail, level='WARNING')
        elif read_depth < marks['narrow']['minimal'] and read_depth >= marks['narrow']['low']:
            yield AuditFailure('insufficient read depth',
                               detail, level='NOT_COMPLIANT')
        elif read_depth < marks['narrow']['low']:
            yield AuditFailure('extremely low read depth',
                               detail, level='ERROR')
    else:
        detail = (
            f"Processed {file_to_check['output_type']} file "
            f"{audit_link(path_to_text(file_to_check['@id']), file_to_check['@id'])} "
            f"produced by {assay_term_name} {pipeline_title} pipeline "
            f"has {read_depth} usable fragments. "
            f"The minimum ENCODE standard for each replicate in a ChIP-seq "
            f"experiment targeting {target_name} and investigated as "
            f"a transcription factor is 10 million usable fragments. "
            f"The recommended value is > 20 million, but > 10 million is "
            f"acceptable. (See {audit_link('ENCODE ChIP-seq data standards', link_to_standards)} )"
        )
        if read_depth >= marks['TF']['minimal'] and read_depth < marks['TF']['recommended']:
            yield AuditFailure('low read depth', detail, level='WARNING')
        elif read_depth < marks['TF']['minimal'] and read_depth >= marks['TF']['low']:
            yield AuditFailure('insufficient read depth',
                               detail, level='NOT_COMPLIANT')
        elif read_depth < marks['TF']['low']:
            yield AuditFailure('extremely low read depth',
                               detail, level='ERROR')
    return


def check_file_modERN_chip_seq_read_depth(
    file_to_check,
    pipeline_title,
    control_type,
    target,
    read_depth,
    link_to_standards
):
    if target and 'name' in target:
        target_name = target['name']
    elif control_type:
        target_name = control_type
    else:
        return

    modERN_cutoff = pipelines_with_read_depth[
        'Transcription factor ChIP-seq pipeline (modERN)']
    if not read_depth:
        detail = (
            f"ENCODE processed {file_to_check['output_type']} file "
            f"{audit_link(path_to_text(file_to_check['@id']), file_to_check['@id'])} "
            f"has no read depth information."
        )
        yield AuditFailure('missing read depth', detail, level='INTERNAL_ACTION')
        return

    if read_depth < modERN_cutoff:
        first_half_of_detail = (
            f"modERN processed alignment file "
            f"{audit_link(path_to_text(file_to_check['@id']), file_to_check['@id'])} "
            f"has {read_depth} usable fragments. "
        )
        if control_type == 'input library':
            detail = (
                f"{first_half_of_detail} It cannot be used as a control "
                f"in experiments studying transcription factors, which "
                f"require {modERN_cutoff} usable fragments, according to "
                f"the standards defined by the modERN project."
            )
        else:
            detail = (
                f"{first_half_of_detail} Replicates for ChIP-seq assays and "
                f"target {target_name} investigated as transcription factor "
                f"require {modERN_cutoff} usable fragments, according to "
                f"the standards defined by the modERN project."
            )
        yield AuditFailure('insufficient read depth', detail, level='NOT_COMPLIANT')

    return


'''
RNA-seq and transcription assay audits
'''


def audit_missing_read_depth(file):
    detail = (
        f"Processed {file['output_type']} file "
        f"{audit_link(path_to_text(file['@id']), file['@id'])} "
        f"has no read depth information."
    )
    yield AuditFailure('missing read depth', detail, level='INTERNAL_ACTION')
    return


def audit_missing_star_quality_metric(value, alignment_files, pipeline):
    file_ids = [f['@id'] for f in alignment_files]
    file_links = [audit_link(path_to_text(file), file) for file in file_ids]
    detail = (
        f"Alignment file(s) {', '.join(file_links)} in "
        f"{audit_link(path_to_text(value['@id']), value['@id'])} processed by "
        f"{audit_link(path_to_text(value['pipelines'][0]['title']), value['pipelines'][0]['@id'])} "
        f"have no read depth containing quality metric associated with it."
    )
    yield AuditFailure('missing read depth', detail, level='INTERNAL_ACTION')


def check_analysis_bulk_rna_standards(
    value,
    files_structure,
    expected_pipeline_titles,
    link_to_standards,
):
    if value['assembly'] not in ['GRCh38', 'mm10']:
        return
    if len(value['datasets']) != 1:
        return
    else:
        assay_term_name = value['datasets'][0]['assay_term_name']

    pipeline_title = value['pipelines'][0]['title']
    if pipeline_title not in expected_pipeline_titles:
        return

    alignment_files = files_structure.get('alignments').values()
    alignment_files = get_non_tophat_alignment_files(alignment_files)
    gene_quantifications = files_structure.get('gene_quantifications_files').values()

    star_quality_metrics = get_metrics(alignment_files, 'StarQualityMetric')
    if star_quality_metrics is not None and \
            len(star_quality_metrics) > 0:
        for metric in star_quality_metrics:
            alignment_file = files_structure.get('alignments')[metric['quality_metric_of'][0]]
            if 'read_depth' in metric:
                if assay_term_name in [
                    'shRNA knockdown followed by RNA-seq',
                    'siRNA knockdown followed by RNA-seq',
                    'CRISPRi followed by RNA-seq',
                    'CRISPR genome editing followed by RNA-seq'
                ]:
                    yield from check_file_read_depth(
                        alignment_file,
                        metric['read_depth'],
                        upper_threshold=10000000,
                        middle_threshold=10000000,
                        lower_threshold=1000000,
                        assay_term_name=assay_term_name,
                        pipeline_title=pipeline_title,
                        pipeline=value['pipelines'][0],
                        standards_link=link_to_standards)
                elif assay_term_name == 'single-cell RNA sequencing assay':
                    yield from check_file_read_depth(
                        alignment_file,
                        metric['read_depth'],
                        upper_threshold=5000000,
                        middle_threshold=5000000,
                        lower_threshold=500000,
                        assay_term_name=assay_term_name,
                        pipeline_title=pipeline_title,
                        pipeline=value['pipelines'][0],
                        standards_link=link_to_standards)
                else:
                    yield from check_file_read_depth(
                        alignment_file,
                        metric['read_depth'],
                        upper_threshold=30000000,
                        middle_threshold=20000000,
                        lower_threshold=1000000,
                        assay_term_name=assay_term_name,
                        pipeline_title=pipeline_title,
                        pipeline=value['pipelines'][0],
                        standards_link=link_to_standards)
            else:
                yield from audit_missing_read_depth(alignment_file)
    elif alignment_files is not None and len(alignment_files) > 0 and \
            (star_quality_metrics is None or len(star_quality_metrics) == 0):
        yield from audit_missing_star_quality_metric(value, alignment_files, value['pipelines'][0])

    replicated = value['datasets'][0]['replication_type'] if 'replication_type' in value['datasets'][0] else None
    if assay_term_name != 'single-cell RNA sequencing assay':
        mad_metrics = get_metrics(gene_quantifications, 'MadQualityMetric')
        if replicated == 'unreplicated' and len(value['datasets'][0]['replicates']) > 1:
            yield from check_spearman_technical_replicates(
                mad_metrics, pipeline_title, 0.9)
            return
        else:
            yield from check_spearman(mad_metrics, replicated, 0.9, 0.8, pipeline_title)
            return
    return


def check_analysis_small_rna_standards(
    value,
    files_structure,
    expected_pipeline_titles,
    link_to_standards,
):
    if value['assembly'] not in ['GRCh38', 'mm10']:
        return
    if len(value['datasets']) != 1 or len(value['pipelines']) != 1:
        return
    else:
        assay_term_name = value['datasets'][0]['assay_term_name']

    pipeline_title = value['pipelines'][0]['title']
    if pipeline_title not in expected_pipeline_titles:
        return

    alignment_files = files_structure.get('alignments').values()
    alignment_files = get_non_tophat_alignment_files(alignment_files)
    gene_quantifications = files_structure.get('gene_quantifications_files').values()

    star_quality_metrics = get_metrics(alignment_files, 'StarQualityMetric')
    if star_quality_metrics is not None and \
            len(star_quality_metrics) > 0:
        for metric in star_quality_metrics:
            alignment_file = files_structure.get('alignments')[metric['quality_metric_of'][0]]
            if 'read_depth' in metric:
                yield from check_file_read_depth(
                    alignment_file,
                    metric['read_depth'],
                    upper_threshold=30000000,
                    middle_threshold=20000000,
                    lower_threshold=1000000,
                    assay_term_name=assay_term_name,
                    pipeline_title=pipeline_title,
                    pipeline=value['pipelines'][0],
                    standards_link=link_to_standards)
            else:
                yield from audit_missing_read_depth(alignment_file)
    elif alignment_files is not None and len(alignment_files) > 0 and \
            (star_quality_metrics is None or len(star_quality_metrics) == 0):
        yield from audit_missing_star_quality_metric(value, alignment_files, value['pipelines'][0])

    replicated = value['datasets'][0]['replication_type'] if 'replication_type' in value['datasets'][0] else None
    if replicated == 'unreplicated' or replicated is None:
        return

    mad_metrics = get_metrics(gene_quantifications, 'MadQualityMetric')

    yield from check_spearman(mad_metrics, replicated, 0.9, 0.8, pipeline_title)
    return


def check_analysis_cage_rampage_standards(
    value,
    files_structure,
    expected_pipeline_titles,
    link_to_standards,
):
    if value['assembly'] not in ['GRCh38', 'mm10']:
        return
    if len(value['datasets']) != 1 or len(value['pipelines']) != 1:
        return
    else:
        assay_term_name = value['datasets'][0]['assay_term_name']

    pipeline_title = value['pipelines'][0]['title']
    if pipeline_title not in expected_pipeline_titles:
        return

    alignment_files = files_structure.get('alignments').values()
    alignment_files = get_non_tophat_alignment_files(alignment_files)
    gene_quantifications = files_structure.get('gene_quantifications_files').values()

    star_quality_metrics = get_metrics(alignment_files, 'StarQualityMetric')
    if star_quality_metrics is not None and \
            len(star_quality_metrics) > 0:
        for metric in star_quality_metrics:
            alignment_file = files_structure.get('alignments')[metric['quality_metric_of'][0]]
            if 'read_depth' in metric:
                yield from check_file_read_depth(
                    alignment_file, metric['read_depth'],
                    upper_threshold=20000000,
                    middle_threshold=10000000,
                    lower_threshold=1000000,
                    assay_term_name=assay_term_name,
                    pipeline_title=pipeline_title,
                    pipeline=value['pipelines'][0],
                    standards_link=link_to_standards)
            else:
                yield from audit_missing_read_depth(alignment_file)
    elif alignment_files is not None and len(alignment_files) > 0 and \
            (star_quality_metrics is None or len(star_quality_metrics) == 0):
        yield from audit_missing_star_quality_metric(value, alignment_files, value['pipelines'][0])

    replicated = value['datasets'][0]['replication_type'] if 'replication_type' in value['datasets'][0] else None
    if replicated == 'unreplicated' or replicated is None:
        return
    mad_metrics = get_metrics(gene_quantifications, 'MadQualityMetric')

    yield from check_spearman(mad_metrics, replicated, 0.9, 0.8, pipeline_title)
    return


def check_analysis_micro_rna_standards(
    value,
    files_structure,
    expected_pipeline_titles,
    link_to_standards,
):
    if value['assembly'] not in ['GRCh38', 'mm10']:
        return
    if len(value['datasets']) != 1 or len(value['pipelines']) != 1:
        return

    pipeline_title = value['pipelines'][0]['title']
    if pipeline_title not in expected_pipeline_titles:
        return

    alignment_files = files_structure.get('alignments').values()
    alignment_files = get_non_tophat_alignment_files(alignment_files)
    microRNA_quantifications = files_structure.get('microRNA_quantifications_files').values()

    quantification_metrics = get_metrics(microRNA_quantifications, 'MicroRnaQuantificationQualityMetric')
    # Desired annotation does not pertain to alignment files
    alignment_metrics = get_metrics(alignment_files, 'MicroRnaMappingQualityMetric')
    correlation_metrics = get_metrics(microRNA_quantifications, 'CorrelationQualityMetric')

    # Audit Spearman correlations
    yield from check_replicate_metric_dual_threshold(
        correlation_metrics,
        metric_name='Spearman correlation',
        audit_name='replicate concordance',
        upper_limit=0.85,
        lower_limit=0.8,
    )
    # Audit flnc read counts
    yield from check_replicate_metric_dual_threshold(
        alignment_metrics,
        metric_name='aligned_reads',
        audit_name='number of aligned reads',
        upper_limit=5000000,
        lower_limit=3000000,
    )
    # Audit mapping rate
    yield from check_replicate_metric_dual_threshold(
        quantification_metrics,
        metric_name='expressed_mirnas',
        audit_name='microRNAs expressed',
        upper_limit=300,
        lower_limit=200,
    )
    return


def check_analysis_long_read_rna_standards(
    value,
    files_structure,
    expected_pipeline_titles,
    link_to_standards
):
    if value['assembly'] not in ['GRCh38', 'mm10']:
        return
    if len(value['datasets']) != 1 or len(value['pipelines']) != 1:
        return

    pipeline_title = value['pipelines'][0]['title']
    if pipeline_title not in expected_pipeline_titles:
        return

    unfiltered_alignment_files = files_structure.get('unfiltered_alignments').values()
    transcript_quantifications = files_structure.get('transcript_quantifications_files').values()

    quantification_metrics = get_metrics(
        transcript_quantifications,
        'LongReadRnaQuantificationQualityMetric',
    )
    # Desired annotation does not pertain to alignment files
    unfiltered_alignment_metrics = get_metrics(
        unfiltered_alignment_files,
        'LongReadRnaMappingQualityMetric'
    )
    correlation_metrics = get_metrics(
        transcript_quantifications,
        'CorrelationQualityMetric'
    )
    # Audit Spearman correlations
    yield from check_replicate_metric_dual_threshold(
        correlation_metrics,
        metric_name='Spearman correlation',
        audit_name='replicate concordance',
        upper_limit=0.8,
        lower_limit=0.6,
    )
    # Audit flnc read counts
    yield from check_replicate_metric_dual_threshold(
        unfiltered_alignment_metrics,
        metric_name='full_length_non_chimeric_read_count',
        audit_name='sequencing depth',
        upper_limit=600000,
        lower_limit=400000,
        metric_description='full-length non-chimeric (FLNC) read count',
    )
    # Audit mapping rate
    yield from check_replicate_metric_dual_threshold(
        unfiltered_alignment_metrics,
        metric_name='mapping_rate',
        audit_name='mapping rate',
        upper_limit=0.9,
        lower_limit=0.6,
        metric_description='mapping rate',
    )
    # Audit gene quantifications
    yield from check_replicate_metric_dual_threshold(
        quantification_metrics,
        metric_name='genes_detected',
        audit_name='genes detected',
        upper_limit=8000,
        lower_limit=4000,
        metric_description='GENCODE genes detected',
    )
    return


'''
WGBS audits
'''


def check_analysis_wgbs_encode3_standards(
    value,
    files_structure,
    expected_pipeline_titles,
    link_to_standards
):
    if value['assembly'] not in ['GRCh38', 'mm10']:
        return
    if len(value['datasets']) != 1:
        return

    pipeline_titles = [pipeline['title'] for pipeline in value['pipelines']]
    if any(
        title not in expected_pipeline_titles
        for title in pipeline_titles
    ):
        return

    alignment_files = files_structure.get('alignments').values()
    cpg_quantifications = files_structure.get('cpg_quantifications').values()

    pipeline_title = value['pipelines'][0]['title']
    if pipeline_title not in expected_pipeline_titles:
        return

    samtools_stats_metrics = get_metrics(alignment_files, 'SamtoolsStatsQualityMetric')
    bismark_metrics = get_metrics(cpg_quantifications, 'BismarkQualityMetric')
    cpg_metrics = get_metrics(cpg_quantifications, 'CorrelationQualityMetric')
    samtools_metrics = get_metrics(cpg_quantifications, 'SamtoolsFlagstatsQualityMetric')

    read_lengths = []
    for m in samtools_stats_metrics:
        if 'average length' in m:
            read_lengths.append(m['average length'])

    # Check coverage
    for m in samtools_metrics:
        if 'mapped' in m:
            if value['assembly'] == 'mm10':
                coverage = float(m['mapped'] * min(read_lengths)) / 2800000000.0
            elif value['assembly'] == 'GRCh38':
                coverage = float(m['mapped'] * min(read_lengths)) / 3300000000.0
            detail = (
                f"Replicate of experiment processed by {pipeline_title} "
                f"( {audit_link(path_to_text(value['pipelines'][0]['@id']), value['pipelines'][0]['@id'])} ) "
                f"has a coverage of {coverage:.2f}X. The minimum ENCODE "
                f"standard coverage for each replicate in a WGBS assay "
                f"is 25X and the recommended value is > 30X "
                f"(See { audit_link('ENCODE WGBS data standards', link_to_standards)})"
            )
            if coverage < 5:
                yield AuditFailure('extremely low coverage', detail, level='ERROR')
            elif coverage < 25:
                yield AuditFailure('insufficient coverage', detail, level='NOT_COMPLIANT')
            elif coverage < 30:
                yield AuditFailure('low coverage', detail, level='WARNING')

    # Check Pearson correlation
    replicated = value['datasets'][0]['replication_type'] if 'replication_type' in value['datasets'][0] else None
    if replicated and replicated != 'unreplicated':
        yield from check_wgbs_pearson(cpg_metrics, 0.8, pipeline_title)

    # Check lambda C methylation ratio
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
                detail = (
                    f"ENCODE experiment processed by {pipeline_title} "
                    f"pipeline has the following %C methylated in different contexts. "
                    f"lambda C methylated in CpG context was {lambdaCpG}%, "
                    f"lambda C methylated in CHG context was {lambdaCHG}%, "
                    f"lambda C methylated in CHH context was {lambdaCHH}%. "
                    f"The %C methylated in all contexts should be < 1%."
                )
                yield AuditFailure('high lambda C methylation ratio', detail,
                                   level='WARNING')
    return


def check_analysis_wgbs_encode4_standards(
    value,
    files_structure,
    expected_pipeline_titles,
    link_to_standards
):
    if value['assembly'] not in ['GRCh38', 'mm10']:
        return
    if len(value['datasets']) != 1 or len(value['pipelines']) != 1:
        return
    else:
        experiment_award = value['datasets'][0]['award']['rfa']

    pipeline_title = value['pipelines'][0]['title']
    if pipeline_title not in expected_pipeline_titles:
        return

    alignment_files = files_structure.get('alignments').values()
    cpg_quantifications = files_structure.get('cpg_quantifications').values()

    gembs_metrics = get_metrics(alignment_files, 'GembsAlignmentQualityMetric')
    cpg_metrics = get_metrics(cpg_quantifications, 'CpgCorrelationQualityMetric')

    # Check coverage
    for m in gembs_metrics:
        if 'average_coverage' in m:
            coverage = m['average_coverage']
            detail = (
                f"Replicate of experiment processed by {pipeline_title} "
                f"({audit_link(path_to_text(value['pipelines'][0]['@id']), value['pipelines'][0]['@id'])}) "
                f"has a coverage of {coverage:.2f}X. The minimum ENCODE standard coverage for each "
                f"replicate in a WGBS assay is 25X and the recommended value is "
                f"> 30X (See {audit_link('ENCODE WGBS data standards', link_to_standards)})."
            )
            if coverage < 5:
                yield AuditFailure('extremely low coverage', detail, level='ERROR')
            elif coverage < 25:
                yield AuditFailure('insufficient coverage', detail, level='NOT_COMPLIANT')
            elif coverage < 30:
                yield AuditFailure('low coverage', detail, level='WARNING')

    # Check Pearson correlation
    replicated = (
        value['datasets'][0]['replication_type']
        if 'replication_type' in value['datasets'][0] else None)
    if replicated and replicated != 'unreplicated':
        yield from check_wgbs_pearson(cpg_metrics, 0.8, pipeline_title)

    # Check lambda C methylation ratio
    for metric in gembs_metrics:
        if 'conversion_rate' in metric:
            conversion_rate = metric.get('conversion_rate')
            if conversion_rate < 0.98:
                detail = (
                    f'ENCODE experiment processed by {pipeline_title} '
                    f'pipeline has a lambda rate of {conversion_rate}. '
                    f'The lambda conversion rate should be > 99%.'
                )
                yield AuditFailure('low lambda C conversion rate', detail, level='WARNING')
        else:
            severity = 'ERROR'
            if experiment_award == 'Roadmap':
                severity = 'WARNING'
            detail = (
                f'Missing lambda conversion rate for ENCODE experiment '
                f'processed by {pipeline_title} pipeline.'
            )
            yield AuditFailure('missing lambda C conversion rate', detail, level=severity)
    return


def check_wgbs_pearson(cpg_metrics, threshold,  pipeline_title):
    for m in cpg_metrics:
        if 'Pearson correlation' in m:
            if m['Pearson correlation'] < threshold:
                detail = (
                    f"ENCODE experiment processed by {pipeline_title} "
                    f"pipeline has CpG quantification Pearson Correlation Coefficient of "
                    f"{m['Pearson correlation']}, while a value >={threshold} is required."
                )
                yield AuditFailure('insufficient replicate concordance', detail, level='NOT_COMPLIANT')
    return


'''
ATAC-seq audits
'''


def check_analysis_atac_encode4_qc_standards(
    value,
    files_structure,
    expected_pipeline_titles,
    link_to_standards
):
    # https://encodedcc.atlassian.net/browse/ENCD-5255
    # https://encodedcc.atlassian.net/browse/ENCD-5350
    # https://encodedcc.atlassian.net/browse/ENCD-5468
    if value['assembly'] not in ['GRCh38', 'mm10']:
        return
    else:
        assembly = value['assembly']
    if len(value['datasets']) != 1:
        return

    pipeline_titles = [pipeline['title'] for pipeline in value['pipelines']]
    if any(
        title not in expected_pipeline_titles
        for title in pipeline_titles
    ):
        return

    alignment_files = files_structure.get('alignments').values()
    pseudo_replicated_peaks_files = files_structure.get('pseudo_replicated_peaks_files').values()
    all_peaks_files = files_structure.get('overlap_and_idr_peaks').values()
    overlap_peaks_files = []

    # For FRiP: use the pseudoreplicated peaks with multiple biological replicates as input
    replicated = (
        value['datasets'][0]['replication_type']
        if 'replication_type' in value['datasets'][0] else None)
    if replicated and replicated != 'unreplicated':
        for file in pseudo_replicated_peaks_files:
            if 'biological_replicates' in file:
                reps = file['biological_replicates']
                if len(reps) > 1:
                    overlap_peaks_files.append(file)
    else:
        for each in pseudo_replicated_peaks_files:
            overlap_peaks_files.append(each)

    alignment_metrics = get_metrics(alignment_files, 'AtacAlignmentQualityMetric')
    align_enrich_metrics = get_metrics(alignment_files, 'AtacAlignmentEnrichmentQualityMetric')
    library_metrics = get_metrics(alignment_files, 'AtacLibraryQualityMetric')
    peak_enrich_metrics = get_metrics(overlap_peaks_files, 'AtacPeakEnrichmentQualityMetric')

    # Checks in AtacAlignmentQualityMetric
    if alignment_metrics is not None and len(alignment_metrics) > 0:
        for metric in alignment_metrics:
            alignment_file = files_structure.get(
                    'alignments')[metric['quality_metric_of'][0]]
            if 'pct_mapped_reads' in metric and 'quality_metric_of' in metric:
                pct_mapped = str(metric['pct_mapped_reads'])
                detail = (
                    f"Alignment file "
                    f"{audit_link(path_to_text(alignment_file['@id']),alignment_file['@id'])} has "
                    f"{pct_mapped}% mapped reads. According to ENCODE4 standards, ATAC-seq assays "
                    f"processed by the uniform processing pipeline require a minimum of 80% reads "
                    f"mapped. The recommended value is over 95%, but 80-95% is acceptable."
                )
                if metric['pct_mapped_reads'] <= 95 and metric['pct_mapped_reads'] >= 80:
                    yield AuditFailure('acceptable alignment rate', detail, level='WARNING')
                elif metric['pct_mapped_reads'] < 80:
                    yield AuditFailure('low alignment rate', detail, level='NOT_COMPLIANT')

            if 'mapped_reads' in metric:
                mappedReads = metric['mapped_reads']
                mapped_run_type = alignment_file.get('mapped_run_type', None)
                if mapped_run_type:
                    if mapped_run_type == 'paired-ended':
                        mappedReads = int(mappedReads / 2)
                    else:
                        mappedReads = int(mappedReads)
                else:
                    if ('read1' in metric and 'read2' in metric):
                        mappedReads = int(mappedReads / 2)
                    else:
                        mappedReads = int(mappedReads)

                detail = (
                    f"Alignment file {audit_link(path_to_text(alignment_file['@id']),alignment_file['@id'])} "
                    f"has {mappedReads} usable fragments. According to ENCODE4 standards, ATAC-seq "
                    f"assays processed by the uniform processing pipeline should have > 25 million "
                    f"usable fragments. 20-25 million is acceptable and < 15 million is not compliant."
                )

                marks = pipelines_with_read_depth['ATAC-seq (unreplicated)']
                if mappedReads >= marks['minimal'] and mappedReads < marks['recommended']:
                    yield AuditFailure('low read depth', detail, level='WARNING')
                elif mappedReads >= marks['low'] and mappedReads < marks['minimal']:
                    yield AuditFailure('insufficient read depth', detail, level='NOT_COMPLIANT')
                elif mappedReads < marks['low']:
                    yield AuditFailure('extremely low read depth', detail, level='ERROR')

            if 'nfr_peak_exists' in metric:
                if not metric['nfr_peak_exists']:
                    detail = (
                        f"Alignment file {audit_link(path_to_text(alignment_file['@id']),alignment_file['@id'])} "
                        f"indicates that there are no peaks in nucleosome-free regions (NFR); ENCODE4 standards "
                        f"require that ATAC-seq experiments have some overlap between NFR and peaks."
                    )
                    yield AuditFailure('no peaks in nucleosome-free regions', detail, level='NOT_COMPLIANT')

    # Checks in AtacAlignmentEnrichmentQualityMetric
    if align_enrich_metrics is not None and len(align_enrich_metrics) > 0:
        for metric in align_enrich_metrics:
            yield from negative_coefficients(metric, ['NSC', 'RSC'], files_structure)
            if 'tss_enrichment' in metric and 'quality_metric_of' in metric:
                alignment_file = files_structure.get(
                    'alignments')[metric['quality_metric_of'][0]]
                tss = metric['tss_enrichment']

                if assembly and assembly == 'mm10':
                    mouse_detail = (
                        f"Transcription Start Site (TSS) enrichment values for alignments "
                        f"to the mouse genome mm10 are concerning when < 10, acceptable "
                        f"between 10 and 15, and ideal when > 15. ENCODE processed "
                        f"file {audit_link(path_to_text(alignment_file['@id']),alignment_file['@id'])} "
                        f"has a TSS enrichment value of {tss}."
                    )
                    if tss < 10:
                        yield AuditFailure('low TSS enrichment', mouse_detail, level='NOT_COMPLIANT')
                    elif tss >= 10 and tss <= 15:
                        yield AuditFailure('moderate TSS enrichment', mouse_detail, level='WARNING')

                if assembly and assembly == 'GRCh38':
                    human_detail = (
                        f"Transcription Start Site (TSS) enrichment values for alignments "
                        f"to the human genome GRCh38 are concerning when < 5, acceptable "
                        f"between 5 and 7, and ideal when > 7. ENCODE processed "
                        f"file {audit_link(path_to_text(alignment_file['@id']),alignment_file['@id'])} "
                        f"has a TSS enrichment value of {tss}."
                        )
                    if tss < 5:
                        yield AuditFailure('low TSS enrichment', human_detail, level='NOT_COMPLIANT')
                    elif tss >= 5 and tss <= 7:
                        yield AuditFailure('moderate TSS enrichment', human_detail, level='WARNING')

    # Checks in AtacLibraryQualityMetric
    if library_metrics is not None and len(library_metrics) > 0:
        for metric in library_metrics:
            alignment_file = files_structure.get(
                    'alignments')[metric['quality_metric_of'][0]]

            if 'NRF' in metric and 'quality_metric_of' in metric:
                NRF_value = float(metric['NRF'])
                detail = (
                    f"NRF (Non Redundant Fraction) is equal to the result of the "
                    f"division of the number of reads after duplicates removal by "
                    f"the total number of reads. "
                    f"An NRF value < 0.7 is poor complexity, "
                    f"between 0.7 and 0.9 is moderate complexity, "
                    f"and >= 0.9 high complexity. NRF value > 0.9 is recommended, "
                    f"but > 0.7 is acceptable. ENCODE processed file "
                    f"{audit_link(path_to_text(alignment_file['@id']),alignment_file['@id'])} "
                    f"was generated from a library with NRF value of {NRF_value}."
                    )
                if NRF_value < 0.7:
                    yield AuditFailure('poor library complexity', detail, level='NOT_COMPLIANT')
                elif NRF_value >= 0.7 and NRF_value < 0.9:
                    yield AuditFailure('moderate library complexity', detail, level='WARNING')

            if 'PBC1' in metric and 'quality_metric_of' in metric:
                PBC1 = float(metric['PBC1'])
                pbc1_detail = (
                    f"PBC1 (PCR Bottlenecking Coefficient 1, M1/M_distinct) "
                    f"is the ratio of the number of genomic locations where  "
                    f"exactly one read maps uniquely (M1) to the number of "
                    f"genomic locations where some reads map (M_distinct). "
                    f"A PBC1 value in the range 0 - 0.5 is severe bottlenecking, "
                    f"0.5 - 0.8 is moderate bottlenecking, 0.8 - 0.9 is mild "
                    f"bottlenecking, and > 0.9 is no bottlenecking. PBC1 value > "
                    f"0.9 is recommended, but > 0.7 is acceptable. ENCODE processed file "
                    f"{audit_link(path_to_text(alignment_file['@id']),alignment_file['@id'])} "
                    f"was generated from a library with a PBC1 value of {PBC1:.2f}."
                    )
                if PBC1 < 0.7:
                    yield AuditFailure('severe bottlenecking', pbc1_detail, level='NOT_COMPLIANT')
                elif PBC1 >= 0.7 and PBC1 <= 0.9:
                    yield AuditFailure('mild to moderate bottlenecking', pbc1_detail, level='WARNING')

            if 'PBC2' in metric and 'quality_metric_of' in metric:
                PBC2_raw = metric['PBC2']
                if PBC2_raw == 'Infinity':
                    PBC2 = float('inf')
                else:
                    PBC2 = float(metric['PBC2'])
                pbc2_detail = (
                    f"PBC2 (PCR Bottlenecking Coefficient 2, M1/M2) is the ratio of "
                    f"the number of genomic locations where exactly one read maps "
                    f"uniquely (M1) to the number of genomic locations where two reads "
                    f"map uniquely (M2). A PBC2 value in the range 0 - 1 is severe "
                    f"bottlenecking, 1 - 3 is moderate bottlenecking, 3 - 10 is mild "
                    f"bottlenecking, > 10 is no bottlenecking. PBC2 value > 10 is "
                    f"recommended, but > 3 is acceptable. ENCODE processed file "
                    f"{audit_link(path_to_text(alignment_file['@id']),alignment_file['@id'])} "
                    f"was generated from a library with a PBC2 value of {PBC2:.2f}."
                    )
                if PBC2 < 1:
                    yield AuditFailure('severe bottlenecking', pbc2_detail, level='NOT_COMPLIANT')
                elif PBC2 >= 1 and PBC2 <= 3:
                    yield AuditFailure('mild to moderate bottlenecking', pbc2_detail, level='WARNING')

    # Checks in AtacPeakEnrichmentQualityMetric
    if peak_enrich_metrics is not None and len(peak_enrich_metrics) > 0:
        for metric in peak_enrich_metrics:
            overlap_peaks_file = files_structure.get('pseudo_replicated_peaks_files')[metric['quality_metric_of'][0]]
            if 'frip' in metric and 'quality_metric_of' in metric:
                frip = float(metric['frip'])
                detail = (
                    f"According to ENCODE4 standards, overlap peaks files in ATAC-seq assays processed "
                    f"by the uniform processing pipeline should have FRiP (fraction of reads in "
                    f"called peak regions) scores > 0.3. FRiP scores 0.2-0.3 are acceptable, "
                    f"and < 0.2 are not compliant. "
                    f"{audit_link(path_to_text(overlap_peaks_file['@id']),overlap_peaks_file['@id'])} "
                    f" has a FRiP score of {frip:.2f}.")
                if frip < 0.2:
                    yield AuditFailure('low FRiP score', detail, level='NOT_COMPLIANT')
                elif frip >= 0.2 and PBC1 <= 0.3:
                    yield AuditFailure('moderate FRiP score', detail, level='WARNING')

    # Checks in AtacReplicationQualityMetric
    peaks_report = {}
    problematic_files = 0
    for f in all_peaks_files:
        output_type = f['output_type']
        file_list = []
        file_list.append(f)
        f_replication_metrics = get_metrics(file_list, 'AtacReplicationQualityMetric')
        if f_replication_metrics is not None and len(f_replication_metrics) > 0:
            if len(f_replication_metrics) != 1:
                problematic_files += 1
                detail = (
                    f"Multiple AtacReplicationQualityMetric objects are posted on "
                    f"{audit_link(path_to_text(f['@id']),f['@id'])}. Values in these metrics may "
                    f"not be assessed for QC until this is resolved.")
                yield AuditFailure('duplicate QC metrics', detail, level='ERROR')
            elif len(f_replication_metrics) == 1:
                for metric in f_replication_metrics:
                    if 'rescue_ratio' in metric and 'self_consistency_ratio' in metric:
                        rescue = metric['rescue_ratio']
                        self_consistency = metric['self_consistency_ratio']
                        if 'reproducible_peaks' in metric:
                            if output_type in ['pseudoreplicated peaks', 'replicated peaks']:
                                peaks_report['overlap_rep_peaks'] = metric['reproducible_peaks']
                                peaks_report['overlap_rep_peaks_file'] = f['@id']
                                if metric['reproducible_peaks'] > 150000:
                                    peaks_report['overlap_rep_peaks_qual'] = 'pass'
                                if metric['reproducible_peaks'] <= 150000 and metric['reproducible_peaks'] >= 100000:
                                    peaks_report['overlap_rep_peaks_qual'] = 'warning'
                                if metric['reproducible_peaks'] < 100000:
                                    peaks_report['overlap_rep_peaks_qual'] = 'not_compliant'

                            if output_type in ['IDR thresholded peaks', 'conservative IDR thresholded peaks']:
                                peaks_report['idr_rep_peaks'] = metric['reproducible_peaks']
                                peaks_report['idr_rep_peaks_file'] = f['@id']
                                if metric['reproducible_peaks'] > 70000:
                                    peaks_report['idr_rep_peaks_qual'] = 'pass'
                                if metric['reproducible_peaks'] <= 70000 and metric['reproducible_peaks'] >= 50000:
                                    peaks_report['idr_rep_peaks_qual'] = 'warning'
                                if metric['reproducible_peaks'] < 50000:
                                    peaks_report['idr_rep_peaks_qual'] = 'not_compliant'

                        # Replicate concordance is only reported for replicated experiments
                        if replicated and replicated != 'unreplicated':
                            detail = (
                                f"According to ENCODE4 standards, peaks files in replicated "
                                f"ATAC-seq assays processed by the uniform processing pipeline "
                                f"should have a rescue ratio and self-consistency ratio < 2. "
                                f"Having only one of these ratios < 2 is acceptable. "
                                f"{audit_link(path_to_text(f['@id']),f['@id'])} "
                                f" has a rescue ratio of {rescue:.2f} and self-consistency ratio "
                                f"of {self_consistency:.2f}."
                                )
                            if rescue >= 2 and self_consistency >= 2:
                                yield AuditFailure('insufficient replicate concordance', detail, level='NOT_COMPLIANT')
                            elif rescue >= 2 or self_consistency >= 2:
                                yield AuditFailure('borderline replicate concordance', detail, level='WARNING')

    # The better reproducible peaks value in overlap or IDR thresholded peaks is reported
    # This should not be reported if any peaks file has multiple Replication metrics
    if problematic_files == 0:
        detail_items = []
        if 'overlap_rep_peaks' in peaks_report.keys():
            detail_items.append(tuple((str(peaks_report['overlap_rep_peaks']),
                                peaks_report.get('overlap_rep_peaks_file'), ' (overlap peaks)')))
        if 'idr_rep_peaks' in peaks_report.keys():
            detail_items.append(tuple((str(peaks_report['idr_rep_peaks']),
                                peaks_report.get('idr_rep_peaks_file'), ' (IDR thresholded peaks)')))
        audit_peaks = ' and '.join(m[0] for m in detail_items)
        file_links = ' and '.join((audit_link(path_to_text(m[1]), m[1])) + m[2] for m in detail_items)
        detail = (
            f'According to ENCODE4 standards, ATAC-seq assays processed by the uniform processing '
            f'pipeline should have either >150k reproducible peaks in an overlap peaks file, or '
            f'>70k in an IDR thresholded peaks file. 100-150k or 50-70k peaks respectively is '
            f'acceptable, and <100k or <50k respectively is not compliant. '
            f'File(s) {file_links} have {audit_peaks} peaks.')
        if 'pass' in peaks_report.values():
            return
        elif 'warning' in peaks_report.values():
            yield AuditFailure('moderate number of reproducible peaks', detail, level='WARNING')
        elif 'not_compliant' in peaks_report.values():
            yield AuditFailure('insufficient number of reproducible peaks', detail, level='NOT_COMPLIANT')


'''
ChIA-PET audits
'''


def check_analysis_chiapet_encode4_qc_standards(
    value,
    files_structure,
    expected_pipeline_titles,
    link_to_standards
):
    if value['assembly'] not in ['GRCh38', 'mm10']:
        return
    if len(value['datasets']) != 1 or len(value['pipelines']) != 1:
        return

    pipeline_titles = [pipeline['title'] for pipeline in value['pipelines']]
    if any(
        title not in expected_pipeline_titles
        for title in pipeline_titles
    ):
        return

    alignment_files = files_structure.get('alignments').values()
    peak_files = files_structure.get('peaks_files').values()
    chr_int_files = files_structure.get('chromatin_interaction_files').values()

    alignment_metric = get_metrics(alignment_files, 'ChiaPetAlignmentQualityMetric')
    peak_metric = get_metrics(peak_files, 'ChiaPetPeakEnrichmentQualityMetric')
    int_metric = get_metrics(chr_int_files, 'ChiaPetChrInteractionsQualityMetric')

    # Checks in ChiaPetAlignmentQualityMetric
    if alignment_metric is not None and len(alignment_metric) > 0:
        for metric in alignment_metric:
            alignment_file = files_structure.get('alignments')[metric['quality_metric_of'][0]]
            if 'total_rp' in metric and 'quality_metric_of' in metric:
                total_reads = metric['total_rp']
                detail = (
                    f"Alignment file "
                    f"{audit_link(path_to_text(alignment_file['@id']),alignment_file['@id'])} has "
                    f"{total_reads} total read pairs. According to ENCODE4 standards, "
                    f"ChIA-PET assays performed with the in-situ protocol require a minimum of "
                    f"150,000,000 total read pairs. For assays performed with the long reads "
                    f"protocol a minimum of 100,000,000 total read pairs is acceptable."
                )
                if metric['total_rp'] < 150000000:
                    yield AuditFailure('low total read pairs', detail, level='WARNING')

            if 'frp_bl' in metric and 'quality_metric_of' in metric:
                fraction_bl = float(metric['frp_bl'])
                detail = (
                    f"Alignment file "
                    f"{audit_link(path_to_text(alignment_file['@id']),alignment_file['@id'])} has "
                    f"a fraction of read pairs with bridge linker value of {fraction_bl:.2f}. "
                    f"According to ENCODE4 standards, ChIA-PET assays require a minimum "
                    f"value of 0.5 for fraction of read pairs with bridge linker."
                )
                if fraction_bl < 0.5:
                    yield AuditFailure('low fraction of read pairs with linker', detail, level='NOT_COMPLIANT')

            if 'nr_pet' in metric and 'quality_metric_of' in metric:
                nonred_pet = metric['nr_pet']
                detail = (
                    f"Alignment file "
                    f"{audit_link(path_to_text(alignment_file['@id']),alignment_file['@id'])} has "
                    f"{nonred_pet} total non-redundant PET. According to ENCODE4 standards, "
                    f"ChIA-PET assays require a minimum of 10,000,000 non-redundant PET."
                )
                if nonred_pet < 10000000:
                    yield AuditFailure('low non-redundant PET', detail, level='NOT_COMPLIANT')

    # Checks in ChiaPetPeakEnrichmentQualityMetric
    if peak_metric is not None and len(peak_metric) > 0:
        for metric in peak_metric:
            peak_file = files_structure.get('peaks_files')[metric['quality_metric_of'][0]]
            if 'binding_peaks' in metric and 'quality_metric_of' in metric:
                peaks = metric['binding_peaks']
                detail = (
                    f"Peaks file "
                    f"{audit_link(path_to_text(peak_file['@id']),peak_file['@id'])} has "
                    f"{peaks} total peaks. According to ENCODE4 standards, ChIA-PET "
                    f"assays require a minimum of 10,000 protein factor binding peaks."
                )
                if peaks < 10000:
                    yield AuditFailure('low protein factor binding peaks', detail, level='NOT_COMPLIANT')

    # Checks in ChiaPetChrInteractionsQualityMetric
    if int_metric is not None and len(int_metric) > 0:
        for metric in int_metric:
            int_file = files_structure.get('chromatin_interaction_files')[metric['quality_metric_of'][0]]
            if 'intra_inter_pet_ratio' in metric and 'quality_metric_of' in metric:
                int_ratio = float(metric['intra_inter_pet_ratio'])
                detail = (
                    f"Chromatin interactions file "
                    f"{audit_link(path_to_text(int_file['@id']),int_file['@id'])} "
                    f"has a ratio of intra/inter-chr PET of {int_ratio:.2f}. "
                    f"According to ENCODE4 standards, ChIA-PET assays performed "
                    f"with the in-situ protocol require a minimum ratio of 1. "
                    f"For experiments performed with the long reads protocol "
                    f"a ratio below 1 is acceptable."
                )
                if int_ratio < 1:
                    yield AuditFailure('low intra/inter-chr PET ratio', detail, level='WARNING')


'''
Function dispatcher
'''


function_dispatcher = {
    'audit_dnase_footprints': audit_dnase_footprints,
}

function_dispatcher_with_files = {
    'audit_experiment_standards_dispatcher': audit_experiment_standards_dispatcher,
}


@audit_checker(
    'Analysis',
    frame=[
        'files',
        'files.quality_metrics',
        'pipelines',
        'datasets',
        'datasets.award',
        'datasets.target',
    ])
def audit_analysis(value, system):
    if value['status'] in ['deleted', 'revoked']:
        return
    dataset_awards = [x['award']['rfa'] for x in value['datasets']]
    if any(award in ['community', 'GGR', 'modENCODE'] for award in dataset_awards):
        return
    excluded_files = ['revoked']
    if value['status'] == 'revoked':
        excluded_files = []
    files_structure = create_files_mapping(
        value['files'], excluded_files)

    for function_name in function_dispatcher.keys():
        for failure in function_dispatcher[function_name](value, system):
            yield failure

    for function_name in function_dispatcher_with_files.keys():
        yield from function_dispatcher_with_files[function_name](value, system, files_structure)

    return
