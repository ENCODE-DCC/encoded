from snovault import (
    AuditFailure,
    audit_checker,
)
from .formatter import (
    audit_link,
    path_to_text,
)


def audit_biosample_donor(value, system):
    '''
    A biosample should have a donor.
    '''
    if value['status'] in ['deleted']:
        return

    if not value['donors']:
        detail = ('Biosample {} is not associated with any donor.'.format(
            audit_link(value['accession'], value['@id'])
            )
        )
        yield AuditFailure('missing donor', detail, level='ERROR')
        return


def audit_death_prop_living_donor(value, system):
    '''
    A biosample should not have a property indicating time since death
    if it is associated with a living donor.
    '''
    if value['status'] in ['deleted']:
        return

    living_donor_flag = False
    for donor in value['donors']:
        if donor.get('living_at_sample_collection') == True:
            living_donor_flag = True
    for death_prop in ['death_to_preservation_interval']:
        if living_donor_flag == True and value.get(death_prop):
            detail = ('Biosample {} has property {} but is associated with at least one donor that is living at sample collection.'.format(
                audit_link(value['accession'], value['@id']),
                death_prop
                )
            )
            yield AuditFailure('death interval for living donor', detail, level='ERROR')
            return


def ontology_check_dis(value, system):
    field = 'diseases'
    dbs = ['MONDO']

    invalid  = []
    for d in value.get(field, []):
        term = d['term_id']
        ont_db = term.split(':')[0]
        if ont_db not in dbs:
            invalid.append(term)

    if invalid:
        detail = ('Biosample {} {} {} not from {}.'.format(
            audit_link(value['accession'], value['@id']),
            field,
            ','.join(invalid),
            ','.join(dbs)
            )
        )
        yield AuditFailure('incorrect ontology term', detail, 'ERROR')


function_dispatcher = {
    'audit_donor': audit_biosample_donor,
    'audit_death_prop_living_donor': audit_death_prop_living_donor,
    'ontology_check_dis': ontology_check_dis
}

@audit_checker('Biosample',
               frame=[
                'donors',
                'diseases'
                ])
def audit_biosample(value, system):
    for function_name in function_dispatcher.keys():
        for failure in function_dispatcher[function_name](value, system):
            yield failure
