from contentbase import (
    AuditFailure,
    audit_checker,
)
from .conditions import (
    rfa,
)

current_statuses = ['released', 'in progress']
not_current_statuses = ['revoked', 'obsolete', 'deleted']
raw_data_formats = [
    'fastq',
    'csfasta',
    'csqual',
    'rcc',
    'idat',
    'CEL',
    ]

paired_end_assays = [
    'RNA-PET',
    'ChIA-PET',
    'DNA-PET',
    ]

broadPeaksTargets = [
    'H3K4me1-mouse',
    'H3K36me3-mouse',
    'H3K79me2-mouse',
    'H3K27me3-mouse',
    'H3K9me1-mouse',
    'H3K9me3-mouse',
    'H3K4me1-human',
    'H3K36me3-human',
    'H3K79me2-human',
    'H3K27me3-human',
    'H3K9me1-human',
    'H3K9me3-human',
    'H3F3A-human',
    'H4K20me1-human',
    'H3K79me3-human',
    'H3K79me3-mouse',
    ]


@audit_checker('file', frame=['replicate', 'dataset', 'replicate.experiment'])
def audit_file_replicate_match(value, system):
    '''
    A file's replicate should belong to the same experiment that the file
    does.  These tend to get confused when replacing objects.
    '''

    if value['status'] in ['deleted', 'replaced', 'revoked']:
        return

    if 'replicate' not in value:
        return

    rep_exp = value['replicate']['experiment']['uuid']
    file_exp = value['dataset']['uuid']

    if rep_exp != file_exp:
        detail = 'File {} has a replicate {} in experiment {}'.format(
            value['@id'],
            value['replicate']['@id'],
            value['replicate']['experiment']['@id'])
        raise AuditFailure('mismatched replicate', detail, level='ERROR')


@audit_checker('file', frame='object', condition=rfa('ENCODE3', 'modERN', 'ENCODE2', 'ENCODE2-Mouse'))
def audit_file_platform(value, system):
    '''
    A raw data file should have a platform specified.
    Should be in the schema.
    '''

    if value['status'] in ['deleted', 'replaced', 'revoked']:
        return

    if value['file_format'] not in raw_data_formats:
        return

    if 'platform' not in value:
        detail = 'Raw data file {} missing platform information'.format(value['@id'])
        raise AuditFailure('missing platform', detail, level='NOT_COMPLIANT')


@audit_checker('file', frame='object', condition=rfa('ENCODE3', 'modERN', 'ENCODE2', 'ENCODE2-Mouse'))
def audit_file_read_length(value, system):
    '''
    Reads files should have a read_length
    '''

    if value['status'] in ['deleted', 'replaced', 'revoked']:
        return

    if value['output_type'] != 'reads':
        return

    if 'read_length' not in value:
        detail = 'Reads file {} missing read_length'.format(value['@id'])
        raise AuditFailure('missing read_length', detail, level='DCC_ACTION')


@audit_checker('file',
               frame=['dataset', 'dataset.target', 'controlled_by',
                      'controlled_by.dataset'],
               condition=rfa('ENCODE2', 'ENCODE2-Mouse', 'ENCODE3', 'modERN'))
