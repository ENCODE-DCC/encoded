from snovault import (
    calculated_property,
    collection,
    load_schema,
)
from .base import (
    Item,
    paths_filtered_by_status,
)
import re


@collection(
    name='biospecimens',
    unique_key='accession',
    properties={
        'title': 'Biospecimens',
        'description': 'Biospecimens used or available',
    })
class Biospecimen(Item):
    item_type = 'biospecimen'
    schema = load_schema('encoded:schemas/biospecimen.json')
    name_key = 'accession'
    rev = {
    }
    embedded = [
        'patient',
        'originated_from',
    ]
    audit_inherit = [
    ]
    set_status_up = [
        'patient',
        'originated_from',
    ]
    set_status_down = []
