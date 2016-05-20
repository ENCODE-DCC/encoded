from snovault import (
    AuditFailure,
    audit_checker,
)
from .conditions import rfa


@audit_checker('antibody_lot', frame=['characterizations'],
               condition=rfa('ENCODE3', 'modERN'))
def audit_antibody_missing_characterizations(value, system):
    '''
    Check to see what characterizations are lacking for each antibody,
    for the cell lines we know about.
    '''
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

    if len(primary_chars) != num_compliant_primary:
        detail = '{} '.format(value['@id']) + \
            'needs compliant primary in one or more cell types.'
        yield AuditFailure('need compliant primaries', detail,
                           level='NOT_COMPLIANT')

    if secondary_chars and not compliant_secondary:
        detail = '{} '.format(value['@id']) + \
            'needs a compliant secondary characterization.'
        yield AuditFailure('need compliant secondary', detail,
                           level='NOT_COMPLIANT')
        return
