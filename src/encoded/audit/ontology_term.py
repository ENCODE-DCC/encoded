from snovault import (
    AuditFailure,
    audit_checker,
)
from .formatter import (
    audit_link,
    path_to_text,
)

def audit_term(value, system):
    '''
    The classification, term_id and term_name should all be present.
    This should be handled by schemas.
    The term_id should be in the ontology.
    The term_name should match the term_id.
    '''

    if value['status'] in ['deleted']:
        return

    ontology = system['registry']['ontology']
    term_name = value['term_name']
    term_id = value['term_id']

    if term_id.startswith('NTR:'):
        detail = ('OntologyTerm {} has a New Term Request {} - {}.'.format(
            audit_link(path_to_text(value['@id']), value['@id']),
            term_id,
            term_name
            )
        )
        yield AuditFailure('NTR term', detail, level='INTERNAL_ACTION')
        return

    if term_id not in ontology:
        detail = ('BiosampleType {} specifies a term_id {} '
            'that is not part of the {} ontology.'.format(
                audit_link(path_to_text(value['@id']), value['@id']),
                term_id,
                term_id.split(':', 1)[0]
            )
        )
        yield AuditFailure('term_id not in ontology', detail,
                           level='ERROR')
        return

    ontology_term_name = ontology[term_id]['name']
    if (ontology_term_name != term_name
        and term_name not in ontology[term_id]['synonyms']):
        detail = ('OntologyTerm {object_id} has a mismatch between'
            ' term_id ({term_id}) and term_name ({term_name}),'
            ' ontology term_name for term_id {term_id} is'
            ' {ontology_term_name}.'.format(
                object_id=audit_link(path_to_text(value['@id']), value['@id']),
                term_id=term_id,
                term_name=term_name,
                ontology_term_name=ontology_term_name
            )
        )
        yield AuditFailure('inconsistent ontology term', detail,
                           level='ERROR')


function_dispatcher = {
    'audit_ontology_term_term': audit_term,
}


@audit_checker('OntologyTerm', frame='object')
def audit_ontology_term(value, system):
    for function_name in function_dispatcher.keys():
        for failure in function_dispatcher[function_name](value, system):
            yield failure
