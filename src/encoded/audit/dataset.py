from snovault import (
    AuditFailure,
    audit_checker,
)
from .formatter import (
    audit_link,
    path_to_text,
)


def audit_experiment_geo_submission(value, system, excluded_types):
    if value['status'] not in ['released']:
        return
    submitted_flag = False
    if 'dbxrefs' in value and value['dbxrefs'] != []:
        for entry in value['dbxrefs']:
            if entry.startswith('GEO:'):
                submitted_flag = True
    if submitted_flag is False:
        detail = ('Experiment {} is released,'
            ' but is not submitted to GEO.'.format(
                audit_link(path_to_text(value['@id']), value['@id'])
            )
        )
        yield AuditFailure('experiment not submitted to GEO', detail, level='INTERNAL_ACTION')
    return


def audit_experiment_released_with_unreleased_files(value, system, excluded_types):
    if value['status'] != 'released':
        return
    if 'original_files' not in value:
        return
    for f in value['original_files']:
        if f['status'] not in ['released', 'deleted',
                               'revoked', 'replaced',
                               'archived']:
            detail = ('Released dataset {} contains file {} that has not been released.'.format(
                    audit_link(path_to_text(value['@id']), value['@id']),
                    audit_link(path_to_text(f['@id']), f['@id'])
                )
            )
            yield AuditFailure('mismatched file status', detail, level='INTERNAL_ACTION')
    return

#######################
# utilities
#######################

def create_files_mapping(files_list, excluded):
    to_return = {'original_files': {},
                 'fastq_files': {},
                 'alignments': {},
                 'unfiltered_alignments': {},
                 'alignments_unfiltered_alignments': {},
                 'transcriptome_alignments': {},
                 'peaks_files': {},
                 'gene_quantifications_files': {},
                 'transcript_quantifications_files': {},
                 'signal_files': {},
                 'preferred_default_idr_peaks': {},
                 'cpg_quantifications': {},
                 'contributing_files': {},
                 'raw_data': {},
                 'processed_data': {},
                 'excluded_types': excluded}
    if files_list:
        for file_object in files_list:
            if file_object['status'] not in excluded:
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
                    to_return['transcript_quantifications_files'][file_object['@id']
                                                            ] = file_object

                if file_output and file_output == 'signal of unique reads':
                    to_return['signal_files'][file_object['@id']] = file_object

                if file_output and file_output == 'optimal IDR thresholded peaks':
                    to_return['preferred_default_idr_peaks'][
                        file_object['@id']
                    ] = file_object
                if (
                    file_object.get('preferred_default')
                    and file_output == 'IDR thresholded peaks'
                ):
                    to_return['preferred_default_idr_peaks'][
                        file_object['@id']
                    ] = file_object

                if file_output and file_output == 'methylation state at CpG':
                    to_return['cpg_quantifications'][file_object['@id']
                                                     ] = file_object

                if file_output_category == 'raw data':
                    to_return['raw_data'][file_object['@id']] = file_object
                else:
                    to_return['processed_data'][file_object['@id']] = file_object

    return to_return


def get_contributing_files(files_list, excluded_types):
    to_return = {}
    if files_list:
        for file_object in files_list:
            if file_object['status'] not in excluded_types:
                to_return[file_object['@id']] = file_object
    return to_return


function_dispatcher_without_files = {
    'audit_geo_submission': audit_experiment_geo_submission
}

function_dispatcher_with_files = {
    'audit_released_with_unreleased_files': audit_experiment_released_with_unreleased_files
}

@audit_checker(
    'Dataset',
    frame=[
        'biosample_ontology',
        'award',
        'contributing_files',
        'original_files',
        'original_files.award'
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
