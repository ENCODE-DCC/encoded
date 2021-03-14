from snovault import (
    AuditFailure,
    audit_checker,
)
from .formatter import (
    audit_link,
    path_to_text,
)


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


def create_files_mapping(files, excluded_files):
    to_return = {'original_files': {},
                 'fastq_files': {},
                 'alignments': {},
                 'unfiltered_alignments': {},
                 'alignments_unfiltered_alignments': {},
                 'transcriptome_alignments': {},
                 'peaks_files': {},
                 'gene_quantifications_files': {},
                 'transcript_quantifications_files': {},
                 'microRNA_quantifications_files': {},
                 'signal_files': {},
                 'normalized_signal_files': {},
                 'preferred_default_idr_peaks': {},
                 'idr_thresholded_peaks': {},
                 'cpg_quantifications': {},
                 'contributing_files': {},
                 'chromatin_interaction_files': {},
                 'raw_data': {},
                 'processed_data': {},
                 'pseudo_replicated_peaks_files': {},
                 'overlap_and_idr_peaks': {},
                 'excluded_types': excluded_files}
    for file_object in files:
        if file_object['status'] not in excluded_files:
            to_return['original_files'][file_object['@id']] = file_object

            file_format = file_object.get('file_format')
            file_output = file_object.get('output_type')
            file_output_category = file_object.get('output_category')

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
                    file_output and file_output in ['peaks',
                                                    'peaks and background as input for IDR']:
                to_return['peaks_files'][file_object['@id']] = file_object

            if file_output and file_output == 'gene quantifications':
                to_return['gene_quantifications_files'][file_object['@id']
                                                        ] = file_object

            if file_output and file_output == 'transcript quantifications':
                to_return['transcript_quantifications_files'][file_object['@id']] = file_object

            if file_output and file_output == 'microRNA quantifications':
                to_return['microRNA_quantifications_files'][file_object['@id']] = file_object

            if file_output and file_output in ['chromatin interactions', 'long range chromatin interactions']:
                to_return['chromatin_interaction_files'][file_object['@id']] = file_object

            if file_output and file_output == 'signal of unique reads':
                to_return['signal_files'][file_object['@id']] = file_object

            if file_output and file_output == 'read-depth normalized signal':
                to_return['normalized_signal_files'][file_object['@id']] = file_object

            if file_output and file_output == 'optimal IDR thresholded peaks':
                to_return['preferred_default_idr_peaks'][file_object['@id']] = file_object

            if (
                file_object.get('preferred_default')
                and file_output == 'IDR thresholded peaks'
            ):
                to_return['preferred_default_idr_peaks'][
                    file_object['@id']
                ] = file_object
            if file_output and file_output == 'IDR thresholded peaks':
                to_return['idr_thresholded_peaks'][
                    file_object['@id']
                ] = file_object
            if file_output and file_output == 'methylation state at CpG':
                to_return['cpg_quantifications'][file_object['@id']
                                                 ] = file_object
            if (
                file_format
                and file_format == 'bed'
                and file_output
                and file_output == 'pseudoreplicated peaks'
            ):
                to_return['pseudo_replicated_peaks_files'][
                    file_object['@id']
                ] = file_object

            if file_format and file_format == 'bed' and file_output and \
                    file_output in ['replicated peaks', 'pseudoreplicated peaks',
                                    'conservative IDR thresholded peaks',
                                    'IDR thresholded peaks']:
                to_return['overlap_and_idr_peaks'][file_object['@id']] = file_object

            if file_output_category == 'raw data':
                to_return['raw_data'][file_object['@id']] = file_object
            else:
                to_return['processed_data'][file_object['@id']] = file_object
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
        'Roadmap'
    ]:
        return

    if value['pipelines'][0]['title'] == 'DNase-seq pipeline':
        yield from check_analysis_dnase_seq_standards(
            value,
            files_structure,
            ['DNase-seq pipeline'],
            '/data-standards/dnase-seq-encode4/')
        return

    if value['pipelines'][0]['title'] in [
                'DNase-HS pipeline single-end - Version 2',
                'DNase-HS pipeline paired-end - Version 2'
    ]:
        yield from check_analysis_dnase_seq_standards(
            value,
            files_structure,
            [
                'DNase-HS pipeline single-end - Version 2',
                'DNase-HS pipeline paired-end - Version 2'
            ],
            '/data-standards/dnase-seq/')
        return


def check_analysis_dnase_seq_standards(
    value,
    files_structure,
    expected_pipeline_titles,
    link_to_standards
):
    alignment_files = files_structure.get('alignments').values()
    signal_files = files_structure.get('normalized_signal_files').values()

    pipeline_titles = [pipeline['title'] for pipeline in value['pipelines']]
    if len(set(pipeline_titles)) != 1 and pipeline_titles[0] not in expected_pipeline_titles:
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
                    f"( {audit_link(path_to_text(value['pipelines'][0]['@id']), value['pipelines'][0]['@id'])} ) "
                    f"{assemblies_detail(extract_assemblies(alignments_assemblies, file_names))} "
                    f"have a SPOT1 score of {metric['spot1_score']:.2f}. "
                    f"According to ENCODE standards, SPOT1 score of 0.4 or higher is considered "
                    f"a product of high quality data. "
                    f"Any sample with a SPOT1 score <0.3 should be targeted for replacement "
                    f"with a higher quality sample, and a "
                    f"SPOT1 score of 0.25 is considered minimally acceptable "
                    f"SPOT1 score of 0.25 is considered minimally acceptable "
                    f"for rare and hard to find primary tissues. (See "
                    f"{audit_link('ENCODE DNase-seq data standards', link_to_standards)} )"
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
                    f"ENCODE processed signal files {', '.join(file_names_links)} produced by "
                    f"{audit_link(path_to_text(value['pipelines'][0]['title']), value['pipelines'][0]['@id'])} "
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
        'datasets'
    ])
def audit_analysis(value, system):
    excluded_files = ['revoked', 'archived']
    if value['status'] == 'revoked':
        excluded_files = []
    if value['status'] == 'archived':
        excluded_files = ['revoked']
    files_structure = create_files_mapping(
        value['files'], excluded_files)

    for function_name in function_dispatcher.keys():
        for failure in function_dispatcher[function_name](value, system):
            yield failure

    for function_name in function_dispatcher_with_files.keys():
        yield from function_dispatcher_with_files[function_name](value, system, files_structure)

    return
