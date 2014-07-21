from ..auditor import (
    AuditFailure,
    audit_checker,
)


@audit_checker('biosample')
def audit_biosample_term(value, system):
    if value['status'] == 'deleted':
        return
    
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
    if ontology_term_name != term_name and term_name not in ontology[term_id]['synonyms']:
        detail = '{} - {} - {}'.format(term_id, term_name, ontology_term_name)
        raise AuditFailure('term name mismatch', detail, level='ERROR')


@audit_checker('biosample')
def audit_biosample_culture_date(value, system):
    if value['culture_harvest_date'] <= value['culture_start_date']:
        detail = 'culture_harvest_date precedes culture_start_date'
        raise AuditFailure('invalid dates', detail, level='ERROR')


@audit_checker('biosample')
def audit_biosample_donor(value, system):
    if (not value['donor']) and (not value['pooled_from']):
        detail = 'biosample donor is missing'
        raise AuditFailure('missing donor', detail, level='ERROR')

    if value['organism']['name'] != value['donor']['organism']['name']:
        detail = 'biosample and donor organism mismatch'
        raise AuditFailure('organism mismatch') 
