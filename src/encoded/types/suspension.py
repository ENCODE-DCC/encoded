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


def property_closure(request, propname, root_uuid):
    conn = request.registry[CONNECTION]
    seen = set()
    remaining = {str(root_uuid)}
    while remaining:
        seen.update(remaining)
        next_remaining = set()
        for uuid in remaining:
            obj = conn.get_by_uuid(uuid)
            next_remaining.update(obj.__json__(request).get(propname, ()))
        remaining = next_remaining - seen
    return seen


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
    def donors(self, request, registry):
        connection = registry[CONNECTION]
        derived_from_closure = property_closure(request, 'derived_from', self.uuid) - {str(self.uuid)}
        obj_props = (request.embed(uuid, '@@object') for uuid in derived_from_closure)
        all_donors = {
            props['accession']
            for props in obj_props
            if 'Donor' in props['@type']
        }
        return sorted(all_donors)
