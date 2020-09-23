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


def caclulate_donor_prop(self, request, donors, propname):
    collected_values = []

    if donors is not None:  # try to get the sex from the donor
        for donor_id in donors:
            donorObject = request.embed(donor_id, '@@object')
            if propname in donorObject and donorObject[propname] not in collected_values:
                if isinstance(donorObject[propname], str):
                    collected_values.append(donorObject[propname])
                elif isinstance(donorObject[propname], list):
                    for i in donorObject[propname]:
                        collected_values.append(i)

    if not collected_values:
        return ['']
    else:
        return collected_values


@abstract_collection(
    name='biosamples',
    unique_key='accession',
    properties={
        'title': 'Biosamples',
        'description': 'Listing of all types of biosample.',
    })
class Biosample(Item):
    base_types = ['Biosample'] + Item.base_types
    name_key = 'accession'
    rev = {}
    embedded = [
        'biosample_ontology'
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

@abstract_collection(
    name='cultures',
    unique_key='accession',
    properties={
        'title': 'Cultures',
        'description': 'Listing of all types of culture.',
    })
class Culture(Biosample):
    item_type = 'analysis_file'
    base_types = ['Culture'] + Biosample.base_types
    schema = load_schema('encoded:schemas/culture.json')
    embedded = Biosample.embedded + []


@collection(
    name='cell-cultures',
    unique_key='accession',
    properties={
        'title': 'Cell cultures',
        'description': 'Listing of Cell cultures',
    })
class CellCulture(Culture):
    item_type = 'cell_culture'
    schema = load_schema('encoded:schemas/cell_culture.json')
    embedded = Culture.embedded + []


@collection(
    name='organoids',
    unique_key='accession',
    properties={
        'title': 'Organoids',
        'description': 'Listing of Organoids',
    })
class Organoid(Culture):
    item_type = 'organoid'
    schema = load_schema('encoded:schemas/organoid.json')
    embedded = Culture.embedded + []


@collection(
    name='tissues',
    unique_key='accession',
    properties={
        'title': 'Tissues',
        'description': 'Listing of Tissues',
    })
class Tissue(Biosample):
    item_type = 'tissue'
    schema = load_schema('encoded:schemas/tissue.json')
    embedded = Biosample.embedded + []
