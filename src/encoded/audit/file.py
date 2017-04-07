from snovault import (
    AuditFailure,
    audit_checker,
)
from .conditions import (
    rfa,
)
from .standards_data import pipelines_with_read_depth

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


@audit_checker('File', frame=[
    'analysis_step_version',
    'analysis_step_version.analysis_step',
    'analysis_step_version.analysis_step.pipelines'])
def audit_file_pipeline_status(value, system):
    if value['status'] not in ['released']:
        return
    if 'analysis_step_version' in value and \
       'analysis_step' in value['analysis_step_version'] and \
       'pipelines' in value['analysis_step_version']['analysis_step']:
        for p in value['analysis_step_version']['analysis_step']['pipelines']:
            if p['status'] not in ['active']:
                detail = 'File {} with a status of {} '.format(value['@id'], value['status']) + \
                         'is associated with a pipeline {} '.format(p['@id']) + \
                         'that has a status of {}.'.format(p['status'])
                yield AuditFailure('inconsistent pipeline status',
                                   detail, level='INTERNAL_ACTION')

'''
@audit_checker('File', frame=['derived_from'])
def audit_file_md5sum_integrity(value, system):
    if value['status'] in ['deleted', 'replaced', 'revoked']:
        return
    md5sum = value['md5sum']
    try:
        hexval = int(md5sum, 16)
        if len(md5sum) != 32:
            detail = 'File {} '.format(value['@id']) + \
                     'has an md5sum value of {}, '.format(md5sum) + \
                     'which is not 32 characters long.'
            yield AuditFailure('inconsistent md5sum',
                               detail, level='INTERNAL_ACTION')
    except ValueError:
        detail = 'File {} '.format(value['@id']) + \
                 'has an md5sum value of {}, '.format(md5sum) + \
                 'which is not a valid hexadecimal number.'
        yield AuditFailure('inconsistent md5sum',
                           detail, level='INTERNAL_ACTION')
'''


@audit_checker('File', frame=['derived_from'])
def audit_file_bam_derived_from(value, system):
    if value['file_format'] != 'bam':
        return
    if value['status'] in ['deleted', 'replaced', 'revoked']:
        return
    if 'derived_from' not in value or \
       'derived_from' in value and len(value['derived_from']) == 0:
        return
    derived_from_files = value.get('derived_from')
    fastq_bam_counter = 0
    for f in derived_from_files:
        if f['status'] not in ['deleted', 'replaced', 'revoked'] and \
           (f['file_format'] == 'bam' or
            f['file_format'] == 'fastq' or (f['file_format'] == 'fasta' and
                                            f['output_type'] == 'reads' and
                                            f['output_category'] == 'raw data')):
            fastq_bam_counter += 1
            if f['dataset'] != value['dataset']:
                detail = 'derived_from is a list of files that were used to create a given file; ' + \
                         'for example, fastq file(s) will appear in the derived_from list of an alignments file. ' + \
                         'Alignments file {} '.format(value['@id']) + \
                         'from experiment {} '.format(value['dataset']) + \
                         'specifies a file {} '.format(f['@id']) + \
                         'from a different experiment {} '.format(f['dataset']) + \
                         'in its derived_from list.'
                yield AuditFailure('inconsistent derived_from',
                                   detail, level='INTERNAL_ACTION')
    if fastq_bam_counter == 0:
        detail = 'derived_from is a list of files that were used to create a given file; ' + \
                 'for example, fastq file(s) will appear in the derived_from list of an alignments file. ' + \
                 'Alignments file {} '.format(value['@id']) + \
                 'is missing the requisite file specification in its derived_from list.'
        yield AuditFailure('missing derived_from',
                           detail, level='INTERNAL_ACTION')


@audit_checker('File', frame=['object'],
               condition=rfa('ENCODE3',
                             'modENCODE',
                             'modERN',
                             'GGR'))
