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
    embedded = [
        'biosample_ontology',
        'donors',
        'donors.diseases',
        'donors.ethnicity'
    ]
