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
        'host_organism',
        'targets',
        'targets.genes',
        'targets.organism'
    ]
    audit_inherit = [
        'host_organism',
        'targets',
        'targets.organism'
    ]
    set_status_up = [
        'targets',
        'host_organism',
    ]
    set_status_down = []

    def unique_keys(self, properties):
        keys = super(AntibodyLot, self).unique_keys(properties)
        source = properties['source']
        product_id = properties['product_id']
        lot_ids = [properties['lot_id']] + properties.get('lot_id_alias', [])
        values = (u'{}/{}/{}'.format(source, product_id, lot_id)
                  for lot_id in lot_ids)
        keys.setdefault('antibody_lot:source_product_lot', []).extend(values)
        return keys

    @calculated_property(schema={
        "title": "Title",
        "type": "string",
    })
    def title(self, accession):
        return accession
