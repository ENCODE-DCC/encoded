from snovault import (
    AuditFailure,
    audit_checker,
)
from .formatter import (
    audit_link,
    path_to_text,
)

@audit_checker('Annotation', frame='object')
def audit_annotation_organism(value, system):
    '''
    Annotations need their organism to be specified
    This should eventually go to required schema element
    '''
    if value['status'] in ['replaced', 'revoked', 'deleted']:
        return

    if 'organism' not in value:
        detail = ('Annotation {} lacks organism information.'.format(audit_link(path_to_text(value['@id']), value['@id'])))
        raise AuditFailure('missing organism', detail, level='INTERNAL_ACTION')