def audit_file_controlled_by(value, system):
    '''
    A fastq in a ChIP-seq experiment should have a controlled_by
    '''

    if value['status'] in ['deleted', 'replaced', 'revoked']:
        return

    if value['dataset'].get('assay_term_name') not in ['ChIP-seq', 'RAMPAGE', 'CAGE', 'shRNA knockdown followed by RNA-seq']:
        return

    if 'target' in value['dataset'] and 'control' in value['dataset']['target'].get('investigated_as', []):
        return

    if 'controlled_by' not in value:
        value['controlled_by'] = []

    if (value['controlled_by'] == []) and (value['file_format'] in ['fastq']):
        detail = 'Fastq file {} from {} requires controlled_by'.format(
            value['@id'],
            value['dataset']['assay_term_name']
            )
        raise AuditFailure('missing controlled_by', detail, level='NOT_COMPLIANT')
        return

    possible_controls = value['dataset'].get('possible_controls')
    biosample = value['dataset'].get('biosample_term_id')
    run_type = value.get('run_type', None)
    read_length = value.get('read_length', None)

    if value['controlled_by']:
        for ff in value['controlled_by']:
            control_bs = ff['dataset'].get('biosample_term_id')
            control_run = ff.get('run_type', None)
            control_length = ff.get('read_length', None)

            if control_bs != biosample:
                detail = 'File {} has a controlled_by file {} with conflicting biosample {}'.format(
                    value['@id'],
                    ff['@id'],
                    control_bs)
                raise AuditFailure('mismatched controlled_by', detail, level='ERROR')
                return

            if ff['file_format'] != value['file_format']:
                detail = 'File {} with file_format {} has a controlled_by file {} with file_format {}'.format(
                    value['@id'],
                    value['file_format'],
                    ff['@id'],
                    ff['file_format']
                    )
                raise AuditFailure('mismatched controlled_by', detail, level='ERROR')

            if (possible_controls is None) or (ff['dataset']['@id'] not in possible_controls):
                detail = 'File {} has a controlled_by file {} with a dataset {} that is not in possible_controls'.format(
                    value['@id'],
                    ff['@id'],
                    ff['dataset']['@id']
                    )
                raise AuditFailure('mismatched controlled_by', detail, level='ERROR')

            if (run_type is None) or (control_run is None):
                continue

            if (read_length is None) or (control_length is None):
                continue

            if run_type != control_run:
                detail = 'File {} is {} but its control file {} is {}'.format(
                    value['@id'],
                    run_type,
                    ff['@id'],
                    control_run
                    )
                raise AuditFailure('mismatched controlled_by run_type', detail, level='WARNING')

            if read_length != control_length:
                detail = 'File {} is {} but its control file {} is {}'.format(
                    value['@id'],
                    value['read_length'],
                    ff['@id'],
                    ff['read_length']
                    )
                raise AuditFailure('mismatched controlled_by read length', detail, level='WARNING')



@audit_checker('file', frame='object', condition=rfa('ENCODE3', 'modERN'))
def audit_file_flowcells(value, system):
    '''
    A fastq file could have its flowcell details.
    Don't bother to check anything but ENCODE3
    '''

    if value['status'] in ['deleted', 'replaced', 'revoked']:
        return

    if value['file_format'] not in ['fastq']:
        return

    if 'flowcell_details' not in value or (value['flowcell_details'] == []):
        detail = 'Fastq file {} is missing flowcell_details'.format(value['@id'])
        raise AuditFailure('missing flowcell_details', detail, level='WARNING')


@audit_checker('file', frame='object',)
def audit_run_type(value, system):
    '''
    A fastq file or a fasta file need to specify run_type.
    This was attempted to be a dependancy and didn't happen.
    '''

    if value['status'] in ['deleted', 'replaced', 'revoked']:
        return

    if value['file_format'] not in ['fastq']:
        return

    if 'run_type' not in value:
        detail = 'File {} has file_format {}. It requires a value for run_type'.format(
            value['@id'],
            value['file_format'])
        raise AuditFailure('missing run_type', detail, level='NOT_COMPLIANT')


