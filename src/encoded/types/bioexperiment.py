
from snovault import (
calculated_property,
collection,
load_schema,
)
from .base import (
Item,
# SharedItem,
paths_filtered_by_status,
)
from pyramid.traversal import find_root, resource_path
import re


@collection(
name='bioexperiments',
unique_key='accession',
properties={
    'title': 'Bioxperiments',
    'description': 'Bioexperiment information page',
},
)
class Bioexperiment(Item):
    item_type = 'bioexperiment'
    schema = load_schema('encoded:schemas/bioexperiment.json')
    name_key = 'accession'
    embedded = [
        'award',
        'lab',
        "submitted_by", #link to User
        # 'biospecimen',
        'bioreplicate',
        'bioreplicate.biolibrary',
        'bioreplicate.biolibrary.biospecimen'
        # "references", #link to Publication
        # 'documents',#link to Document
        

    ]
    rev = {
        'bioreplicate': ('Bioreplicate', 'bioexperiment'),

    }

    audit_inherit = [

    ]
    set_status_up = [
    ]
    set_status_down = [
    ]

    @calculated_property(
        schema={
            "title": "Bioreplicate",
            "type": "array",
            "items": {
                "type": 'string',
                "linkTo": "Bioreplicate"
            },
        }
    )
    def bioreplicate(self, request, bioreplicate):
        return paths_filtered_by_status(request, bioreplicate)









