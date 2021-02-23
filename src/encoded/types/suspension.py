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
    CalculatedBiosampleOntologies,
)


@collection(
    name='suspensions',
    unique_key='accession',
    properties={
        'title': 'Suspensions',
        'description': 'Listing of Suspensions',
    })
class Suspension(Item, CalculatedDonors, CalculatedBiosampleOntologies):
    item_type = 'suspension'
    schema = load_schema('encoded:schemas/suspension.json')
    embedded = [
        'biosample_ontologies',
        'donors',
        'donors.organism'
    ]
