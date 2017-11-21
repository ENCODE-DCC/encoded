from snovault import (
    AuditFailure,
    audit_checker,
)

from .item import STATUS_LEVEL


def audit_file_processed_derived_from(value, system):
    if value['output_category'] in ['raw data',
                                    'reference']:
        return
    if 'derived_from' not in value or \
       'derived_from' in value and len(value['derived_from']) == 0:
        detail = 'derived_from is a list of files that were used to create a given file; ' + \
                 'for example, fastq file(s) will appear in the derived_from list of an ' + \
                 'alignments file. ' + \
                 'Processed file {} '.format(value['@id']) + \
                 'is missing the requisite file specification in its derived_from list.'
        yield AuditFailure('missing derived_from',
                           detail, level='INTERNAL_ACTION')
        return

    if value['file_format'] != 'bam':
        return
    # Ignore replaced BAMs because missing derived_from logic should be applied to their
    # replacements instead (ENCD-3595).
    if value['status'] == 'replaced':
        return

    fastq_bam_counter = 0
    for f in value.get('derived_from'):
        if (f['file_format'] == 'bam'
            or f['file_format'] == 'fastq'
            or (f['file_format'] in ['fasta', 'csfasta', 'csqual']
                and f['output_type'] == 'reads'
                and f['output_category'] == 'raw data')):

            # Audit shouldn't trigger if status isn't registered in STATUS_LEVEL dict.
            if f['status'] not in STATUS_LEVEL or value['status'] not in STATUS_LEVEL:
                return

            if STATUS_LEVEL[f['status']] >= STATUS_LEVEL[value['status']]:
                fastq_bam_counter += 1

            if f['dataset'] != value['dataset'].get('@id'):
                detail = 'derived_from is a list of files that were used ' + \
                         'to create a given file; ' + \
                         'for example, fastq file(s) will appear in the ' + \
                         'derived_from list of an ' + \
                         'alignments file. ' + \
                         'Alignments file {} '.format(value['@id']) + \
                         'from experiment {} '.format(value['dataset']['@id']) + \
                         'specifies a file {} '.format(f['@id']) + \
                         'from a different experiment {} '.format(f['dataset']) + \
                         'in its derived_from list.'
                yield AuditFailure('inconsistent derived_from',
                                   detail, level='INTERNAL_ACTION')
    if fastq_bam_counter == 0:
        detail = 'derived_from is a list of files that were used to create a given file; ' + \
                 'for example, fastq file(s) will appear in the derived_from list of an ' + \
                 'alignments file. ' + \
                 'Alignments file {} '.format(value['@id']) + \
                 'is missing the requisite file specification in its derived_from list.'
        yield AuditFailure('missing derived_from',
                           detail, level='INTERNAL_ACTION')


def audit_file_assembly(value, system):
    if 'derived_from' not in value:
        return
    for f in value['derived_from']:
        if f.get('assembly') and value.get('assembly') and \
           f.get('assembly') != value.get('assembly'):
            detail = 'Processed file {} '.format(value['@id']) + \
                'assembly {} '.format(value['assembly']) + \
                'does not match assembly {} of the file {} '.format(
                f['assembly'],
                f['@id']) + \
                'it was derived from.'
            yield AuditFailure('inconsistent assembly',
                               detail, level='INTERNAL_ACTION')
            return


def audit_file_replicate_match(value, system):
    '''
    A file's replicate should belong to the same experiment that the file
    does.  These tend to get confused when replacing objects.
    '''

    if 'replicate' not in value:
        return

    rep_exp = value['replicate']['experiment']
    file_exp = value['dataset']['@id']

    if rep_exp != file_exp:
        detail = 'File {} from experiment {} '.format(value['@id'], value['dataset']['@id']) + \
                 'is associated with replicate [{},{}] '.format(
                     value['replicate']['biological_replicate_number'],
                     value['replicate']['technical_replicate_number']) + \
                 '{}, but that replicate is associated with a different '.format(
                     value['replicate']['@id']) + \
                 'experiment {}.'.format(value['replicate']['experiment'])
        yield AuditFailure('inconsistent replicate', detail, level='ERROR')
        return


def audit_paired_with(value, system):
    '''
    A file with a paired_end needs a paired_with.
    Should be handled in the schema.
    A paired_with should be the same replicate
    '''

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

    if value['replicate'].get('@id') != value['paired_with']['replicate']:
        detail = 'File {} has replicate {}. It is paired_with file {} with replicate {}'.format(
            value['@id'],
            value['replicate'].get('@id'),
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
                paired_with
            )
            yield AuditFailure('multiple paired_with', detail, level='ERROR')
            return


def audit_file_format_specifications(value, system):
    for doc in value.get('file_format_specifications', []):
        if doc['document_type'] != "file format specification":
            detail = 'File {} has document {} not of type file format specification'.format(
                value['@id'],
                doc['@id']
            )
            yield AuditFailure('inconsistent document_type', detail, level='ERROR')
            return


def audit_file_controlled_by(value, system):
    '''
    A fastq in a ChIP-seq experiment should have a controlled_by
    '''

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

    if not value.get('controlled_by'):
        detail = 'controlled_by is a list of files that are used as ' + \
                 'controls for a given experimental file. ' + \
                 'Fastq files generated in a {} assay require the '.format(
                     value['dataset']['assay_term_name']) + \
                 'specification of control fastq file(s) in the controlled_by list. ' + \
                 'Fastq file {} '.format(
                     value['@id']) + \
                 'is missing the requisite file specification in controlled_by list.'
        yield AuditFailure('missing controlled_by', detail, level='NOT_COMPLIANT')
        return

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


function_dispatcher = {
    'audit_derived_from': audit_file_processed_derived_from,
    'audit_assembly': audit_file_assembly,
    'audit_replicate_match': audit_file_replicate_match,
    'audit_paired_with': audit_paired_with,
    'audit_specifications': audit_file_format_specifications,
    'audit_controlled_by': audit_file_controlled_by
}


@audit_checker('File',
               frame=['derived_from',
                      'replicate',
                      'paired_with',
                      'file_format_specifications',
                      'dataset',
                      'dataset.target',
                      'platform',
                      'controlled_by',
                      'controlled_by.replicate',
                      'controlled_by.dataset',
                      'controlled_by.paired_with',
                      'controlled_by.platform'])
def audit_file(value, system):
    for function_name in function_dispatcher.keys():
        for failure in function_dispatcher[function_name](value, system):
            yield failure

# def audit_file_chip_seq_control_read_depth(value, system):
# migrated to experiment https://encodedcc.atlassian.net/browse/ENCD-3493

# def audit_file_flowcells(value, system): # removed in version 56
# http://redmine.encodedcc.org/issues/5060
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
