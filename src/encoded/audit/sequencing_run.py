from snovault import (
    AuditFailure,
    audit_checker,
)
from .formatter import (
    audit_link,
    path_to_text,
)


def audit_read_counts(value, system):
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
        yield AuditFailure('Variable read counts', detail, level='INTERNAL_ACTION')
        return


function_dispatcher = {
    'audit_read_counts': audit_read_counts,
}


@audit_checker('SequencingRun',
               frame=['object',
                      'derived_from',
                      'files'])
def audit_ontology_term(value, system):
    for function_name in function_dispatcher.keys():
        for failure in function_dispatcher[function_name](value, system):
            yield failure