@audit_checker('file', frame=['paired_with'],)
def audit_paired_with(value, system):
    '''
    A file with a paired_end needs a paired_with.
    Should be handled in the schema.
    A paired_with should be the same replicate
    '''

    if value['status'] in ['deleted', 'replaced', 'revoked']:
        return

    if 'paired_end' not in value:
        return

    if 'paired_with' not in value:
        detail = 'File {} has paired_end = {}. It requires a paired file'.format(
            value['@id'],
            value['paired_end'])
        raise AuditFailure('missing paired_with', detail, level='NOT_COMPLIANT')

    if 'replicate' not in value['paired_with']:
        return

    if 'replicate' not in value:
        detail = 'File {} has paired_end = {}. It requires a replicate'.format(
            value['@id'],
            value['paired_end'])
        raise AuditFailure('missing replicate', detail, level='DCC_ACTION')

    if value['replicate'] != value['paired_with']['replicate']:
        detail = 'File {} has replicate {}. It is paired_with file {} with replicate {}'.format(
            value['@id'],
            value.get('replicate'),
            value['paired_with']['@id'],
            value['paired_with'].get('replicate'))
        raise AuditFailure('mismatched paired_with', detail, level='ERROR')

    if value['paired_end'] == '1':
        context = system['context']
        paired_with = context.get_rev_links('paired_with')
        if len(paired_with) > 1:
            detail = 'Paired end 1 file {} paired_with by multiple paired end 2 files: {!r}'.format(
                value['@id'],
                paired_with,
            )
            raise AuditFailure('multiple paired_with', detail, level='ERROR')


@audit_checker('file', frame=['step_run',
                              'dataset'], condition=rfa('modERN'))
def audit_modERN_ChIP_pipeline_steps(value, system):

    expt = value['dataset']
    if 'Experiment' not in expt['@type']:
        return

    if expt['assay_term_id'] != 'OBI:0000716':
        return

    if value['file_format'] == 'fastq':
        return

    if 'step_run' not in value:
        detail = 'File {} is missing a step_run'.format(value['@id'])
        yield AuditFailure('missing step_run', detail, level='WARNING')
        return

    if (value['file_format'] != 'fastq') and ('derived_from' not in value):
        detail = 'File {} is missing its derived_from'.format(value['@id'])
        yield AuditFailure('missing derived_from', detail, level='WARNING')

    step = value['step_run']
    if (value['file_format'] == 'bam') and step['aliases'][0] != 'modern:chip-seq-bwa-alignment-step-run-v-1-virtual':
        detail = 'Bam {} is linked to the wrong step_run: {}'.format(value['@id'], step['aliases'][0])
        yield AuditFailure('wrong step_run ChIP-seq bam', detail, level='WARNING')

    if (value['output_type'] == 'normalized signal of all reads'):
        if not ((step['aliases'][0] != 'modern:chip-seq-unique-read-signal-generation-step-run-v-1-virtual') or (step['aliases'][0] != 'modern:chip-seq-replicate-pooled-unique-read-signal-generation-step-run-v-1-virtual')):
            detail = 'Normalized signal of all reads {} is linked to the wrong step_run: {}'.format(value['@id'], step['aliases'][0])
            yield AuditFailure('wrong step_run for unique signal', detail, level='WARNING')

    if (value['output_type']) == 'read-depth normalized signal':
        if not ((step['aliases'][0] != 'modern:chip-seq-read-depth-normalized-signal-generation-step-run-v-1-virtual') or (step['aliases'][0] != 'modern:chip-seq-replicate-pooled-read-depth-normalized-signal-generation-step-run-v-1-virtual')):
            detail = 'Read depth normalized signal {} is linked to the wrong step_run: {}'.format(value['@id'], step['aliases'][0])
            yield AuditFailure('wrong step_run for depth signal', detail, level='WARNING')

    if (value['output_type']) == 'control normalized signal':
        if not ((step['aliases'][0] != 'modern:chip-seq-control-normalized-signal-generation-step-run-v-1-virtual') or (step['aliases'][0] != 'modern:chip-seq-replicate-pooled-control-normalized-signal-generation-step-run-v-1-virtual')):
            detail = 'Control normalized signal {} is linked to the wrong step_run: {}'.format(value['@id'], step['aliases'][0])
            yield AuditFailure('wrong step_run for control signal', detail, level='WARNING')

    if (value['file_format'] == 'bigBed'):
        if not ((step['aliases'][0] != 'modern:chip-seq-peaks-to-bigbed-step-run-v-1-virtual') or (step['aliases'][0] != 'modern:chip-seq-optimal-idr-thresholded-peaks-to-bigbed-step-run-v-1-virtual')):
            detail = 'bigBed {} is linked to the wrong step_run: {}'.format(value['@id'], step['aliases'][0])
            yield AuditFailure('wrong step_run for bigBed peaks', detail, level='WARNING')

    if (value['output_type'] == 'peaks') and (value['file_format'] == 'bed'):
        if (value['file_format_type'] == 'narrowPeak') and (step['aliases'][0] != 'modern:chip-seq-spp-peak-calling-step-run-v-1-virtual'):
            detail = 'Peaks {} is linked to the wrong step_run: {}'.format(value['@id'], step['aliases'][0])
            yield AuditFailure('wrong step_run for peaks', detail, level='WARNING')

    if (value['output_type'] == 'optimal idr thresholded peaks') and (value['file_format'] == 'bed'):
        if (value['file_format_type'] == 'narrowPeak') and (step['aliases'][0] != 'modern:chip-seq-optimal-idr-step-run-v-1-virtual'):
            detail = 'Optimal IDR thresholded peaks {} is linked to the wrong step_run: {}'.format(value['@id'], step['aliases'][0])
            yield AuditFailure('wrong step_run for IDR peaks', detail, level='WARNING')


