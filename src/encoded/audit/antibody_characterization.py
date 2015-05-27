from contentbase.auditor import (
    AuditFailure,
    audit_checker,
)
from .conditions import rfa


@audit_checker('antibody_characterization', frame=['characterization_reviews'])
def audit_antibody_characterization_review(value, system):
    '''
    Make sure that biosample terms are in ontology
    for each characterization_review.
    '''
    if (value['status'] in ['not reviewed', 'not submitted for review by lab', 'deleted', 'in progress']):
        return

    if 'secondary_characterization_method' in value:
        return

    if value['characterization_reviews']:
        ontology = system['registry']['ontology']
        for review in value['characterization_reviews']:
            term_id = review['biosample_term_id']
            term_name = review['biosample_term_name']

            if term_id.startswith('NTR:'):
                detail = 'Antibody_characterization {} contains a New Term Request {} - {}'.format(
                    value['@id'],
                    term_id,
                    term_name
                    )
                raise AuditFailure('NTR biosample', detail, level='DCC_ACTION')

            if term_id not in ontology:
                detail = 'Antibody characterization {} contains a biosample_term_id {} that is not in the ontology'.format(
                    value['@id'],
                    term_id
                    )
                raise AuditFailure('term_id not in ontology', term_id, level='DCC_ACTION')

            ontology_term_name = ontology[term_id]['name']
            if ontology_term_name != term_name and term_name not in ontology[term_id]['synonyms']:
                detail = 'Antibody characterization {} has a mismatched term {} - {} expected {}'.format(
                    value['@id'],
                    term_id,
                    term_name,
                    ontology_term_name)
                raise AuditFailure('mismatched term_name', detail, level='ERROR')


@audit_checker('antibody_characterization', frame=[
    'characterization_reviews',
    'characterization_reviews.lanes'
    ])
def audit_antibody_characterization_unique_reviews(value, system):
    '''
    Make sure primary characterizations have unique lane, biosample_term_id and
    organism combinations for characterization reviews
    '''
    if(value['status'] in ['deleted', 'not submitted for review by lab', 'in progress', 'not reviewed']):
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
            detail = 'Characterization_review.lane {} is a duplicate review for {} - {}'.format(
                lane,
                term_id,
                organism
                )
            raise AuditFailure('duplicate lane review', detail, level='ERROR')


@audit_checker('antibody_characterization', frame=[
    'target',
    'characterizes',
    'characterizes.targets'
    ])
def audit_antibody_characterization_target(value, system):
    '''
    Make sure that target in characterization
    matches target of antibody
    '''
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
            detail = 'Antibody {} is not for a tagged protein, yet target is investigated_as a recombinant protein'.format(antibody['@id'])
            raise AuditFailure('not tagged antibody', detail, level='ERROR')
        else:
            if prefix not in unique_antibody_target:
                detail = '{} is not found in target list for antibody {}'.format(
                    prefix,
                    antibody['@id']
                    )
                raise AuditFailure('mismatched tag target', detail, level='ERROR')
    else:
        target_matches = False
        for antibody_target in antibody['targets']:
            if target['name'] == antibody_target.get('name'):
                target_matches = True
        if not target_matches:
            detail = 'Target {} is not found in target list for antibody {}'.format(
                target['name'],
                antibody['@id']
                )
            raise AuditFailure('mismatched target', detail, level='ERROR')


@audit_checker('antibody_characterization', frame=[
    'characterization_reviews',
    'characterization_reviews.lanes'
    ])
def audit_antibody_characterization_status(value, system):
    '''
    Make sure the lane_status matches
    the characterization status
    '''
    if 'secondary_characterization_method' in value:
        return

    if(value['status'] in ["deleted", "not submitted for review by lab", 'in progress', 'not reviewed']):
        if 'characterization_reviews' in value:
            '''If any of these statuses, we shouldn't have characterization_reviews'''
            detail = 'Antibody_characterization.status of {} is incompatible with having a value for characterization_reviews'.format(value['status'])
            raise AuditFailure('unexpected characterization_reviews', detail, level='WARNING')
        else:
            return

    '''Check each of the lane_statuses in characterization_reviews for an appropriate match'''
    has_compliant_lane = False
    is_pending = False
    if value['status'] == 'pending dcc review':
        is_pending = True
    for lane in value['characterization_reviews']:
        if (is_pending and lane['lane_status'] != 'pending dcc review') or (not is_pending and lane['lane_status'] == 'pending dcc review'):
            detail = 'A lane.status of {} is incompatible with antibody_characterization.status of pending dcc review'.format(lane['lane_status'])
            raise AuditFailure('mismatched lane status', detail, level='WARNING')
            continue

        if lane['lane_status'] == 'compliant':
            has_compliant_lane = True

    if has_compliant_lane and value['status'] != 'compliant':
        detail = 'A lane.status of {} is incompatible with antibody_characterization status of {}'.format(lane['lane_status'], value['status'])
        raise AuditFailure('mismatched lane status', detail, level='DCC_ACTION')


@audit_checker('antibody_characterization', frame=['target'], condition=rfa('ENCODE3'))
def audit_antibody_characterization_method_allowed(value, system):
    '''
    Warn if a lab submits an ENCODE3 characterization if
    the method is not yet approved by the standards document.
    '''
    if 'primary_characterization_method' in value:
        return

    target = value['target']
    is_histone = False
    if 'histone modification' in target['investigated_as']:
        is_histone = True

    secondary = value['secondary_characterization_method']
    if (secondary == 'motif enrichment') or (is_histone and secondary == 'ChIP-seq comparison'):
        detail = '{} is not an approved secondary_characterization_method according to the current standards'.format(value['secondary_characterization_method'])
        raise AuditFailure('unapproved char method', detail, level='NOT_COMPLIANT')
