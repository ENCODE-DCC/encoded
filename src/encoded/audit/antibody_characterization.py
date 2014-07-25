from ..auditor import (
    AuditFailure,
    audit_checker,
)

@audit_checker('antibody_characterization')
def audit_antibody_characterization_method(value, system):
    if (value['status'] in ['not reviewed', 'not submitted for review by lab', 'deleted']):
        return

    '''Make sure the characterization method is specified'''
    if ('primary_characterization_method' not in value) and ('secondary_characterization_method' not in value):
        detail = 'characterization_method must be specified'
        yield AuditFailure('missing characterization_method', detail, level='ERROR')


@audit_checker('antibody_characterization')
def audit_antibody_characterization_review(value, system):
    if (value['status'] in ['not reviewed', 'not submitted for review by lab', 'deleted']):
        return

    '''Make sure primary characterizations have characterization review subobjects'''
    if ('secondary_characterization_method' in value):
        return

    if not value['characterization_review']:
        detail = 'primary characterizations require a characterization_review'
        yield AuditFailure('missing characterization_review', detail, level='ERROR')

    '''Make sure the lane information is filled out in characterization_review'''
    if value['characterization_review']:
        ontology = system['registry']['ontology']
        for review in value['characterization_review']:

            if 'lane' not in review:
                detail = 'biosample_term_id is required for each lane'
                yield AuditFailure('missing lane', detail, level='ERROR')

            if 'organism' not in review:
                detail = 'organism is required for each lane'
                yield AuditFailure('missing organism', detail, level='ERROR')

            if 'biosample_type' not in review:
                detail = 'biosample_type is required for each lane'
                yield AuditFailure('missing biosample_type', detail, level='ERROR')

            if 'biosample_term_id' not in review or 'biosample_term_name' not in review:
                detail = 'biosample is required for each lane'
                yield AuditFailure('missing biosample', detail, level='ERROR')

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
