from snovault import (
    AuditFailure,
    audit_checker,
)
from .formatter import (
    audit_link,
    path_to_text,
)


def ontology_check_dev(value, system):
    field = 'development_ontology'
    dbs = ['MmusDv']

    term = value[field]['term_id']
    ont_db = term.split(':')[0]
    if ont_db not in dbs:
        detail = ('Donor {} {} {} not from {}.'.format(
            audit_link(value['accession'], value['@id']),
            field,
            term,
            ','.join(dbs)
            )
        )
        yield AuditFailure('incorrect ontology term', detail, 'ERROR')


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
        detail = ('Donor {} {} {} not from {}.'.format(
            audit_link(value['accession'], value['@id']),
            field,
            ','.join(invalid),
            ','.join(dbs)
            )
        )
        yield AuditFailure('incorrect ontology term', detail, 'ERROR')


function_dispatcher = {
    'ontology_check_dev': ontology_check_dev,
    'ontology_check_dis': ontology_check_dis
}

@audit_checker('MouseDonor',
               frame=[
                'development_ontology',
                'diseases'
                ])
def audit_mouse_donor(value, system):
    for function_name in function_dispatcher.keys():
        for failure in function_dispatcher[function_name](value, system):
            yield failure
