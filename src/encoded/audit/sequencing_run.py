from snovault import (
    AuditFailure,
    audit_checker,
)
from .formatter import (
    audit_link,
    path_to_text,
)


def no_platform(value, system):
    if value['status'] in ['deleted']:
        return

    if not value.get('platform'):
        detail = ('SequencingRun {} has no platform specified.'.format(
            audit_link(path_to_text(value['@id']), value['@id'])
            )
        )
        yield AuditFailure('no platform specified', detail, level='ERROR')
        return


def audit_read_counts(value, system):
    '''
    All sequence files belonging to a SequencingRun
    should have the same number of reads.
    '''
    if value['status'] in ['deleted']:
        return

    read_count_lib = set()
    for f in value.get('files'):
        read_count_lib.add(f.get('read_count'))
    if len(read_count_lib) != 1:
        detail = ('SequencingRun {} has files of variable read counts - {}.'.format(
            audit_link(path_to_text(value['@id']), value['@id']),
            read_count_lib
            )
        )
        yield AuditFailure('variable read counts', detail, level='ERROR')
        return


def audit_required_files(value, system):
    '''
    All sequence files belonging to a SequencingRun
    should have the same number of reads.
    '''
    if value['status'] in ['deleted']:
        return

    not_found = []
    protocol = value['derived_from'][0].get('protocol')
    for f in protocol['required_files']:
        file_prop_name = (f + '_file').replace('Read ', 'read_')
        if not value.get(file_prop_name):
            not_found.append(f)
    if not_found:
        detail = ('SequencingRun {} is missing {}, required based on standards for {}.'.format(
            audit_link(path_to_text(value['@id']), value['@id']),
            ','.join(not_found),
            audit_link(path_to_text(protocol['@id']), protocol['@id'])
            )
        )
        yield AuditFailure('missing required file', detail, level='ERROR')
        return


function_dispatcher = {
    'audit_read_counts': audit_read_counts,
    'audit_required_files': audit_required_files,
    'no_platform': no_platform
}


@audit_checker('SequencingRun',
               frame=['object',
                      'derived_from',
                      'derived_from.protocol',
                      'files'])
def audit_sequencing_run(value, system):
    for function_name in function_dispatcher.keys():
        for failure in function_dispatcher[function_name](value, system):
            yield failure
