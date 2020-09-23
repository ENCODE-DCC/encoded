from snovault import (
    AuditFailure,
    audit_checker,
)
from .formatter import (
    audit_link,
    path_to_text,
)


def audit_biosample_donor(value, system):
    '''
    A biosample should have a donor.
    The organism of donor and biosample should match.
    '''
    if value['status'] in ['deleted']:
        return

    if not value['donors']:
        detail = ('Biosample {} is not associated with any donor.'.format(
            audit_link(value['accession'], value['@id'])
            )
        )
        yield AuditFailure('missing donor', detail, level='ERROR')
        return


function_dispatcher = {
    'audit_donor': audit_biosample_donor,
}

@audit_checker('Biosample',
               frame=['donors'])
def audit_biosample(value, system):
    for function_name in function_dispatcher.keys():
        for failure in function_dispatcher[function_name](value, system):
            yield failure
