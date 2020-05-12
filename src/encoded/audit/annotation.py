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


@audit_checker('Annotation')
def audit_annotation_derived_from_revoked(value, system):
    '''
    Annotations with files derived from a revoked file should be flagged with an audit.
    '''
    request = system.get('request')
    for file in value.get('files'):
        if 'derived_from' in file:
            for f in file['derived_from']:
                parent = request.embed(f + '@@object')
                if parent['status'] == 'revoked':
                    detail = (
                        f'Annotation {audit_link(path_to_text(value["@id"]), value["@id"])} '
                        f'includes a file {file["@id"]} that was derived from a revoked file {parent["@id"]}.')
                    raise AuditFailure('derived from revoked file', detail, level='WARNING')
