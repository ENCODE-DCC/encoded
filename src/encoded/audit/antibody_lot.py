from snovault import (
    AuditFailure,
    audit_checker,
)
from .conditions import rfa


@audit_checker('antibody_lot', frame=[
    'targets',
    'characterizations',
    'characterizations.target'],
    condition=rfa('ENCODE3', 'modERN'))
def audit_antibody_missing_characterizations(value, system):
    '''
    Check to see what characterizations are lacking for each antibody,
    for the cell lines we know about.
    '''
    if value['targets'][0].get('investigated_as') in ['control']:
        return

    if not value['characterizations']:
        detail = '{} '.format(value['@id']) + \
            'does not have any supporting characterizations submitted.'
        yield AuditFailure('no characterizations submitted', detail,
                           level='NOT_COMPLIANT')
        return

    primary_chars = []
    secondary_chars = []
    num_compliant_primary = 0
    compliant_secondary = False
    for char in value['characterizations']:
        if 'primary_characterization_method' in char:
            primary_chars.append(char)
            if char['status'] in ['compliant', 'exempt from standards']:
                num_compliant_primary += 1
        if 'secondary_characterization_method' in char:
            secondary_chars.append(char)
            if char['status'] in ['compliant', 'exempt from standards']:
                compliant_secondary = True

    if not primary_chars:
        detail = '{} '.format(value['@id']) + \
            'does not have any primary characterizations submitted.'
        yield AuditFailure('no primary characterizations', detail,
                           level='NOT_COMPLIANT')

    if not secondary_chars:
        detail = '{} '.format(value['@id']) + \
            'does not have any secondary characterizations submitted.'
        yield AuditFailure('no secondary characterizations', detail,
                           level='NOT_COMPLIANT')

    if value['lot_reviews'][0]['detail'] in ['Characterizations not reviewed.']:
        detail = '{} has old characterizations that were not reviewed.'.format(
            value['@id'])
        yield AuditFailure('characterizations not reviewed', detail, level='WARNING')

    for lot_review in value['lot_reviews']:
        if lot_review['detail'] in [
            'Pending review of primary characterization.',
            'Primary characterization(s) in progress.',
            'Pending review of primary and secondary characterizations.',
            'Pending review of primary and awaiting submission of secondary characterization(s).',
            'Awaiting compliant primary and secondary characterizations.',
            'Awaiting a compliant primary characterization.',
            'Secondary characterization(s) in progress.'
        ]:
            biosample = lot_review['biosample_term_name']
            if biosample == 'not specified':
                biosample = 'one or more cell types/tissues.'

            detail = '{} needs a compliant primary in {}'.format(
                value['@id'],
                lot_review['biosample_term_name'])
            yield AuditFailure('need compliant primaries', detail,
                               level='NOT_COMPLIANT')

        if lot_review['detail'] is None and lot_review['status'] == 'awaiting characterization':
            detail = '{} needs a compliant primary characterization for one or more cell ' + \
                'types/tissues.'.format(value['@id'])
            yield AuditFailure('need compliant primaries', detail,
                               level='NOT_COMPLIANT')

    if secondary_chars and not compliant_secondary:
        detail = '{} '.format(value['@id']) + \
            'needs a compliant secondary characterization.'
        yield AuditFailure('need compliant secondary', detail,
                           level='NOT_COMPLIANT')
        return