@audit_checker('file', frame='object')
def audit_file_size(value, system):

    if value['status'] in ['deleted', 'replaced', 'uploading', 'revoked']:
        return

    if 'file_size' not in value:
        detail = 'File {} requires a value for file_size'.format(value['@id'])
        raise AuditFailure('missing file_size', detail, level='DCC_ACTION')


@audit_checker('file', frame=['file_format_specifications'],)
def audit_file_format_specifications(value, system):

    for doc in value.get('file_format_specifications', []):
        if doc['document_type'] != "file format specification":
            detail = 'File {} has document {} not of type file format specification'.format(
                value['@id'],
                doc['@id']
                )
            raise AuditFailure('wrong document_type', detail, level='ERROR')


@audit_checker('file', frame='object')
def audit_file_paired_ended_run_type(value, system):
    '''
    Audit to catch those files that were upgraded to have run_type = paired ended
    resulting from its migration out of replicate but lack the paired_end property
    to specify which read it is. This audit will also catch the case where run_type
    = paired-ended but there is no paired_end = 2 due to registeration error.
    '''

    if value['status'] in ['deleted', 'replaced', 'revoked', 'upload failed']:
        return

    if value['file_format'] not in ['fastq', 'fasta', 'csfasta']:
        return

    if (value['output_type'] == 'reads') and (value.get('run_type') == 'paired-ended'):
        if 'paired_end' not in value:
            detail = 'File {} has a paired-ended run_type '.format(value['@id']) + \
                     'but is missing its paired_end value'
            raise AuditFailure('missing paired_end', detail, level='DCC_ACTION')

        if (value['paired_end'] == 1) and 'paired_with' not in value:
            detail = 'File {} has a paired-ended '.format(value['@id']) + \
                     'run_type but is missing a paired_end=2 mate'
            raise AuditFailure('missing mate pair', detail, level='DCC_ACTION')


@audit_checker('file', frame=['quality_metrics',
                              'analysis_step_version',
                              'analysis_step_version.analysis_step',
                              'analysis_step_version.analysis_step.pipelines',
                              'analysis_step_version.software_versions',
                              'analysis_step_version.software_versions.software',
                              'dataset',
                              'dataset.target',
                              'derived_from'],
               condition=rfa('ENCODE3', 'ENCODE'))
