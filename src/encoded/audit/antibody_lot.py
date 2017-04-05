from snovault import (
    AuditFailure,
    audit_checker,
)
from .conditions import rfa


@audit_checker('AntibodyLot', frame='object')
def audit_antibody_dbxrefs_ar(value, system):
    dbxrefs = value.get('dbxrefs')
    if dbxrefs:
        for entry in dbxrefs:
            if entry.startswith('AR:'):
                return
    detail = '{} '.format(value['@id']) + \
             'does not have AR dbxrefs.'
    yield AuditFailure('missing antibody registry reference', detail,
                       level='INTERNAL_ACTION')


@audit_checker('AntibodyLot', frame=[
    'targets',
    'characterizations',
    'characterizations.target'],
    condition=rfa('ENCODE3', 'modERN'))
def audit_antibody_missing_characterizations(value, system):
    '''
    Check to see what characterizations are lacking for each antibody,
    for the cell lines we know about.
    '''
    for t in value['targets']:
        if 'control' in t.get('investigated_as'):
            return

    if not value['characterizations']:
        detail = '{} does not have any supporting characterizations submitted.'.format(value['@id'])
        yield AuditFailure('no characterizations submitted', detail, level='NOT_COMPLIANT')
        return

    primary_chars = []
    secondary_chars = []
    compliant_secondary = False
    need_review = False
    for char in value['characterizations']:
        if char['status'] == 'pending dcc review':
            need_review = True
        if 'primary_characterization_method' in char:
            primary_chars.append(char)
        if 'secondary_characterization_method' in char:
            secondary_chars.append(char)
            if char['status'] in ['compliant', 'exempt from standards']:
                compliant_secondary = True

    if not primary_chars:
        detail = '{} does not have any primary characterizations submitted.'.format(value['@id'])
        yield AuditFailure('no primary characterizations', detail, level='NOT_COMPLIANT')

    if not secondary_chars:
        detail = '{} does not have any secondary characterizations submitted.'.format(value['@id'])
        yield AuditFailure('no secondary characterizations', detail, level='NOT_COMPLIANT')

    if need_review:
        detail = '{} has characterization(s) needing review.'.format(value['@id'])
        yield AuditFailure('characterization(s) pending review', detail, level='INTERNAL_ACTION')

    for lot_review in value['lot_reviews']:
        if lot_review['detail'] in \
            ['Awaiting a compliant primary and pending review of a secondary characterization.',
             'Awaiting a compliant primary and secondary characterization was not reviewed.',
             'Awaiting a compliant primary and submission of a secondary characterization.',
             'Awaiting a compliant primary characterization.',
             'Awaiting compliant primary and secondary characterizations.',
             'Primary characterization not reviewed and awaiting a compliant secondary characterization.',
             'Primary characterization not reviewed and pending review of a secondary characterization.',
             'Primary characterization not reviewed.',
             'Pending review of primary and secondary characterizations.',
             'Pending review of primary characterization and awaiting a compliant secondary characterization.',
             'Pending review of primary characterization and secondary characterization not reviewed.',
             'Pending review of primary characterization.']:
            biosample = lot_review['biosample_term_name']
            if biosample == 'any cell type or tissue':
                biosample = 'one or more cell types/tissues.'

            detail = '{} needs a compliant primary in {}'.format(value['@id'], biosample)
            yield AuditFailure('need compliant primaries', detail, level='NOT_COMPLIANT')

    if secondary_chars and not compliant_secondary:
        detail = '{} needs a compliant secondary characterization.'.format(value['@id'])
        yield AuditFailure('need compliant secondary', detail, level='NOT_COMPLIANT')
        return
