from ..auditor import (
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
    }


@audit_checker('library')
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
            value['accession'],
            value['nucleic_acid_term_name'],
            value['nucleic_acid_term_id'],
            value['nucleic_acid_term_id'],
            expected)
        raise AuditFailure('mismatched nucleic_acid_term', detail, level='ERROR')


@audit_checker('library')
def audit_library_documents(value, system):
    '''
    If any of the library methods say <see document> then
    there needs to be a document.
    '''

    if value['status'] in ['deleted']:
        return

    list_of_methods = ['extraction_method',
                       'fragmentation_method',
                       'library_size_selection_method',
                       'lysis_method',
                       ]

    for method in list_of_methods:
        if value.get(method) == "see document" and value['documents'] == []:
            detail = 'Library {} has a method that specifies "see document" yet has no document'.format(
                value['accession']
                )
            raise AuditFailure('missing document', detail, level='ERROR')


@audit_checker('library')
def audit_library_RNA_size_range(value, system):
    '''
    An RNA library should have a size_range specified.
    This needs to accomodate the rfa
    '''

    if value['status'] in ['deleted']:
        return

    RNAs = ['SO:0000356', 'SO:0000871']

    if (value['nucleic_acid_term_id'] in RNAs) and ('size_range' not in value):
        detail = 'RNA library {} requires a value for size_range'.format(value['accession'])
        raise AuditFailure('missing size_range', detail, level='ERROR')


@audit_checker('library')
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
            value['accession'])
        yield AuditFailure('depleted_in length mismatch', detail, level='ERROR')

    for i, dep_term in enumerate(value['depleted_in_term_id']):
        if dep_term == value['nucleic_acid_term_id']:
            detail = 'Library {} of type {} cannot be depleted in {}'.format(
                value['accession'],
                value['nucleic_acid_term_id'],
                value['depleted_in_term_id'][i])
            yield AuditFailure('invalid depleted_in_term_id', detail, level='ERROR')

        expected = moleculeDict[value['depleted_in_term_name'][i]]
        if expected != value['depleted_in_term_id'][i]:
            detail = 'Library {} has mismatch between {} - {}'.format(
                value['accession'],
                value['depleted_in_term_name'][i],
                value['depleted_in_term_id'][i])
            yield AuditFailure('mismatched depleted_in_term', detail, level='ERROR')
