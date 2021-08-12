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
    CalculatedBiosampleClassification,
    CalculatedBiosampleSummary,
    CalculatedTreatmentSummary,
)


@collection(
    name='suspensions',
    unique_key='accession',
    properties={
        'title': 'Suspensions',
        'description': 'Listing of Suspensions',
    })
class Suspension(Item, 
                CalculatedDonors,
                CalculatedBiosampleOntologies,
                CalculatedBiosampleClassification,
                CalculatedBiosampleSummary,
                CalculatedTreatmentSummary):
    item_type = 'suspension'
    schema = load_schema('encoded:schemas/suspension.json')
    name_key = 'accession'
    embedded = [
        'biosample_ontologies',
        'donors',
        'donors.organism',
        'enriched_cell_types',
        'donors.ethnicity',
        'donors.diseases',
        'donors.development_ontology',
        'feature_antibodies',
        'feature_antibodies.target'
    ]
