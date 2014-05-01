from ..auditor import (
    AuditFailure,
    audit_checker,
)


@audit_checker('biosample')
def audit_biosample_term(value, system):
    if 'biosample_term_id' not in value:
        return
    ontology = system['registry']['ontology']
    term_id = value['biosample_term_id']
    term_name = value.get('biosample_term_name')

    if term_id.startswith('NTR:'):
        detail = '{} - {}'.format(term_id, term_name)
        raise AuditFailure('NTR', detail, level='WARNING')

    if term_id not in ontology:
        raise AuditFailure('term id not in ontology', term_id, level='WARNING')

    ontology_term_name = ontology[term_id]['name']
    if ontology_term_name != term_name or term_name not in ontology[term_id]['synonyms']:
        detail = '{} - {} - {}'.format(term_id, term_name, ontology_term_name)
        raise AuditFailure('term name mismatch', detail, level='ERROR')
