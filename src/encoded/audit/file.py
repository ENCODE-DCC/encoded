from snovault import (
    AuditFailure,
    audit_checker,
)
from .formatter import (
    audit_link,
    path_to_text,
)

from .item import STATUS_LEVEL

def check_award_condition(value, awards):
    return value.get('award', None) and value.get('award', {}).get('rfa') in awards

def audit_file_processed_step_run(value, system):
    if value['status'] in ['replaced',
                           'deleted',
                           'revoked',
                           'uploading',
                           'content error',
                           'upload failed']:
        return
    if value['output_category'] in ['raw data',
                                    'reference']:
        return
    if check_award_condition(value.get('dataset'), ['ENCODE3', 'ENCODE4']):
        if 'step_run' not in value:
            detail = ('Missing analysis_step_run information in file {}.'.format(
                audit_link(path_to_text(value['@id']), value['@id'])
                )
            )
            if value.get('lab', '') == '/labs/encode-processing-pipeline/':
                yield AuditFailure('missing analysis_step_run',
                                   detail, level='ERROR')
            else:
                yield AuditFailure('missing analysis_step_run',
                                   detail, level='WARNING')


def audit_file_raw_step_run(value, system):
    if value['status'] in ['replaced',
                           'deleted',
                           'revoked',
                           'uploading',
                           'content error',
                           'upload failed']:
        return
    if value['output_category'] not in ['raw data']:
        return
    if 'derived_from' not in value or \
            'derived_from' in value and len(value['derived_from']) == 0:
        return
    else:
        if 'step_run' not in value:
            detail = f'Missing analysis_step_run information in file {audit_link(path_to_text(value["@id"]), value["@id"])}.'
            yield AuditFailure('missing analysis_step_run', detail, level='WARNING')


def audit_file_processed_derived_from(value, system):
    if value['output_category'] in ['raw data',
                                    'reference']:
        return
    if 'derived_from' not in value or \
       'derived_from' in value and len(value['derived_from']) == 0:
        detail = ('derived_from is a list of files that were used to create a given file; '
            'for example, fastq file(s) will appear in the derived_from list of an '
            'alignments file. Processed file {} is missing the requisite file'
            ' specification in its derived_from list.'.format(
                audit_link(path_to_text(value['@id']), value['@id'])
            )
        )
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
                detail = ('derived_from is a list of files that were used '
                    'to create a given file; '
                    'for example, fastq file(s) will appear in the '
                    'derived_from list of an '
                    'alignments file. '
                    'Alignments file {} '
                    'from experiment {} '
                    'specifies a file {} '
                    'from a different experiment {} '
                    'in its derived_from list.'.format(
                        audit_link(path_to_text(value['@id']), value['@id']),
                        audit_link(path_to_text(value['dataset']['@id']), value['dataset']['@id']),
                        audit_link(path_to_text(f['@id']), f['@id']),
                        audit_link(path_to_text(f['dataset']), f['dataset'])
                    )
                )
                yield AuditFailure('inconsistent derived_from',
                                   detail, level='INTERNAL_ACTION')
    if fastq_bam_counter == 0:
        detail = ('derived_from is a list of files that were used to create a given file; '
            'for example, fastq file(s) will appear in the derived_from list of an '
            'alignments file. Alignments file {} is missing the requisite '
            'file specification in its derived_from list.'.format(
                audit_link(path_to_text(value['@id']), value['@id']),
            )
        )
        yield AuditFailure('missing derived_from',
                           detail, level='INTERNAL_ACTION')


