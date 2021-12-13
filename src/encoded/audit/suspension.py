from snovault import (
    AuditFailure,
    audit_checker,
)
from .formatter import (
    audit_link,
    path_to_text,
)


def audit_suspension_donor(value, system):
    '''
    A Suspension should have a donor.
    '''
    if value['status'] in ['deleted']:
        return

    if not value['donors']:
        detail = ('Suspension {} is not associated with any donor.'.format(
            audit_link(value['accession'], value['@id'])
            )
        )
        yield AuditFailure('missing donor', detail, level='ERROR')
        return


def audit_death_prop_living_donor(value, system):
    '''
    A suspension should not have a property indicating time since death
    if it is associated with a living donor.
    '''
    if value['status'] in ['deleted']:
        return

    living_donor_flag = False
    for donor in value['donors']:
        if donor.get('living_at_sample_collection') == True:
            living_donor_flag = True
    for death_prop in ['death_to_dissociation_interval']:
        if living_donor_flag == True and value.get(death_prop):
            detail = ('Biosample {} has property {} but is associated with at least one donor that is living at sample collection.'.format(
                audit_link(value['accession'], value['@id']),
                death_prop
                )
            )
            yield AuditFailure('death interval for living donor', detail, level='ERROR')
            return


def ontology_check_enr(value, system):
    field = 'enriched_cell_types'
    dbs = ['CL']

    invalid = []
    for e in value.get(field, []):
        term = e['term_id']
        ont_db = term.split(':')[0]
        if ont_db not in dbs:
            invalid.append(term)

    if invalid:
        detail = ('Suspension {} {} {} not from {}.'.format(
            audit_link(value['accession'], value['@id']),
            field,
            ','.join(invalid),
            ','.join(dbs)
            )
        )
        yield AuditFailure('incorrect ontology term', detail, 'ERROR')


def ontology_check_dep(value, system):
    field = 'depleted_cell_types'
    dbs = ['CL']

    invalid = []
    for e in value.get(field, []):
        term = e['term_id']
        ont_db = term.split(':')[0]
        if ont_db not in dbs:
            invalid.append(term)

    if invalid:
        detail = ('Suspension {} {} {} not from {}.'.format(
            audit_link(value['accession'], value['@id']),
            field,
            ','.join(invalid),
            ','.join(dbs)
            )
        )
        yield AuditFailure('incorrect ontology term', detail, 'ERROR')


function_dispatcher = {
    'audit_donor': audit_suspension_donor,
    'audit_death_prop_living_donor': audit_death_prop_living_donor,
    'ontology_check_enr': ontology_check_enr,
    'ontology_check_dep': ontology_check_dep
}

@audit_checker('Suspension',
               frame=[
                'donors',
                'enriched_cell_types',
                'depleted_cell_types'
                ])
def audit_suspension(value, system):
    for function_name in function_dispatcher.keys():
        for failure in function_dispatcher[function_name](value, system):
            yield failure
