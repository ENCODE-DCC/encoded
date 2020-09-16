from snovault import (
    calculated_property,
    collection,
    load_schema,
)
from .base import (
    SharedItem,
    paths_filtered_by_status,
)


@collection(
    name='antibodies',
    unique_key='accession',
    properties={
        'title': 'Antibody lot',
        'description': 'Listing of ENCODE antibodies',
    })
class AntibodyLot(SharedItem):
    item_type = 'antibody_lot'
    schema = load_schema('encoded:schemas/antibody_lot.json')
    name_key = 'accession'
    rev = {}
    embedded = [
        'host_organism'
    ]

    @calculated_property(schema={
        "title": "Title",
        "type": "string",
    })
    def title(self, accession):
        return accession
