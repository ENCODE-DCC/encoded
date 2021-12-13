from snovault import (
    AuditFailure,
    audit_checker,
)
from .formatter import (
    audit_link,
    path_to_text,
)


def ontology_check_dis(value, system):
    field = 'experimental_variable_disease'
    dbs = ['MONDO']

    ontobj = value.get(field)
    if ontobj:
        term = ontobj['term_id']
        ont_db = term.split(':')[0]
        if ont_db not in dbs:
            detail = ('File {} {} {} not from {}.'.format(
                audit_link(value['accession'], value['@id']),
                field,
                term,
                ','.join(dbs)
                )
            )
            yield AuditFailure('incorrect ontology term', detail, 'ERROR')


function_dispatcher = {
    'ontology_check_dis': ontology_check_dis
}

@audit_checker('ProcessedMatrixFile',
               frame=[
                'experimental_variable_disease'
                ])
def audit_processed_matrix_file(value, system):
    for function_name in function_dispatcher.keys():
        for failure in function_dispatcher[function_name](value, system):
            yield failure