def audit_file_assembly(value, system):
    if 'derived_from' not in value:
        return
    for f in value['derived_from']:
        if f.get('assembly') and value.get('assembly') and \
           f.get('assembly') != value.get('assembly'):
            detail = ('Processed file {} assembly {} '
                'does not match assembly {} of the file {} '
                'it was derived from.'.format(
                    audit_link(path_to_text(value['@id']), value['@id']),
                    value['assembly'],
                    f['assembly'],
                    audit_link(path_to_text(f['@id']), f['@id'])
                )
            )
            yield AuditFailure('inconsistent assembly',
                               detail, level='WARNING')
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
        detail = ('File {} from experiment {} '
            'is associated with replicate [{},{}] '
            '{}, but that replicate is associated with a different '
            'experiment {}.'.format(
                audit_link(path_to_text(value['@id']), value['@id']),
                audit_link(path_to_text(value['dataset']['@id']), value['dataset']['@id']),
                value['replicate']['biological_replicate_number'],
                value['replicate']['technical_replicate_number'],
                audit_link(path_to_text(value['replicate']['@id']), value['replicate']['@id']),
                audit_link(path_to_text(value['replicate']['experiment']), value['replicate']['experiment'])
            )
        )
        yield AuditFailure('inconsistent replicate', detail, level='ERROR')
        return


def audit_paired_with(value, system):
    '''
    A file with a paired_end needs a paired_with.
    Should be handled in the schema.
    A fastq file should be paired_with a fastq file.
    A paired_with should be the same replicate
    '''

    if 'paired_end' not in value:
        return

    if value['paired_end'] in ['1,2']:
        return

    if 'paired_with' not in value:
        detail = ('The file {} that is a read1 in a paired ended sequencing run is not paired_with a paired end 2 file'.format(
            audit_link(path_to_text(value['@id']), value['@id']),
            )
        )
        yield AuditFailure('missing paired_with', detail, level='WARNING')
        return

    paired_with_file_format = value['paired_with'].get('file_format')

    if value.get('file_format') == 'fastq' and paired_with_file_format != 'fastq':
        detail = ('Both the files in a paired-end run must be fastq files. '
            'Fastq file {} is paired with file {}, which is a {} file.'.format(
            audit_link(path_to_text(value['@id']), value['@id']),
            audit_link(path_to_text(value['paired_with']['@id']), value['paired_with']['@id']),
            paired_with_file_format
            )
        )
        yield AuditFailure('paired with non-fastq', detail, level='ERROR')

    if 'replicate' not in value['paired_with']:
        return

    if 'replicate' not in value:
        detail = ('File {} has paired_end = {}. It requires a replicate'.format(
            audit_link(path_to_text(value['@id']), value['@id']),
            value['paired_end']
            )
        )
        yield AuditFailure('missing replicate', detail, level='INTERNAL_ACTION')
    elif value['replicate'].get('@id') != value['paired_with']['replicate']:
        detail = ('File {} has replicate {}. It is paired_with file {} with replicate {}'.format(
            audit_link(path_to_text(value['@id']), value['@id']),
            audit_link(path_to_text(value['replicate'].get('@id')), value['replicate'].get('@id')),
            audit_link(path_to_text(value['paired_with']['@id']), value['paired_with']['@id']),
            audit_link(path_to_text(value['paired_with'].get('replicate')), value['paired_with'].get('replicate'))
            )
        )
        yield AuditFailure('inconsistent paired_with', detail, level='ERROR')

    paired_with_id = value['paired_with'].get('@id')

    if value['paired_end'] == value['paired_with'].get('paired_end'):
        detail = ('The read{} file {} is paired with read{} file {}.'.format(
            value['paired_end'],
            audit_link(path_to_text(value['@id']), value['@id']),
            value['paired_with'].get('paired_end'),
            audit_link(path_to_text(paired_with_id), paired_with_id),
            )
        )
        yield AuditFailure('inconsistent paired_with', detail, level='WARNING')

    if value['paired_end'] == '1':
        context = system['context']
        paired_with = context.get_rev_links('paired_with')
        if len(paired_with) > 1:
            detail = ('Paired end 1 file {} paired_with by multiple paired end 2 files: {!r}'.format(
                audit_link(path_to_text(value['@id']), value['@id']),
                paired_with
                )
            )
            yield AuditFailure('multiple paired_with', detail, level='ERROR')
            return

    file_read_count = value.get('read_count')
    paired_with_read_count = value['paired_with'].get('read_count')

    if (file_read_count and paired_with_read_count) and (file_read_count != paired_with_read_count):
        detail = ('File {} has {} reads. It is'
            ' paired_with file {} that has {} reads'.format(
                audit_link(path_to_text(value['@id']), value['@id']),
                file_read_count,
                audit_link(path_to_text(value['paired_with']['@id']), value['paired_with']['@id']),
                paired_with_read_count
            )
        )
        yield AuditFailure('inconsistent read count', detail, level='ERROR')

