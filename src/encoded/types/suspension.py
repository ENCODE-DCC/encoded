from snovault import (
    abstract_collection,
    calculated_property,
    collection,
    CONNECTION,
    load_schema,
)
from .base import (
    Item,
    paths_filtered_by_status,
)
import re


@collection(
    name='suspensions',
    unique_key='accession',
    properties={
        'title': 'Suspensions',
        'description': 'Listing of Suspensions',
    })
class Suspension(Item):
    item_type = 'suspension'
    schema = load_schema('encoded:schemas/suspension.json')
    embedded = [
        'biosample_ontology',
        'donors',
        'donors.diseases',
        'donors.ethnicity'
    ]


    @calculated_property(define=True,
                         schema={"title": "Donors",
                                 "description": "The donors the sample was derived from.",
                                 "comment": "Do not submit. This is a calculated property",
                                 "type": "array",
                                 "items": {
                                    "type": "string",
                                    "linkTo": "Donor"
                                    }
                                })
    def donors(self, request, derived_from):
        all_donors = set()
        for bs in derived_from:
            bs_obj = request.embed(bs, '@@object')
            if 'Donor' in bs_obj.get('@type'):
                all_donors.add(bs_obj.get('@id'))
            else:
                all_donors.update(bs_obj.get('donors'))
        return sorted(all_donors)