def audit_file_processed_empty_derived_from(value, system):
    if value['output_category'] in ['raw data',
                                    'reference']:
        return
    if value['status'] in ['deleted', 'replaced', 'revoked']:
            return
    if 'derived_from' not in value or \
       'derived_from' in value and len(value['derived_from']) == 0:
            detail = 'derived_from is a list of files that were used to create a given file; ' + \
                     'for example, fastq file(s) will appear in the derived_from list of an alignments file. ' + \
                     'Processed file {} '.format(value['@id']) + \
                     'is missing the requisite file specification in its derived_from list.'
            yield AuditFailure('missing derived_from',
                               detail, level='INTERNAL_ACTION')
            return


@audit_checker('File', frame=['derived_from'])
def audit_file_derived_from_revoked(value, system):
    if value['status'] in ['deleted', 'replaced', 'revoked']:
            return
    if 'derived_from' in value and len(value['derived_from']) > 0:
        for f in value['derived_from']:
            if f['status'] == 'revoked':
                detail = 'The file {} '.format(value['@id']) + \
                         'with a status {} '.format(value['status']) + \
                         'was derived from file {} '.format(f['@id']) + \
                         'that has a status \'revoked\'.'
                yield AuditFailure('mismatched file status',
                                   detail, level='INTERNAL_ACTION')
                return


@audit_checker('file', frame=['derived_from'])
def audit_file_assembly(value, system):
    if value['status'] in ['deleted', 'replaced', 'revoked']:
        return
    if 'derived_from' not in value:
        return
    for f in value['derived_from']:
        if 'assembly' in f:
            if f['assembly'] != value['assembly']:
                detail = 'Processed file {} '.format(value['@id']) + \
                         'assembly {} '.format(value['assembly']) + \
                         'does not match assembly {} of the file {} '.format(
                         f['assembly'],
                         f['@id']) + \
                    'it was derived from.'
                yield AuditFailure('inconsistent assembly',
                                   detail, level='INTERNAL_ACTION')
                return


@audit_checker('file', frame=['replicate', 'replicate.experiment',
                              'derived_from', 'derived_from.replicate',
                              'derived_from.replicate.experiment'])
def audit_file_biological_replicate_number_match(value, system):

    if value['status'] in ['deleted', 'replaced', 'revoked']:
        return

    if 'replicate' not in value:
        return

    if 'derived_from' not in value or len(value['derived_from']) == 0:
        return

    bio_rep_number = value['replicate']['biological_replicate_number']
    tech_rep_number = value['replicate']['technical_replicate_number']
    file_replicate = (bio_rep_number, tech_rep_number)
    file_exp_accession = value['replicate']['experiment']['accession']
    derived_from_files = value['derived_from']

    for derived_from_file in derived_from_files:
        if 'replicate' in derived_from_file:

            # excluding control files from different experiments
            if derived_from_file['replicate']['experiment']['accession'] != file_exp_accession:
                continue

            derived_bio_rep_num = derived_from_file['replicate']['biological_replicate_number']
            derived_tech_rep_num = derived_from_file['replicate']['technical_replicate_number']
            derived_replicate = (derived_bio_rep_num, derived_tech_rep_num)
            if file_replicate != derived_replicate:
                detail = 'File {} '.format(value['@id']) + \
                         'is associated with replicate [{},{}] '.format(file_replicate[0],
                                                                        file_replicate[1]) + \
                         ', but it was derived from file {} '.format(derived_from_file['@id']) + \
                         'which is associated with a replicate [{},{}].'.format(
                             derived_replicate[0],
                             derived_replicate[1])
                yield AuditFailure('inconsistent replicate',
                                   detail, level='ERROR')
                return


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
        detail = 'File {} from experiment {} '.format(value['@id'], value['dataset']['@id']) + \
                 'is associated with replicate [{},{}] '.format(
                     value['replicate']['biological_replicate_number'],
                     value['replicate']['technical_replicate_number']) + \
                 '{}, but that replicate is associated with a different '.format(
                     value['replicate']['@id']) + \
                 'experiment {}.'.format(value['replicate']['experiment']['@id'])
        yield AuditFailure('inconsistent replicate', detail, level='ERROR')
        return


@audit_checker('file', frame=['award'],
               condition=rfa("ENCODE3", "modERN", "GGR"))
