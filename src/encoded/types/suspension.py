from snovault import (
    calculated_property,
    collection,
    load_schema,
)
from .base import (
    Item,
)
from .shared_calculated_properties import (
    CalculatedDonors,
)


@collection(
    name='suspensions',
    unique_key='accession',
    properties={
        'title': 'Suspensions',
        'description': 'Listing of Suspensions',
    })
class Suspension(Item, CalculatedDonors):
    item_type = 'suspension'
    schema = load_schema('encoded:schemas/suspension.json')
    embedded = []


    @calculated_property(condition='derived_from', define=True, schema={
        "title": "Biosample ontology",
        "description": "An embedded property for linking to biosample type which describes the ontology of the samples the suspension derived from.",
        "comment": "Do not submit. This is a calculated property",
        "type": "array",
        "items": {
            "type": "string",
            "linkTo": "OntologyTerm"
        },
    })
    def biosample_ontology(self, request, derived_from):
        onts = set()
        for bs in derived_from:
            bs_obj = request.embed(bs, '@@object')
            if isinstance(bs_obj.get('biosample_ontology'), list):
                onts.update(bs_obj.get('biosample_ontology'))
            else:
                onts.add(bs_obj.get('biosample_ontology'))
        return sorted(onts)
