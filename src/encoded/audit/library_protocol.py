from snovault import (
    AuditFailure,
    audit_checker,
)
from .formatter import (
    audit_link,
    path_to_text,
)


def ontology_check_assay(value, system):
    field = 'assay_ontology'
    dbs = ['EFO']

    ontobj = value.get(field)
    if ontobj:
        term = ontobj['term_id']
        ont_db = term.split(':')[0]
        if ont_db not in dbs:
            detail = ('LibraryProtocol {} {} {} not from {}.'.format(
                audit_link(value['@id'], value['@id']),
                field,
                term,
                ','.join(dbs)
                )
            )
            yield AuditFailure('incorrect ontology term', detail, 'ERROR')


function_dispatcher = {
    'ontology_check_assay': ontology_check_assay
}

@audit_checker('LibraryProtocol',
               frame=[
                'assay_ontology'
                ])
def audit_library_protocol(value, system):
    for function_name in function_dispatcher.keys():
        for failure in function_dispatcher[function_name](value, system):
            yield failure