def audit_file_platform(value, system):
    '''
    A raw data file should have a platform specified.
    Should be in the schema.
    '''

    if value['status'] in ['deleted', 'replaced', 'revoked']:
        return

    if value['file_format'] not in raw_data_formats:
        return

    if 'award' in value and 'rfa' in value['award'] and \
       'platform' not in value:
        detail = 'File {} metadata lacks information on the instrument/platform '.format(value['@id']) + \
                 'used to produce it.'
        raise AuditFailure('missing platform', detail, level='ERROR')


def check_presence(file_to_check, files_list):
    for f in files_list:
        if f['accession'] == file_to_check['accession']:
            return True
    return False


@audit_checker('file',
               frame=['dataset',
                      'dataset.target',
                      'platform',
                      'controlled_by',
                      'controlled_by.replicate',
                      'controlled_by.dataset',
                      'controlled_by.paired_with',
                      'controlled_by.platform'],
               condition=rfa('Roadmap',
                             'ENCODE2',
                             'ENCODE2-Mouse',
                             'ENCODE',
                             'ENCODE3',
                             'modERN'))
def audit_file_controlled_by(value, system):
    '''
    A fastq in a ChIP-seq experiment should have a controlled_by
    '''

    if value['status'] in ['deleted', 'replaced', 'revoked', 'archived']:
        return

    if value['dataset'].get('assay_term_name') not in ['ChIP-seq',
                                                       'RAMPAGE',
                                                       'CAGE',
                                                       'shRNA knockdown followed by RNA-seq',
                                                       'siRNA knockdown followed by RNA-seq',
                                                       'CRISPR genome editing followed by RNA-seq']:

        return

    if value['file_format'] not in ['fastq']:
        return

    if 'target' in value['dataset'] and \
       'control' in value['dataset']['target'].get('investigated_as', []):
        return

    if 'controlled_by' not in value:
        value['controlled_by'] = []

    if value['controlled_by'] == []:
        detail = 'controlled_by is a list of files that are used as controls for a given experimental file. ' + \
                 'Fastq files generated in a {} assay require the '.format(
                     value['dataset']['assay_term_name']) + \
                 'specification of control fastq file(s) in the controlled_by list. ' + \
                 'Fastq file {} '.format(
                     value['@id']) + \
                 'is missing the requisite file specification in controlled_by list.'
        yield AuditFailure('missing controlled_by', detail, level='NOT_COMPLIANT')
        return

    if value['dataset'].get('assay_term_name') in ['ChIP-seq',
                                                   'RAMPAGE']:
        bio_rep_numbers = set()
        pe_files = []
        if len(value['controlled_by']) > 0:
            for control_file in value['controlled_by']:
                if 'replicate' in control_file:
                    bio_rep_numbers.add(control_file['replicate']['biological_replicate_number'])
                if 'run_type' in control_file:
                    if control_file['run_type'] == 'paired-ended':
                        pe_files.append(control_file)
        for pe_file in pe_files:
            if 'paired_with' not in pe_file:
                detail = 'Fastq file {} '.format(value['@id']) + \
                         'from experiment {} '.format(value['dataset']['@id']) + \
                         'contains in controlled_by list PE fastq file ' + \
                         '{} with missing paired_with property.'.format(pe_file['@id'])
                yield AuditFailure('missing paired_with in controlled_by',
                                   detail, level='INTERNAL_ACTION')
            elif check_presence(pe_file['paired_with'], pe_files) is False:
                detail = 'Fastq file {} '.format(value['@id']) + \
                         'from experiment {} '.format(value['dataset']['@id']) + \
                         'contains in controlled_by list PE fastq file ' + \
                         '{} which is paired to a file {} '.format(pe_file['@id'],
                                                                   pe_file['paired_with']['@id']) + \
                         'that is not included in the controlled_by list'
                yield AuditFailure('missing paired_with in controlled_by', detail,
                                   level='INTERNAL_ACTION')

        if len(bio_rep_numbers) > 1:
            detail = 'Fastq file {} '.format(value['@id']) + \
                     'from experiment {} '.format(value['dataset']['@id']) + \
                     'contains in controlled_by list fastq files ' + \
                     'from diferent biological replicates {}.'.format(list(bio_rep_numbers))
            yield AuditFailure('inconsistent controlled_by replicates', detail, level='ERROR')

    possible_controls = value['dataset'].get('possible_controls')
    biosample = value['dataset'].get('biosample_term_id')
    biosample_term_name = value['dataset'].get('biosample_term_name')
    run_type = value.get('run_type', None)
    read_length = value.get('read_length', None)

    if value['controlled_by']:
        for ff in value['controlled_by']:
            control_bs = ff['dataset'].get('biosample_term_id')
            control_run = ff.get('run_type', None)
            control_length = ff.get('read_length', None)

            if control_bs != biosample:
                detail = 'controlled_by is a list of files that are used as controls for a given file. ' + \
                         'This experiment was performed using {}, but '.format(biosample_term_name) + \
                         'file {} contains in controlled_by list a file '.format(value['@id']) + \
                         '{} that belongs to experiment with different biosample {}.'.format(
                             ff['@id'],
                             ff['dataset'].get('biosample_term_name'))
                yield AuditFailure('inconsistent control', detail, level='ERROR')
                return

            if ff['file_format'] != value['file_format']:
                detail = 'controlled_by is a list of files that are used as controls for a given file. ' + \
                         'File {} with file_format {} contains in controlled_by list '.format(
                             value['@id'],
                             value['file_format'],) + \
                         'a file {} with different file_format {}.'.format(
                             ff['@id'],
                             ff['file_format'])
                yield AuditFailure('inconsistent control', detail, level='ERROR')
                return

            if (possible_controls is None) or (ff['dataset']['@id'] not in possible_controls):
                detail = 'possible_controls is a list of experiment(s) that can serve as ' + \
                         'analytical controls for a given experiment. ' + \
                         'controlled_by is a list of files that are used as ' + \
                         'controls for a given file. ' + \
                         'File {} contains in controlled_by list a file {} '.format(
                             value['@id'],
                             ff['@id']) + \
                         'that belongs to an experiment {} that '.format(ff['dataset']['@id']) + \
                         'is not specified in possible_controls list of this experiment.'

                yield AuditFailure('inconsistent control', detail, level='ERROR')
                return

            if (run_type is None) or (control_run is None):
                continue

            if (read_length is None) or (control_length is None):
                continue

            if run_type != control_run and \
               value['dataset'].get('assay_term_name') not in ['RAMPAGE', 'CAGE']:
                detail = 'File {} is {} but its control file {} is {}'.format(
                    value['@id'],
                    run_type,
                    ff['@id'],
                    control_run
                    )
                yield AuditFailure('inconsistent control run_type',
                                   detail, level='WARNING')

            if read_length != control_length and \
               abs(read_length - control_length) > 2 and \
               value['dataset'].get('assay_term_name') not in \
                    ['shRNA knockdown followed by RNA-seq',
                     'siRNA knockdown followed by RNA-seq',
                     'CRISPR genome editing followed by RNA-seq']:

                detail = 'File {} is {} but its control file {} is {}'.format(
                    value['@id'],
                    value['read_length'],
                    ff['@id'],
                    ff['read_length']
                    )
                yield AuditFailure('inconsistent control read length',
                                   detail, level='WARNING')
                return


