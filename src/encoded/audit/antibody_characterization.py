from ..auditor import (
    AuditFailure,
    audit_checker,
)


@audit_checker('antibody_characterization')
def audit_antibody_characterization_review(value, system):
    if (value['status'] in ['not reviewed', 'not submitted for review by lab', 'deleted', 'in progress']):
        return

    if 'secondary_characterization_method' in value:
        return

    '''Make sure that biosample terms are in ontology for each characterization_review'''
    if value['characterization_reviews']:
        ontology = system['registry']['ontology']
        for review in value['characterization_reviews']:

            term_id = review['biosample_term_id']
            term_name = review['biosample_term_name']

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

@audit_checker('antibody_characterization')
def audit_antibody_characterization_unique_reviews(value, system):
    '''Make sure primary characterizations have unique lane, biosample_term_id and organism combinations for characterization reviews'''
    if(value['status'] in ["deleted", "not submitted for review by lab", 'in progress', 'not reviewed']):
        return

    if 'secondary_characterization_method' in value:
        return

    unique_reviews = set()
    for review in value['characterization_reviews']:
        lane = review['lane']
        term_id = review['biosample_term_id']
        organism = review['organism']
        review_lane = frozenset([lane, term_id, organism])
        if review_lane not in unique_reviews:
            unique_reviews.add(review_lane)
        else:
            detail = '{} - {} - {}'.format(lane, term_id, organism)
            raise AuditFailure('duplicate lane review', detail, level='ERROR')


@audit_checker('antibody_characterization')
def audit_antibody_characterization_target(value, system):
    '''Make sure that target in characterization matches target of antibody'''
    antibody = value['characterizes']
    target = value['target']
    if 'recombinant protein' in target['investigated_as']:
        prefix = target['label'].split('-')[0]
        unique_antibody_target = set()
        unique_investigated_as = set()
        for antibody_target in antibody['targets']:
            label = antibody_target['label']
            unique_antibody_target.add(label)
            for investigated_as in antibody_target['investigated_as']:
                unique_investigated_as.add(investigated_as)
        if 'tag' not in unique_investigated_as:
            detail = '{} is not to tagged protein'.format(antibody['@id'])
            raise AuditFailure('not tagged antibody', detail, level='ERROR')
        else:
            if prefix not in unique_antibody_target:
                detail = '{} not found in target for {}'.format(prefix, antibody['@id'])
                raise AuditFailure('tag target mismatch', detail, level='ERROR')
    else:
        target_matches = False
        for antibody_target in antibody['targets']:
            if target['name'] == antibody_target.get('name'):
                target_matches = True
        if not target_matches:
            detail = '{} not found in target for {}'.format(target['name'], antibody['@id'])
            raise AuditFailure('target mismatch', detail, level='ERROR')
