from snovault import (
    AuditFailure,
    audit_checker,
)


@audit_checker('Donor', frame='object')
def audit_fly_worm_donor_genotype_dbxrefs(value, system):
    '''
    Fly and worm donors need their genotype information and dbxrefs
    filled out since the genotype will ge part of the biosample summary.
    '''
    if ('FlyDonor' in value['@type']) or ('WormDonor' in value['@type']):
        if 'genotype' not in value or not value['genotype']:
            detail = 'Strain {} should have a value '.format(value['@id']) + \
                'specified for genotype.'
            yield AuditFailure('missing genotype', detail, level='WARNING')
        if not value['dbxrefs']:
            detail = 'Strain {} should have one or more ids '.format(value['@id']) + \
                'specified in the dbxrefs array.'
            yield AuditFailure('missing dbxrefs', detail, level='WARNING')