@audit_checker('file', frame='object')
def audit_file_flowcells(value, system):
    '''
    A fastq file could have its flowcell details.
    '''

    if value['status'] in ['deleted', 'replaced', 'revoked']:
        return

    if value['file_format'] not in ['fastq']:
        return

    if 'flowcell_details' not in value or (value['flowcell_details'] == []):
        detail = 'Fastq file {} is missing flowcell_details'.format(value['@id'])
        raise AuditFailure('missing flowcell_details', detail, level='WARNING')


@audit_checker('file', frame=['paired_with'])
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

    if value['paired_end'] in ['1,2']:
        return

    if 'paired_with' not in value:
        return

    if 'replicate' not in value['paired_with']:
        return

    if 'replicate' not in value:
        detail = 'File {} has paired_end = {}. It requires a replicate'.format(
            value['@id'],
            value['paired_end'])
        yield AuditFailure('missing replicate', detail, level='INTERNAL_ACTION')
        return

    if value['replicate'] != value['paired_with']['replicate']:
        detail = 'File {} has replicate {}. It is paired_with file {} with replicate {}'.format(
            value['@id'],
            value.get('replicate'),
            value['paired_with']['@id'],
            value['paired_with'].get('replicate'))
        yield AuditFailure('inconsistent paired_with', detail, level='ERROR')
        return

    if value['paired_end'] == '1':
        context = system['context']
        paired_with = context.get_rev_links('paired_with')
        if len(paired_with) > 1:
            detail = 'Paired end 1 file {} paired_with by multiple paired end 2 files: {!r}'.format(
                value['@id'],
                paired_with,
            )
            yield AuditFailure('multiple paired_with', detail, level='ERROR')
            return

