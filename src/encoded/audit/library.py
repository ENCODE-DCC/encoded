from snovault import (
    AuditFailure,
    audit_checker,
)
from .formatter import (
    audit_link,
    path_to_text,
)

@audit_checker('Library', frame=['biosample', 'biosample.biosample_ontology'])
def audit_single_cell_libraries(value, system):
    if not value.get('barcode_details'):
        return
    biosample = value.get('biosample')
    if biosample:
        if biosample.get('biosample_ontology', {}).get('classification') != 'single cell':
            detail = ('The library {} prepared form {} biosample {} '
                'has a specified barcode_details, which should '
                'be specified onle for single cell biosamples.'.format(
                    audit_link(path_to_text(value['@id']), value['@id']),
                    biosample.get('biosample_ontology', {}).get('classification'),
                    audit_link(path_to_text(biosample['@id']), biosample['@id'])
                )
            )
            yield AuditFailure('inconsistent barcode details', detail, level='WARNING')
