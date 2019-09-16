from snovault import (
    AuditFailure,
    audit_checker,
)
from .formatter import (
    audit_link,
    path_to_text,
)

@audit_checker('Donor', frame='object')
def audit_fly_worm_donor_genotype_dbxrefs(value, system):
    '''
    Fly and worm donors need their genotype information and dbxrefs
    filled out since the genotype will ge part of the biosample summary.
    '''
    if ('FlyDonor' in value['@type']) or ('WormDonor' in value['@type']):
        if 'genotype' not in value or not value['genotype']:
            detail = ('Strain {} should have a value '
                'specified for genotype.'.format(
                    audit_link(path_to_text(value['@id']), value['@id'])
                )
            )
            yield AuditFailure('missing genotype', detail, level='WARNING')
        if not value.get('dbxrefs') and not value.get('external_ids'):
            detail = ('Strain {} should have one or more ids '
                'specified in the dbxrefs or external_ids array.'.format(
                    audit_link(path_to_text(value['@id']), value['@id'])
                )
            )
            yield AuditFailure('missing external identifiers', detail, level='WARNING')