def audit_file_read_depth(value, system):
    '''
    An alignment file from the ENCODE Processing Pipeline should have read depth
    in accordance with the criteria
    '''

    if value['status'] in ['deleted', 'replaced', 'revoked']:
        return

    if value['file_format'] != 'bam':
        return

    if value['output_type'] == 'transcriptome alignments':
        return

    if value['lab'] != '/labs/encode-processing-pipeline/':
        return

    if 'analysis_step_version' not in value:
        detail = 'ENCODE Processed alignment file {} has '.format(value['@id']) + \
                 'no analysis step version'
        yield AuditFailure('missing analysis step version', detail, level='DCC_ACTION')
        return

    if 'analysis_step' not in value['analysis_step_version']:
        detail = 'ENCODE Processed alignment file {} has '.format(value['@id']) + \
                 'no analysis step in {}'.format(value['analysis_step_version']['@id'])
        yield AuditFailure('missing analysis step', detail, level='DCC_ACTION')
        return

    if 'pipelines' not in value['analysis_step_version']['analysis_step']:
        detail = 'ENCODE Processed alignment file {} has '.format(value['@id']) + \
                 'no pipelines in {}'.format(value['analysis_step_version']['analysis_step']['@id'])
        yield AuditFailure('missing pipelines in analysis step', detail, level='DCC_ACTION')
        return

    if 'software_versions' not in value['analysis_step_version']:
        detail = 'ENCODE Processed alignment file {} has '.format(value['@id']) + \
                 'no software_versions in {}'.format(value['analysis_step_version']['@id'])
        yield AuditFailure('missing software versions', detail, level='DCC_ACTION')
        return

    if value['analysis_step_version']['software_versions'] == []:
        detail = 'ENCODE Processed alignment file {} has no '.format(value['@id']) + \
                 'softwares listed in software_versions,' + \
                 ' under {}'.format(value['analysis_step_version']['@id'])
        yield AuditFailure('missing software', detail, level='DCC_ACTION')
        return

    '''
    excluding bam files from TopHat
    '''
    for record in value['analysis_step_version']['software_versions']:
        if record['software']['title'] == 'TopHat':
            return

    quality_metrics = value.get('quality_metrics')

    if (quality_metrics is None) or (quality_metrics == []):
        detail = 'ENCODE Processed alignment file {} has no quality_metrics'.format(
            value['@id'])
        yield AuditFailure('missing quality metrics', detail, level='DCC_ACTION')
        return

    read_depth = 0

    derived_from_files = value.get('derived_from')
    if (derived_from_files is None) or (derived_from_files == []):
        detail = 'ENCODE Processed alignment file {} has no derived_from files'.format(
            value['@id'])
        yield AuditFailure('missing derived_from files', detail, level='DCC_ACTION')
        return

    paring_status_detected = False
    for derived_from_file in derived_from_files:
        if 'file_type' in derived_from_file and derived_from_file['file_type'] == 'fastq' and \
           'run_type' in derived_from_file:
            if derived_from_file['run_type'] == 'single-ended':
                paired_ended_status = False
                paring_status_detected = True
                break
            else:
                if derived_from_file['run_type'] == 'paired-ended':
                    paired_ended_status = True
                    paring_status_detected = True
                    break

    if paring_status_detected is False:
        detail = 'ENCODE Processed alignment file {} has no run_type in derived_from files'.format(
            value['@id'])
        yield AuditFailure('missing run_type in derived_from files', detail, level='DCC_ACTION')
        return

    for metric in quality_metrics:
        if 'Uniquely mapped reads number' in metric:  # start_quality_metric.json
            read_depth = metric['Uniquely mapped reads number']
            continue
        else:
            if "total" in metric:
                if paired_ended_status is False:
                    read_depth = metric['total']
                else:
                    read_depth = metric['total']/2
                continue

    if read_depth == 0:
        detail = 'ENCODE Processed alignment file {} has no uniquely mapped reads number'.format(
            value['@id'])
        yield AuditFailure('missing read depth', detail, level='DCC_ACTION')
        return

    special_assay_name = 'empty'
    target_name = 'empty'

    if 'dataset' in value:
        if (value['dataset']['assay_term_name'] == 'shRNA knockdown followed by RNA-seq') or \
           (value['dataset']['assay_term_name'] == 'single cell isolation followed by RNA-seq'):
            special_assay_name = value['dataset']['assay_term_name']
        if 'target' in value['dataset']:
            target_name = value['dataset']['target']['name']

    pipeline_titles = [
        'Small RNA-seq single-end pipeline',
        'RNA-seq of long RNAs (paired-end, stranded)',
        'RNA-seq of long RNAs (single-end, unstranded)',
        'RAMPAGE (paired-end, stranded)',
        'Histone ChIP-seq'
    ]

    read_depths_special = {
        'shRNA knockdown followed by RNA-seq': 10000000,
        'single cell isolation followed by RNA-seq': 5000000
    }
    read_depths = {
        'Small RNA-seq single-end pipeline': 30000000,
        'RNA-seq of long RNAs (paired-end, stranded)': 30000000,
        'RNA-seq of long RNAs (single-end, unstranded)': 30000000,
        'RAMPAGE (paired-end, stranded)': 25000000
    }

    marks = {
        'narrow': 20000000,
        'broad': 45000000
    }

    for pipeline in value['analysis_step_version']['analysis_step']['pipelines']:
        if pipeline['title'] not in pipeline_titles:
            return
        if pipeline['title'] == 'Histone ChIP-seq':  # do the chipseq narrow broad ENCODE3
            if target_name in ['Control-human', 'Control-mouse']:
                if read_depth < marks['broad']:
                    detail = 'ENCODE Processed alignment file {} has {} '.format(value['@id'],
                                                                                 read_depth) + \
                             'uniquely mapped reads. Replicates for this assay ' + \
                             '{} and target {} require '.format(pipeline['title'], target_name) + \
                             '{} (broad-marks)'.format(marks['broad'])
                    yield AuditFailure('insufficient read depth', detail, level='ERROR')
                if read_depth < marks['narrow']:
                    detail = 'ENCODE Processed alignment file {} has {} '.format(value['@id'],
                                                                                 read_depth) + \
                             'uniquely mapped reads. Replicates for this assay ' + \
                             '{} and target {} require '.format(pipeline['title'], target_name) + \
                             '{} (narrow-marks)'.format(marks['narrow'])
                    yield AuditFailure('insufficient read depth', detail, level='ERROR')
                return
            if target_name == 'empty':
                detail = 'ENCODE Processed alignment file {} '.format(value['@id']) + \
                         'belongs to ChIP-seq experiment {} '.format(value['dataset']['@id']) + \
                         'with no target specified.'
                yield AuditFailure('ChIP-seq missing target', detail, level='ERROR')
                return
            if target_name in broadPeaksTargets:
                if read_depth < marks['broad']:
                    detail = 'ENCODE Processed alignment file {} has {} '.format(value['@id'],
                                                                                 read_depth) + \
                             'uniquely mapped reads. Replicates for this assay ' + \
                             '{} and target {} require '.format(pipeline['title'], target_name) + \
                             '{}'.format(marks['broad'])
                    yield AuditFailure('insufficient read depth', detail, level='ERROR')
                    return
            else:
                if read_depth < marks['narrow']:
                    detail = 'ENCODE Processed alignment file {} has {} '.format(value['@id'],
                                                                                 read_depth) + \
                             'uniquely mapped reads. Replicates for this assay ' + \
                             '{} and target {} require '.format(pipeline['title'], target_name) + \
                             '{}'.format(marks['narrow'])
                    yield AuditFailure('insufficient read depth', detail, level='ERROR')
                    return
        else:
            if special_assay_name != 'empty':  # either shRNA or single cell
                if read_depth < read_depths_special[special_assay_name]:
                    detail = 'ENCODE Processed alignment file {} has {} '.format(value['@id'],
                                                                                 read_depth) + \
                             'uniquely mapped reads. Replicates for this assay ' + \
                             '{} require '.format(pipeline['title']) + \
                             '{}'.format(read_depths_special[special_assay_name])
                    yield AuditFailure('insufficient read depth', detail, level='ERROR')
                    return
            else:
                if (read_depth < read_depths[pipeline['title']]):
                    detail = 'ENCODE Processed alignment file {} has {} '.format(value['@id'], read_depth) + \
                             'uniquely mapped reads. Replicates for this ' + \
                             'assay {} require {}'.format(pipeline['title'],
                                                          read_depths[pipeline['title']])
                    yield AuditFailure('insufficient read depth', detail, level='ERROR')
                    return