'''
@audit_checker('file', frame=['step_run',
                              'dataset'], condition=rfa('modERN'))
def audit_modERN_ChIP_pipeline_steps(value, system):

    expt = value['dataset']
    if 'Experiment' not in expt['@type']:
        return

    if expt['assay_term_name'] != 'ChIP-seq':
        return

    if value['status'] in ['archived', 'revoked', 'deleted', 'replaced']:
        return

    if value['file_format'] == 'fastq':
        if 'step_run' in value:
            detail = 'Fastq file {} should not have an associated step_run'.format(value['@id'])
            yield AuditFailure('unexpected step_run', detail, level='ERROR')
        return

    if 'step_run' not in value:
        detail = 'File {} is missing a step_run'.format(value['@id'])
        yield AuditFailure('missing step_run', detail, level='WARNING')
        return

    if (value['file_format'] != 'fastq') and ('derived_from' not in value):
        detail = 'File {} is missing its derived_from'.format(value['@id'])
        return

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
'''

@audit_checker('file', frame=['file_format_specifications'],)
def audit_file_format_specifications(value, system):

    for doc in value.get('file_format_specifications', []):
        if doc['document_type'] != "file format specification":
            detail = 'File {} has document {} not of type file format specification'.format(
                value['@id'],
                doc['@id']
                )
            raise AuditFailure('inconsistent document_type', detail, level='ERROR')


def get_chip_seq_bam_read_depth(bam_file):
    if bam_file['status'] in ['deleted', 'replaced', 'revoked']:
        return False

    if bam_file['file_format'] != 'bam' or bam_file['output_type'] != 'alignments':
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
                    read_depth = int(metric['total']/2)
                else:
                    read_depth = metric['total']
                break

    if read_depth == 0:
        return False

    return read_depth


def get_control_bam(experiment_bam, pipeline_name):
    #  get representative FASTQ file
    if 'derived_from' not in experiment_bam or len(experiment_bam['derived_from']) < 1:
        return False

    derived_from_fastqs = experiment_bam['derived_from']
    control_fastq = False
    for entry in derived_from_fastqs:
        if 'controlled_by' in entry and len(entry['controlled_by']) > 0:
            control_fastq = entry['controlled_by'][0]  # getting representative FASTQ
            break

    # get representative FASTQ from control
    if control_fastq is False:
        return False
    else:
        if 'original_files' not in control_fastq['dataset']:
            return False

        control_bam = False
        control_files = control_fastq['dataset']['original_files']
        for control_file in control_files:
            if control_file['status'] in ['deleted', 'replaced', 'revoked']:
                continue
            if control_file['file_format'] == 'bam' and \
               control_file['output_type'] == 'alignments' and \
               'assembly' in control_file and 'assembly' in experiment_bam and \
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
                    derived_list = control_file['derived_from']
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


def get_target_name(bam_file):
    if 'dataset' in bam_file and 'target' in bam_file['dataset'] and \
       'name' in bam_file['dataset']['target']:
            return bam_file['dataset']['target']['name']
    return False


