from snovault import (
    AuditFailure,
    audit_checker,
)


moleculeDict = {
    'DNA': 'SO:0000352',
    'RNA': 'SO:0000356',
    'polyadenylated mRNA': 'SO:0000871',
    'miRNA': 'SO:0000276',
    'rRNA': 'SO:0000252',
    'capped mRNA': 'SO:0000862',
    'protein': 'SO:0000104'
    }


@audit_checker('library', frame='object')
def audit_library_nucleic_acid(value, system):
    '''
    The library needs the nucleic_acid_term_name to match the nucleic_acid_term_id.
    Niether of these terms should be missing, according to the schema.
    This audit should eventually be replaced by a calculated field.
    '''

    if value['status'] in ['deleted']:
        return

    expected = moleculeDict[value['nucleic_acid_term_name']]
    if expected != value['nucleic_acid_term_id']:
        detail = 'Library {} has nucleic_acid_term_name "{}" and nucleic_acid_term_id "{}". However {} is {}'.format(
            value['@id'],
            value['nucleic_acid_term_name'],
            value['nucleic_acid_term_id'],
            value['nucleic_acid_term_id'],
            expected)
        raise AuditFailure('inconsistent nucleic_acid_term', detail, level='ERROR')


@audit_checker('library', frame='object')
def audit_library_depleted_in(value, system):
    '''
    If there is a depleted_term_name or term_id,
    both should exist - should be handled by schema
    They should match each other.
    This should also be replaced by a calculated field
    '''

    if value['status'] in ['deleted']:
        return

    if not value['depleted_in_term_name'] or not value['depleted_in_term_id']:
        return

    if len(value['depleted_in_term_name']) != len(value['depleted_in_term_id']):
        detail = 'Library {} has depleted_in_term_name array and depleted_in_term_id array of differing lengths'.format(
            value['@id'])
        yield AuditFailure('depleted_in length mismatch', detail, level='ERROR')

    for i, dep_term in enumerate(value['depleted_in_term_id']):
        if dep_term == value['nucleic_acid_term_id']:
            detail = 'Library {} of type {} cannot be depleted in {}'.format(
                value['@id'],
                value['nucleic_acid_term_id'],
                value['depleted_in_term_id'][i])
            yield AuditFailure('invalid depleted_in_term_id', detail, level='ERROR')

        expected = moleculeDict[value['depleted_in_term_name'][i]]
        if expected != value['depleted_in_term_id'][i]:
            detail = 'Library {} has mismatch between {} - {}'.format(
                value['@id'],
                value['depleted_in_term_name'][i],
                value['depleted_in_term_id'][i])
            yield AuditFailure('inconsistent depleted_in_term', detail, level='ERROR')
