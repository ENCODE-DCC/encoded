from snovault import (
    AuditFailure,
    audit_checker,
)
from .formatter import (
    audit_link,
    path_to_text,
)


def audit_age_collection(value, system):
    '''
    A biosample should have a donor.
    '''
    if value['status'] in ['deleted']:
        return

    if 'age_at_collection' in value:
        donor_age = value['donors'][0].get('age')
        if donor_age != 'variable':
            detail = ('Tissue {} should not have age_at_collection unless donor age is variable.'.format(
                audit_link(value['accession'], value['@id'])
                )
            )
            yield AuditFailure('age_at_collection inconsistency', detail, level='ERROR')
            return

    elif value['donors'][0].get('age') == 'variable':
            detail = ('Tissue {} should have age_at_collection if donor age is variable.'.format(
                audit_link(value['accession'], value['@id'])
                )
            )
            yield AuditFailure('age_at_collection inconsistency', detail, level='ERROR')
            return


function_dispatcher = {
    'audit_age_collection': audit_age_collection
}

@audit_checker('Tissue',
               frame=['donors'])
def audit_tissue(value, system):
    for function_name in function_dispatcher.keys():
        for failure in function_dispatcher[function_name](value, system):
            yield failure
