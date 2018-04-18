from snovault import (
    AuditFailure,
    audit_checker,
)


@audit_checker('Library', frame=['biosample'])
def audit_single_cell_libraries(value, system):
    if not value.get('barcode_details'):
        return
    biosample = value.get('biosample')
    if biosample:
        if biosample.get('biosample_type') != 'single cell':
            detail = ('The library {} prepared form {} biosample {} '
                     'has a specified barcode_details, which should '
                     'be specified onle for single cell biosamples.').format(
                         value['@id'],
                         biosample.get('biosample_type'),
                         biosample['@id']
                     )
            yield AuditFailure('inconsistent barcode details', detail, level='WARNING')