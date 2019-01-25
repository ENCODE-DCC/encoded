from snovault import (
    AuditFailure,
    audit_checker,
)
from .conditions import rfa


@audit_checker('antibody_characterization', frame=[
    'characterization_reviews',
    'characterization_reviews.lanes'
    ])
def audit_antibody_characterization_unique_reviews(value, system):
    '''
    Make sure primary characterizations have unique lane, BiosampleType and
    organism combinations for characterization reviews
    '''
    if(value['status'] in ['deleted', 'not submitted for review by lab', 'in progress', 'not reviewed']):
        return

    if 'secondary_characterization_method' in value:
        return

    unique_reviews = set()
    for review in value['characterization_reviews']:
        lane = review['lane']
        biosample_ontology = review['biosample_ontology']
        organism = review['organism']
        review_lane = frozenset([lane, biosample_ontology, organism])
        if review_lane not in unique_reviews:
            unique_reviews.add(review_lane)
        else:
            detail = 'Lane {} in {} is a duplicate review for {} - {}'.format(
                lane,
                value['@id'],
                biosample_ontology,
                organism
                )
            raise AuditFailure('duplicate lane review', detail, level='INTERNAL_ACTION')


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
        if ('tag' not in unique_investigated_as
            and 'synthetic tag' not in unique_investigated_as):
            detail = 'Antibody {} is not for a tagged protein, yet target {} in {} is investigated_as a recombinant protein'.format(
                antibody['@id'],
                prefix,
                value['@id']
                )
            raise AuditFailure('not tagged antibody', detail, level='ERROR')
        else:
            if prefix not in unique_antibody_target:
                detail = '{} is not found in target list in {} for antibody {}'.format(
                    prefix,
                    value['@id'],
                    antibody['@id']
                    )
                raise AuditFailure('mismatched tag target', detail, level='ERROR')
    else:
        target_matches = False
        antibody_targets = []
        for antibody_target in antibody['targets']:
            antibody_targets.append(antibody_target.get('name'))
            if target['name'] == antibody_target.get('name'):
                target_matches = True
        if not target_matches:
            antibody_targets_string = str(antibody_targets).replace('\'', '')
            detail = 'Antibody characterization {} target is {}, '.format(
                value['@id'],
                target['name']) + \
                'but it could not be found in antibody\'s {} '.format(antibody['@id']) + \
                'target list {}.'.format(antibody_targets_string)
            raise AuditFailure('inconsistent target', detail, level='ERROR')


@audit_checker('antibody_characterization', frame=[
    'characterization_reviews',
    'characterization_reviews.lanes'
    ])
def audit_antibody_characterization_status(value, system):
    '''
    Make sure the lane_status matches
    the characterization status
    '''

    if (value['status'] in ['not reviewed', 'not submitted for review by lab', 'deleted', 'in progress']):
        return

    if 'secondary_characterization_method' in value:
        return

    '''Check each of the lane_statuses in characterization_reviews for an appropriate match'''
    has_compliant_lane = False
    is_pending = False
    if value['status'] == 'pending dcc review':
        is_pending = True
    for lane in value['characterization_reviews']:
        if (is_pending and lane['lane_status'] != 'pending dcc review') or (not is_pending and lane['lane_status'] == 'pending dcc review'):
            detail = 'A lane.status of {} in {} is incompatible with antibody_characterization.status of {}'.format(
                lane['lane_status'],
                value['@id'],
                value['status']
                )
            raise AuditFailure('mismatched lane status', detail, level='INTERNAL_ACTION')
            continue

        if lane['lane_status'] == 'compliant':
            has_compliant_lane = True

    if has_compliant_lane and value['status'] != 'compliant':
        detail = 'A lane.status of {} in {} is incompatible with antibody_characterization status of {}'.format(
            lane['lane_status'],
            value['@id'],
            value['status']
            )
        raise AuditFailure('mismatched lane status', detail, level='INTERNAL_ACTION')


@audit_checker('antibody_characterization', condition=rfa('ENCODE3', 'modERN', 'ENCODE4'))
def audit_antibody_pending_review(value, system):
    ''' Pending dcc review characterizsations should be flagged for review if from ENCODE3, modERN'''
    if (value['status'] in ['compliant',
                            'not compliant',
                            'exempt from standards'
                            'not reviewed', 
                            'not submitted for review by lab',
                            'deleted',
                            'in progress']):
        return
    if value['status'] == 'pending dcc review':
        detail = '{} has characterization(s) needing review.'.format(value['@id'])
        raise AuditFailure('characterization(s) pending review', detail, level='INTERNAL_ACTION')
