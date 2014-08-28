from ..auditor import (
    AuditFailure,
    audit_checker,
)


@audit_checker('antibody_characterization')
def audit_antibody_characterization_review(value, system):
    if (value['status'] in ['not reviewed', 'not submitted for review by lab', 'deleted']):
        return

    '''Make sure primary characterizations have characterization review subobjects'''
    if ('secondary_characterization_method' in value):
        return

    '''Make sure the lane information is filled out in characterization_review'''
    if value['characterization_reviews']:
        ontology = system['registry']['ontology']
        for review in value['characterization_reviews']:

            term_id = review['biosample_term_id']
            term_name = review['biosample_term_name']
            print "ontology: %s" % ontology

            if term_id.startswith('NTR:'):
                detail = '{} - {}'.format(term_id, term_name)
                raise AuditFailure('NTR', detail, level='WARNING')

            if term_id not in ontology:
                raise AuditFailure('term id not in ontology', term_id, level='WARNING')

            ontology_term_name = ontology[term_id]['name']
            if ontology_term_name != term_name and term_name not in ontology[term_id]['synonyms']:
                detail = '{} - {} - {}'.format(term_id, term_name, ontology_term_name)
                raise AuditFailure('term name mismatch', detail, level='ERROR')


@audit_checker('antibody_characterization')
def audit_antibody_characterization_standards(value, system):
    '''Make sure that a standards document is attached if status is compliant or not compliant.'''
    if (value['status'] in ['compliant', 'not compliant']):
        has_standards = False
        for document in value['documents']:
            if document.get('document_type') == 'standards document':
                has_standards = True
        if not has_standards:
            detail = 'Missing standards document'
            raise AuditFailure('missing standards', detail, level='ERROR')