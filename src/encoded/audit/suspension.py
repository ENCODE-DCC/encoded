from snovault import (
    AuditFailure,
    audit_checker,
)
from .formatter import (
    audit_link,
    path_to_text,
)


def audit_suspension_donor(value, system):
    '''
    A Suspension should have a donor.
    '''
    if value['status'] in ['deleted']:
        return

    if not value['donors']:
        detail = ('Suspension {} is not associated with any donor.'.format(
            audit_link(value['accession'], value['@id'])
            )
        )
        yield AuditFailure('missing donor', detail, level='ERROR')
        return


function_dispatcher = {
    'audit_donor': audit_suspension_donor,
}

@audit_checker('Suspension',
               frame=['donors'])
def audit_suspension(value, system):
    for function_name in function_dispatcher.keys():
        for failure in function_dispatcher[function_name](value, system):
            yield failure