def extract_award_version(bam_file):
    if 'dataset' in bam_file and 'award' in bam_file['dataset'] and \
       'rfa' in bam_file['dataset']['award']:
        if bam_file['dataset']['award']['rfa'] in ['ENCODE2-Mouse', 'ENCODE2']:
            return 'ENC2'
    return 'ENC3'


@audit_checker('file', frame=[
    'award',
    'quality_metrics',
    'analysis_step_version',
    'analysis_step_version.analysis_step',
    'analysis_step_version.analysis_step.pipelines',
    'analysis_step_version.software_versions',
    'analysis_step_version.software_versions.software',
    'dataset',
    'dataset.target',
    'derived_from',
    'derived_from.controlled_by',
    'derived_from.controlled_by.dataset',
    'derived_from.controlled_by.dataset.target',
    'derived_from.controlled_by.dataset.original_files',
    'derived_from.controlled_by.dataset.original_files.quality_metrics',
    'derived_from.controlled_by.dataset.original_files.dataset',
    'derived_from.controlled_by.dataset.original_files.dataset.target',
    'derived_from.controlled_by.dataset.original_files.derived_from',
    'derived_from.controlled_by.dataset.original_files.analysis_step_version',
    'derived_from.controlled_by.dataset.original_files.analysis_step_version.analysis_step',
    'derived_from.controlled_by.dataset.original_files.analysis_step_version.analysis_step.pipelines',
    'derived_from.controlled_by.dataset.original_files.analysis_step_version.software_versions',
    'derived_from.controlled_by.dataset.original_files.analysis_step_version.software_versions.software'])
def audit_file_chip_seq_control_read_depth(value, system,
                                           condition=rfa('ENCODE3',
                                                         'ENCODE2-Mouse',
                                                         'ENCODE2',
                                                         'ENCODE',
                                                         'Roadmap')):
    '''
    An alignment file from the ENCODE Processing Pipeline should have read depth
    in accordance with the criteria
    '''

    if value['status'] in ['deleted', 'replaced', 'revoked']:
        return

    if value['file_format'] != 'bam':
        return

    if value['output_type'] in ['transcriptome alignments', 'unfiltered alignments']:
        return

    if value['lab'] not in ['/labs/encode-processing-pipeline/']:
        return

    if 'analysis_step_version' not in value:
        detail = 'ENCODE Processed alignment file {} has '.format(value['@id']) + \
            'no analysis step version'
        yield AuditFailure('missing analysis step version', detail, level='INTERNAL_ACTION')
        return

    if 'analysis_step' not in value['analysis_step_version']:
        detail = 'ENCODE Processed alignment file {} has '.format(value['@id']) + \
            'no analysis step in {}'.format(value['analysis_step_version']['@id'])
        yield AuditFailure('missing analysis step', detail, level='INTERNAL_ACTION')
        return

    if 'pipelines' not in value['analysis_step_version']['analysis_step']:
        detail = 'ENCODE Processed alignment file {} has '.format(value['@id']) + \
            'no pipelines in {}'.format(value['analysis_step_version']['analysis_step']['@id'])
        yield AuditFailure('missing pipelines in analysis step', detail, level='INTERNAL_ACTION')
        return

    if 'software_versions' not in value['analysis_step_version']:
        detail = 'ENCODE Processed alignment file {} has '.format(value['@id']) + \
            'no software_versions in {}'.format(value['analysis_step_version']['@id'])
        yield AuditFailure('missing software versions', detail, level='INTERNAL_ACTION')
        return

    if value['analysis_step_version']['software_versions'] == []:
        detail = 'ENCODE Processed alignment file {} has no '.format(value['@id']) + \
            'softwares listed in software_versions,' + \
            ' under {}'.format(value['analysis_step_version']['@id'])
        yield AuditFailure('missing software', detail, level='INTERNAL_ACTION')
        return

    chip_flag = False
    for p in value['analysis_step_version']['analysis_step']['pipelines']:
        if p['title'] == 'ChIP-seq read mapping':
            chip_flag = True
        if p['title'] == 'Raw mapping with no filtration':
            return

    if chip_flag is False:
        return

    quality_metrics = value.get('quality_metrics')

    if (quality_metrics is None) or (quality_metrics == []):
        return

    derived_from_files = value.get('derived_from')
    if (derived_from_files is None) or (derived_from_files == []):
        return

    target_name = 'empty'
    target_investigated_as = 'empty'

    if 'dataset' in value:
        if 'target' in value['dataset'] and 'name' in value['dataset']['target']:
            target_name = value['dataset']['target']['name']
            target_investigated_as = value['dataset']['target']['investigated_as']

    if target_name not in ['Control-human', 'Control-mouse']:
        control_bam = get_control_bam(value, 'ChIP-seq read mapping')
        if control_bam is not False:
            control_depth = get_chip_seq_bam_read_depth(control_bam)
            control_target = get_target_name(control_bam)
            standards_version = extract_award_version(control_bam)
            if control_depth is not False and control_target is not False:
                for failure in check_control_read_depth_standards(control_bam,
                                                                  control_depth,
                                                                  control_target,
                                                                  True,
                                                                  target_name,
                                                                  target_investigated_as,
                                                                  standards_version):
                    yield failure


