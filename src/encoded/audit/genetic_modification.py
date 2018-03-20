from snovault import (
    AuditFailure,
    audit_checker,
)

# flag genetic modifications with purpose "tagging" that lack genetic modification characterization.
def audit_tagging_modification(value, system):
    if value['purpose'] == 'tagging' and\
       not value.get('characterizations'):
        detail = ('Genetic modification {} performed for the '
                  'purpose of {} is missing validating characterization.').format(
            value['@id'],
            value['purpose']
        )
        yield AuditFailure(
            'missing genetic modification characterization',
            detail,
            level='WARNING')
        return


function_dispatcher = {
    'audit_tag': audit_tagging_modification,
}

@audit_checker('GeneticModification',
               frame=['characterizations'])
def audit_modification(value, system):
    for function_name in function_dispatcher.keys():
        for failure in function_dispatcher[function_name](value, system):
            yield failure