def audit_file_format_specifications(value, system):
    for doc in value.get('file_format_specifications', []):
        if doc['document_type'] != "file format specification":
            detail = ('File {} has document {} not of type file format specification'.format(
                audit_link(path_to_text(value['@id']), value['@id']),
                audit_link(path_to_text(doc['@id']), doc['@id'])
                )
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

    if value['dataset'].get('control_type'):
        return

    if not value.get('controlled_by'):
        detail = ('controlled_by is a list of files that are used as '
            'controls for a given experimental file. '
            'Fastq files generated in a {} assay require the '
            'specification of control fastq file(s) in the controlled_by list. '
            'Fastq file {} '
            'is missing the requisite file specification in controlled_by list.'.format(
                value['dataset']['assay_term_name'],
                audit_link(path_to_text(value['@id']), value['@id'])
            )
        )
        yield AuditFailure('missing controlled_by', detail, level='WARNING')
        return

    possible_controls = value['dataset'].get('possible_controls')
    biosample = value['dataset'].get('biosample_ontology', {}).get('term_id')
    biosample_term_name = value['dataset'].get('biosample_ontology', {}).get('term_name')
    run_type = value.get('run_type', None)
    read_length = value.get('read_length', None)

    if value['controlled_by']:
        for ff in value['controlled_by']:
            control_bs = ff['dataset'].get('biosample_ontology', {}).get('term_id')
            control_run = ff.get('run_type', None)
            control_length = ff.get('read_length', None)

            if control_bs != biosample:
                detail = ('controlled_by is a list of files that are used as controls for a given file. '
                    'This experiment was performed using {}, but '
                    'file {} contains in controlled_by list a file '
                    '{} that belongs to experiment with different biosample {}.'.format(
                        biosample_term_name,
                        audit_link(path_to_text(value['@id']), value['@id']),
                        audit_link(path_to_text(ff['@id']), ff['@id']),
                        ff['dataset'].get('biosample_ontology', {}).get('term_name')
                    )
                )
                yield AuditFailure('inconsistent control', detail, level='ERROR')
                return

            if ff['file_format'] != value['file_format']:
                detail = ('controlled_by is a list of files that are used as controls for a given file. ' 
                    'File {} with file_format {} contains in controlled_by list '
                    'a file {} with different file_format {}.'.format(
                        audit_link(path_to_text(value['@id']), value['@id']),
                        value['file_format'],
                        audit_link(path_to_text(ff['@id']), ff['@id']),
                        ff['file_format']
                    )
                )
                yield AuditFailure('inconsistent control', detail, level='ERROR')
                return

            if (possible_controls is None) or (ff['dataset']['@id'] not in possible_controls):
                detail = ('possible_controls is a list of experiment(s) that can serve as '
                    'analytical controls for a given experiment. '
                    'controlled_by is a list of files that are used as '
                    'controls for a given file. '
                    'File {} contains in controlled_by list a file {} '
                    'that belongs to an experiment {} that '
                    'is not specified in possible_controls list of this experiment.'.format(
                        audit_link(path_to_text(value['@id']), value['@id']),
                        audit_link(path_to_text(ff['@id']), ff['@id']),
                        audit_link(path_to_text(ff['dataset']['@id']), ff['dataset']['@id'])
                    )
                )
                yield AuditFailure('inconsistent control', detail, level='ERROR')
                return

            if (run_type is None) or (control_run is None):
                continue

            if (read_length is None) or (control_length is None):
                continue

            if run_type != control_run and \
               value['dataset'].get('assay_term_name') not in ['RAMPAGE', 'CAGE']:
                detail = ('File {} is {} but its control file {} is {}.'.format(
                    audit_link(path_to_text(value['@id']), value['@id']),
                    run_type,
                    audit_link(path_to_text(ff['@id']), ff['@id']),
                    control_run
                    )
                )
                yield AuditFailure('inconsistent control run_type',
                                   detail, level='WARNING')

            if read_length != control_length and \
               abs(read_length - control_length) > 2 and \
               value['dataset'].get('assay_term_name') not in \
                    ['shRNA knockdown followed by RNA-seq',
                     'siRNA knockdown followed by RNA-seq',
                     'CRISPR genome editing followed by RNA-seq']:

                detail = ('File {} is {} but its control file {} is {}.'.format(
                    audit_link(path_to_text(value['@id']), value['@id']),
                    value['read_length'],
                    audit_link(path_to_text(ff['@id']), ff['@id']),
                    ff['read_length']
                    )
                )
                yield AuditFailure('inconsistent control read length',
                                   detail, level='WARNING')
                return


def audit_duplicate_quality_metrics(value, system):
    quality_metrics = value.get('quality_metrics')
    if not quality_metrics:
        return
    metric_signatures = []
    audit_signatures = []
    for metric in quality_metrics:
        metric_type = metric.get('@type', [None])[0]
        signature = (
            metric_type,
            metric.get('processing_stage')
        )
        if signature not in metric_signatures:
            metric_signatures.append(signature)
        elif signature not in audit_signatures:
            # Add so only yields audit once per signature per file.
            audit_signatures.append(signature)
            detail = ('File {} has more than one {} quality metric.'.format(
                audit_link(path_to_text(value.get('@id')), value.get('@id')),
                metric_type
                )
            )
            yield AuditFailure(
                'duplicate quality metric',
                detail,
                level='INTERNAL_ACTION'
            )


def audit_file_in_correct_bucket(value, system):
    request = system.get('request')
    file_item = request.root.get_by_uuid(value['uuid'])
    result, current_path, destination_path = file_item._file_in_correct_bucket(request)
    if not result:
        detail = ('Move {} file {} from {} to {}'.format(
            value.get('status'),
            value.get('accession', value.get('uuid')),
            current_path,
            destination_path
            )
        )
        yield AuditFailure(
            'incorrect file bucket',
            detail,
            level='INTERNAL_ACTION'
        )



def audit_read_structure(value, system):
    read_structure = value.get('read_structure', [])
    for element in read_structure:
        if element['start'] == 0 or element['end'] == 0:
            detail = ('The read_stucture is 1-based. '
                'Neither start or end can be 0 for sequence element {}.'.format(
                    element['sequence_element']
                )
            )
            yield AuditFailure(
                'invalid read_structure',
                detail,
                level='ERROR'
            )
        if element['start'] > element['end']:
            detail = ('The start coordinate is bigger than the end coordinate '
                'for sequence element {}.'.format(
                    element['sequence_element']
                )
            )
            yield AuditFailure(
                'invalid read_structure',
                detail,
                level='ERROR'
            )


def audit_file_matching_md5sum(value, system):
    '''
    Files with md5 sums matching other files should be marked with a WARNING audit.
    If the other files are listed as matching but in fact have different md5 sums,
    the file should be flagged with an ERROR for incorrect metadata.
    '''

    matching_files = []
    checked_statuses = ['released', 'revoked', 'archived', 'in progress']
    if 'matching_md5sum' not in value or value.get('status') not in checked_statuses:
        return

    for file in value.get('matching_md5sum'):
        if file.get('uuid') == value.get('uuid'):
            detail = ('File {} is listing itself as having '
                'a matching md5 sum.'.format(
                    audit_link(path_to_text(value['@id']), value['@id'])
                )
            )
            yield AuditFailure('inconsistent matching_md5sum', detail, level='ERROR')
        if file.get('md5sum') != value.get('md5sum'):
            detail = ('File {} is listed as having a matching md5 sum '
                'as file {}, but the files have different md5 sums.'.format(
                    audit_link(path_to_text(file['@id']), file['@id']),
                    audit_link(path_to_text(value['@id']), value['@id'])
                )
            )
            yield AuditFailure('inconsistent matching_md5sum', detail, level='ERROR')
        elif file.get('status') in checked_statuses:
            matching_files.append(file['@id'])
            matching_files_links = [audit_link(path_to_text(file), file) for file in matching_files]

    if not matching_files:
        return
    elif len(matching_files) > 2:
        matching_files_joined = 'Files {}, and {}'.format(
            ', '.join(matching_files_links[:-1]),
            matching_files_links[-1]
        )
    else:
        matching_files_joined = ' and '.join(matching_files_links)

    detail = ('The md5 sum of file {} '
        'matches that of file(s) {}.'.format(
            audit_link(path_to_text(value['@id']), value['@id']),
            matching_files_joined
        )
    )
    yield AuditFailure('matching md5 sums', detail, level='WARNING')


def audit_file_index_of(value, system):
    '''
    Files with output_type: index reads may specify that they are index_of
    either 1 SE or 2 PE files. The SE/PE files must be fastq files, from the
    same experiment as index. Other combinations (including mispaired PE files)
    are flagged as an ERROR.
    https://encodedcc.atlassian.net/browse/ENCD-5252
    '''
    if value['output_type'] != 'index reads':
        return
    if 'index_of' in value:
        index_exp = value['dataset']['@id']
        indexed_files_with_expts = []
        indexed_fastq_with_pair = []
        count_indexed_files = 0
        incorrect_pairings = 0
        non_fastqs = 0
        run_type = set()
        non_illumina_platforms = [
                "ced61406-dcc6-43c4-bddd-4c977cc676e8",
                "c7564b38-ab4f-4c42-a401-3de48689a998",
                "e2be5728-5744-4da4-8881-cb9526d0389e",
                "6c275b37-018d-4bf8-85f6-6e3b830524a9",
                "8f1a9a8c-3392-4032-92a8-5d196c9d7810"
                ]
        for indexed_file in value['index_of']:
            count_indexed_files += 1
            if indexed_file['file_format'] != 'fastq':
                non_fastqs += 1
            if index_exp != indexed_file['dataset']:
                indexed_files_with_expts.append(tuple((indexed_file['@id'], indexed_file['dataset'])))
            if 'run_type' in indexed_file:
                run_type.add(indexed_file['run_type'])
                if indexed_file['run_type'] == 'paired-ended':
                    if 'paired_with' in indexed_file:
                        indexed_fastq_with_pair.append(tuple((indexed_file['@id'], indexed_file['paired_with'])))
                    else:
                        incorrect_pairings += 1
            elif 'platform' in indexed_file and indexed_file['platform']['uuid'] in non_illumina_platforms:
                run_type.add('none')
        if len(indexed_fastq_with_pair) == 2:
            if indexed_fastq_with_pair[0][0] != indexed_fastq_with_pair[1][1]:
                incorrect_pairings += 1

        if len(indexed_files_with_expts) > 0:
            fastq_links = ', '.join(audit_link(path_to_text(m[0]), m[0]) for m in indexed_files_with_expts)
            expts_links = ', '.join(audit_link(path_to_text(m[1]), m[1]) for m in indexed_files_with_expts)
            detail = (
                f'Index file {audit_link(path_to_text(value["@id"]), value["@id"])} '
                f'is from experiment {audit_link(path_to_text(value["dataset"]["@id"]), value["dataset"]["@id"])} '
                f'but it is used as an index for '
                f'file(s) {fastq_links} from experiment(s) {expts_links}.'
            )
            yield AuditFailure('inconsistent index file', detail, level='ERROR')

        if non_fastqs > 0:
            detail = (
                f'Index file {audit_link(path_to_text(value["@id"]), value["@id"])} '
                f'is incorrectly specified for non-fastq file(s).'
            )
            yield AuditFailure('inconsistent index file', detail, level='ERROR')

        if 'single-ended' in run_type and 'paired-ended' in run_type:
            detail = (
                f'Index file {audit_link(path_to_text(value["@id"]), value["@id"])} '
                f'is incorrectly specified for both single- and paired-end fastq files.'
            )
            yield AuditFailure('inconsistent index file', detail, level='ERROR')

        if count_indexed_files == 1 and 'paired-ended' in run_type:
            detail = (
                f'Index file {audit_link(path_to_text(value["@id"]), value["@id"])} '
                f'specifies that it is index_of only one paired-end fastq file.'
            )
            yield AuditFailure('inconsistent index file', detail, level='ERROR')

        if incorrect_pairings > 0 and run_type == {'paired-ended'}:
            detail = (
                f'Index file {audit_link(path_to_text(value["@id"]), value["@id"])} '
                f'specifies that it is index_of 2 paired-end fastq that are not paired with each other.'
                )
            yield AuditFailure('inconsistent index file', detail, level='ERROR')

        if 'none' in run_type and len(run_type) > 1:
            detail = (
                f'Index file {audit_link(path_to_text(value["@id"]), value["@id"])} '
                f'is incorrectly specified for fastq files sequenced using different platforms.'
            )
            yield AuditFailure('inconsistent index file', detail, level='ERROR')

        if run_type == {'none'} and (count_indexed_files - non_fastqs) > 1:
            detail = (
                f'Index file {audit_link(path_to_text(value["@id"]), value["@id"])} '
                f'is incorrectly specified for multiple non-Illumina fastq files.'
            )
            yield AuditFailure('inconsistent index file', detail, level='ERROR')


def audit_index_reads_read_structure(value, system):
    if value['output_type'] == 'index reads':
        if 'read_structure' not in value or \
            'read_structure' in value and len(value['read_structure']) == 0:
            detail = (
                f'Index file {audit_link(path_to_text(value["@id"]), value["@id"])} '
                f'is missing read structure information.'
            )
            yield AuditFailure('missing read structure', detail, level='INTERNAL_ACTION')

function_dispatcher = {
    'audit_step_run': audit_file_processed_step_run,
    'audit_derived_from': audit_file_processed_derived_from,
    'audit_file_raw_step_run': audit_file_raw_step_run,
    'audit_assembly': audit_file_assembly,
    'audit_replicate_match': audit_file_replicate_match,
    'audit_paired_with': audit_paired_with,
    'audit_specifications': audit_file_format_specifications,
    'audit_controlled_by': audit_file_controlled_by,
    'audit_duplicate_quality_metrics': audit_duplicate_quality_metrics,
    'audit_file_in_correct_bucket': audit_file_in_correct_bucket,
    'audit_read_structure': audit_read_structure,
    'audit_file_matching_md5sum': audit_file_matching_md5sum,
    'audit_file_index_of': audit_file_index_of,
    'audit_index_reads_read_structure': audit_index_reads_read_structure,
}


@audit_checker('File',
               frame=['derived_from',
                      'replicate',
                      'paired_with',
                      'file_format_specifications',
                      'dataset',
                      'dataset.biosample_ontology',
                      'dataset.target',
                      'dataset.award',
                      'platform',
                      'controlled_by',
                      'controlled_by.replicate',
                      'controlled_by.dataset',
                      'controlled_by.dataset.biosample_ontology',
                      'controlled_by.paired_with',
                      'controlled_by.platform',
                      'quality_metrics',
                      'matching_md5sum',
                      'index_of',
                      'index_of.platform',
                      ]
               )
def audit_file(value, system):
    for function_name in function_dispatcher.keys():
        for failure in function_dispatcher[function_name](value, system):
            yield failure

# def audit_file_chip_seq_control_read_depth(value, system):
# migrated to experiment https://encodedcc.atlassian.net/browse/ENCD-3493

# def audit_file_flowcells(value, system): # removed in version 56
# http://redmine.encodedcc.org/issues/5060

# def audit_modERN_ChIP_pipeline_steps(value, system):
# removed https://encodedcc.atlassian.net/browse/ENCD-3493

# def audit_file_pipeline_status(value, system): removed at release 56
# http://redmine.encodedcc.org/issues/5017

# def audit_file_md5sum_integrity(value, system): # removed release 55

# def audit_file_derived_from_revoked(value, system): removed at release 56
# http://redmine.encodedcc.org/issues/5018

# def audit_file_biological_replicate_number_match
# https://encodedcc.atlassian.net/browse/ENCD-3493

# def audit_file_platform(value, system): removed from release v56
