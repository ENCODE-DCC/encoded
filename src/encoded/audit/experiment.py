from ..auditor import (
    AuditFailure,
    audit_checker,
)


@audit_checker('example')
def audit_experiment_biosample_term(value, system):
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
    if ontology_term_name != term_name:
        detail = '{} - {} - {}'.format(term_id, term_name, ontology_term_name)
        raise AuditFailure('term name mismatch', detail, level='ERROR')

'''
Experiments should have assays with valid ontologies term ids and names that 
are coherent.
'''
@audit_checker('experiment')
def audit_experiment_assay(value, system):
    if 'assay_term_id' not in value:
        detail = 'missing'
        raise AuditFailure('missing assay term id', detail, level='ERROR')

    if 'assay_term_name' not in value:
        detail = 'missing'
        raise AuditFailure('missing assay term name', detail, level='ERROR')    
        
    ontology = system['registry']['ontology']
    term_id = value['assay_term_id']
    term_name = value.get('assay_term_name')

    if term_id.startswith('NTR:'):
        detail = '{} - {}'.format(term_id, term_name)
        raise AuditFailure('assay with NTR', detail, level='WARNING')

    if term_id not in ontology:
        raise AuditFailure('term id not in ontology', term_id, level='ERROR')

    ontology_term_name = ontology[term_id]['name']
    if ontology_term_name != term_name:
        detail = '{} - {} - {}'.format(term_id, term_name, ontology_term_name)
        raise AuditFailure('term name mismatch', detail, level='ERROR')


'''
Certain assay types (ChIP-seq, ...) require valid targets.  
'''
@audit_checker('experiment')
def audit_experiment_target(value, system):
    if 'assay_term_name' not in value or value['assay_term_name'] not in ['ChIP-seq']:
        return
 
    if 'target' not in value:
        detail = 'missing'
        raise AuditFailure('missing target', detail, level='ERROR')    
            
    ontology = system['registry']['ontology']
    target = value['target']

    if term_id.startswith('NTR:'):
        detail = '{} - {}'.format(term_id, term_name)
        raise AuditFailure('assay with NTR', detail, level='WARNING')

    if term_id not in ontology:
        raise AuditFailure('term id not in ontology', term_id, level='ERROR')

    ontology_term_name = ontology[term_id]['name']
    if ontology_term_name != term_name:
        detail = '{} - {} - {}'.format(term_id, term_name, ontology_term_name)
        raise AuditFailure('term name mismatch', detail, level='ERROR')