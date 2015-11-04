from contentbase import (
    AuditFailure,
    audit_checker,
)
from .conditions import rfa

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

    if value['status'] in ['deleted', 'replaced']:
        return

    if value['file_format'] not in raw_data_formats:
        return

    if 'platform' not in value:
        detail = 'Raw data file {} missing platform information'.format(value['@id'])
        raise AuditFailure('missing platform', detail, level='ERROR')


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
        raise AuditFailure('missing read_length', detail, level='ERROR')


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

    possible_controls = value['dataset'].get('possible_controls')
    biosample = value['dataset'].get('biosample_term_id')

    for ff in value['controlled_by']:
        control_bs = ff['dataset'].get('biosample_term_id')

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
            raise AuditFailure('mismatched controlled_by', detail, level='DCC_ACTION')


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
            detail = 'File {} has a paired-ended run_type but is missing its paired_end value'.format(
                value['@id'])
            raise AuditFailure('missing paired_end', detail, level='DCC_ACTION')

        if (value['paired_end'] == 1) and 'paired_with' not in value:
            detail = 'File {} has a paired-ended run_type but is missing a paired_end=2 mate'.format(
                value['@id'])
            raise AuditFailure('missing mate pair', detail, level='DCC_ACTION')


@audit_checker('file', frame=['quality_metrics',
                              'analysis_step_version',
                              'analysis_step_version.analysis_step',
                              'analysis_step_version.analysis_step.pipelines',
                              'analysis_step_version.software_versions',
                              'analysis_step_version.software_versions.software',
                              'dataset'],
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
        detail = 'ENCODE Processed alignment file {} has no analysis step version'.format(
                value['@id'])
        raise AuditFailure('missing analysis step version', detail, level='DCC_ACTION')

    if 'analysis_step' not in value['analysis_step_version']:
        detail = 'ENCODE Processed alignment file {} has no analysis step in {}'.format(
                value['@id'],
                value['analysis_step_version']['@id'])
        raise AuditFailure('missing analysis step', detail, level='DCC_ACTION')

    if 'pipelines' not in value['analysis_step_version']['analysis_step']:
        detail = 'ENCODE Processed alignment file {} has no pipelines in {}'.format(
                value['@id'],
                value['analysis_step_version']['analysis_step']['@id'])
        raise AuditFailure('missing pipelines in analysis step', detail, level='DCC_ACTION')

    if 'software_versions' not in value['analysis_step_version']:
        detail = 'ENCODE Processed alignment file {} has no software_versions in {}'.format(
                value['@id'],
                value['analysis_step_version']['@id'])
        raise AuditFailure('missing software versions', detail, level='DCC_ACTION')

    if value['analysis_step_version']['software_versions'] == []:
        detail = 'ENCODE Processed alignment file {} has no softwares listed in software_versions, under {}'.format(
                value['@id'],
                value['analysis_step_version']['@id'])
        raise AuditFailure('missing software', detail, level='DCC_ACTION')

    '''
    excluding bam files from TopHat
    '''
    for record in value['analysis_step_version']['software_versions']:   
        if record['software']['title']=='TopHat':
            return

    quality_metrics = value.get('quality_metrics')

    if (quality_metrics is None) or (quality_metrics == []):
        detail = 'ENCODE Processed alignment file {} has no quality_metrics'.format(
            value['@id'])
        raise AuditFailure('missing quality metrics', detail, level='DCC_ACTION')
    read_depth = 0

    for metric in quality_metrics:
        if "uniqueMappedCount" in metric:
            read_depth = metric['uniqueMappedCount']            
            continue
        else:
            if 'Uniquely mapped reads number' in metric:
                read_depth = metric['Uniquely mapped reads number']
                continue
    if read_depth == 0:
        detail = 'ENCODE Processed alignment file {} has no uniquely mapped reads number'.format(
            value['@id'])
        raise AuditFailure('missing read depth', detail, level='DCC_ACTION')

    read_depth_criteria = {
        'Small RNA-seq single-end pipeline': 30000000,
        'RNA-seq of long RNAs (paired-end, stranded)': 30000000,
        'RNA-seq of long RNAs (paired-end, stranded)': 30000000,
        'RAMPAGE (paired-end, stranded)': 25000000,
        'ChIP-seq of histone modifications': 45000000,
    }

    read_depth_special = {
        'shRNA knockdown followed by RNA-seq':10000000,
        'single cell isolation followed by RNA-seq':10000000
    }

    '''
    Finding out if that is shRNA or single Cell to be treated differently
    '''
    shRNAFlag = False
    singleCellFlag = False

    if 'dataset' in value:
        if value['dataset']['assay_term_name'] == 'shRNA knockdown followed by RNA-seq':
            shRNAFlag = True
        if value['dataset']['assay_term_name'] == 'single cell isolation followed by RNA-seq':
            singleCellFlag = True

    for pipeline in value['analysis_step_version']['analysis_step']['pipelines']:
        if pipeline['title'] not in read_depth_criteria:
            return
        if ((singleCellFlag is True) and read_depth < read_depth_special['single cell isolation followed by RNA-seq']) or ((shRNAFlag is True) and read_depth < read_depth_special['shRNA knockdown followed by RNA-seq']):
            if shRNAFlag is True:
                detail = 'ENCODE Processed alignment file {} has {} uniquely mapped reads. Replicates for this assay {} require {}'.format(
                    value['@id'],
                    read_depth,
                    pipeline['title'],
                    read_depth_special['shRNA knockdown followed by RNA-seq'])
            else:
                detail = 'ENCODE Processed alignment file {} has {} uniquely mapped reads. Replicates for this assay {} require {}'.format(
                    value['@id'],
                    read_depth,
                    pipeline['title'],
                    read_depth_special['single cell isolation followed by RNA-seq'])

            raise AuditFailure('insufficient read depth', detail, level='ERROR')

        if (read_depth < read_depth_criteria[pipeline['title']]) and (singleCellFlag is False) and (shRNAFlag is False):
            detail = 'ENCODE Processed alignment file {} has {} uniquely mapped reads. Replicates for this assay {} require {}'.format(
                value['@id'],
                read_depth,
                pipeline['title'],
                read_depth_criteria[pipeline['title']])
            raise AuditFailure('insufficient read depth', detail, level='ERROR')