@audit_checker('file', frame=['quality_metrics',
                              'analysis_step_version',
                              'analysis_step_version.analysis_step',
                              'analysis_step_version.analysis_step.pipelines',
                              'analysis_step_version.software_versions',
                              'analysis_step_version.software_versions.software',
                              'dataset'],
               condition=rfa('ENCODE3', 'ENCODE'))
def audit_file_mad_qc_spearman_correlation(value, system):
    '''
    A gene quantification file from the ENCODE Processing Pipeline should have a mad QC
    in accordance with the criteria
    '''

    if value['status'] in ['deleted', 'replaced', 'revoked']:
        return

    if value['output_type'] != 'gene quantifications':
        return

    if value['lab'] != '/labs/encode-processing-pipeline/':
        return

    if 'analysis_step_version' not in value:
        detail = 'ENCODE Processed gene quantification file {} has no analysis step version'.format(
            value['@id'])
        raise AuditFailure('missing analysis step version', detail, level='DCC_ACTION')

    if 'analysis_step' not in value['analysis_step_version']:
        detail = 'ENCODE Processed gene quantification file {} has no analysis step in {}'.format(
            value['@id'],
            value['analysis_step_version']['@id'])
        raise AuditFailure('missing analysis step', detail, level='DCC_ACTION')

    if 'pipelines' not in value['analysis_step_version']['analysis_step']:
        detail = 'ENCODE Processed gene quantification file {} has no pipelines in {}'.format(
            value['@id'],
            value['analysis_step_version']['analysis_step']['@id'])
        raise AuditFailure('missing pipelines in analysis step', detail, level='DCC_ACTION')

    quality_metrics = value.get('quality_metrics')

    if (quality_metrics is None) or (quality_metrics == []):
        detail = 'ENCODE Processed gene quantification file {} has no quality_metrics'.format(
            value['@id'])
        raise AuditFailure('missing quality metrics', detail, level='DCC_ACTION')

    spearman_correlation = False
    for metric in quality_metrics:
        if 'Spearman correlation' in metric:
            spearman_correlation = metric['Spearman correlation']
            break
    if spearman_correlation is False:
        detail = 'ENCODE Processed gene quantification file {} '.format(value['@id']) + \
                 'has no MAD quality metric'
        raise AuditFailure('missing Spearman correlation', detail, level='DCC_ACTION')

    spearman_pipelines = ['RAMPAGE (paired-end, stranded)',
                          'Small RNA-seq single-end pipeline',
                          'RNA-seq of long RNAs (single-end, unstranded)',
                          'RNA-seq of long RNAs (paired-end, stranded)']

    experiment_replication_type = 'isogenic'
    if 'dataset' in value:
        if 'replication_type' in value['dataset']:
            if value['dataset']['replication_type'] in ['anisogenic',
                                                        'anisogenic, sex-matched and age-matched',
                                                        'anisogenic, age-matched',
                                                        'anisogenic, sex-matched']:
                experiment_replication_type = 'anisogenic'
                required_value = 0.8
            else:
                required_value = 0.9

    for pipeline in value['analysis_step_version']['analysis_step']['pipelines']:
        if pipeline['title'] in spearman_pipelines:
            if spearman_correlation <= required_value:
                detail = 'ENCODE Processed gene quantification file {} '.format(value['@id']) + \
                         'has Spearman correlaton of {} '.format(spearman_correlation) + \
                         ', gene quantification file for {}'.format(experiment_replication_type) + \
                         ' assay {} '.format(pipeline['title']) + \
                         'require {}'.format(required_value)
                raise AuditFailure('insufficient spearman correlation', detail,
                                   level='NOT_COMPLIANT')