def check_control_read_depth_standards(value,
                                       read_depth,
                                       target_name,
                                       is_control_file,
                                       control_to_target,
                                       target_investigated_as,
                                       standards_version):

    marks = pipelines_with_read_depth['ChIP-seq read mapping']

    if is_control_file is True:  # treat this file as control_bam -
        # raising insufficient control read depth
        if target_name not in ['Control-human', 'Control-mouse']:
            detail = 'Control alignment file {} '.format(value['@id']) + \
                     'has a target {} that is neither '.format(target_name) + \
                     'Control-human nor Control-mouse.'
            yield AuditFailure('inconsistent target of control experiment', detail, level='WARNING')
            return

        if control_to_target == 'empty':
            return

        elif 'broad histone mark' in target_investigated_as: #  control_to_target in broad_peaks_targets:
            if 'assembly' in value:
                detail = 'Control alignment file {} mapped to {} assembly has {} '.format(
                    value['@id'],
                    value['assembly'],
                    read_depth) + \
                    'usable fragments. ' + \
                    'The minimum ENCODE standard for a control of ChIP-seq assays targeting broad ' + \
                    'histone mark {} '.format(control_to_target) + \
                    'is 40 million usable fragments, the recommended number of usable ' + \
                    'fragments is > 45 million. (See /data-standards/chip-seq/ )'
            else:
                detail = 'Control alignment file {} has {} '.format(
                    value['@id'],
                    read_depth) + \
                    'usable fragments. ' + \
                    'The minimum ENCODE standard for a control of ChIP-seq assays targeting broad ' + \
                    'histone mark {} '.format(control_to_target) + \
                    'is 40 million usable fragments, the recommended number of usable ' + \
                    'fragments is > 45 million. (See /data-standards/chip-seq/ )'
            if read_depth >= 40000000 and read_depth < marks['broad']:
                yield AuditFailure('control low read depth', detail, level='WARNING')
            elif read_depth >= 5000000 and read_depth < 40000000:
                yield AuditFailure('control insufficient read depth', detail, level='NOT_COMPLIANT')
            elif read_depth < 5000000:
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
            if read_depth >= 10000000 and read_depth < marks['narrow']:
                yield AuditFailure('control low read depth', detail, level='WARNING')
            elif read_depth >= 5000000 and read_depth < 10000000:
                yield AuditFailure('control low read depth', detail, level='NOT_COMPLIANT')
            elif read_depth < 5000000:
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
            if read_depth >= 10000000 and read_depth < marks['narrow']:
                yield AuditFailure('control low read depth', detail, level='WARNING')
            elif read_depth >= 3000000 and read_depth < 10000000:
                yield AuditFailure('control low read depth', detail, level='NOT_COMPLIANT')
            elif read_depth < 3000000:
                yield AuditFailure('control extremely low read depth', detail, level='ERROR')
        return
