from contentbase import (
    calculated_property,
    collection,
    load_schema,
)
from .base import (
    Item,
)
from pyramid.traversal import (
    find_root,
)


@collection(
    name='antibody-approvals',
    properties={
        'title': 'Antibody Approvals',
        'description': 'Listing of characterization approvals for ENCODE antibodies',
    })
class AntibodyApproval(Item):
    schema = load_schema('encoded:schemas/antibody_approval.json')
    item_type = 'antibody_approval'

    def unique_keys(self, properties):
        keys = super(AntibodyApproval, self).unique_keys(properties)
        value = u'{antibody}/{target}'.format(**properties)
        keys.setdefault('antibody_approval:lot_target', []).append(value)
        return keys

    # trigger redirect to antibody_lot
    @calculated_property(name='@id', schema={
        "type": "string",
    })
    def jsonld_id(self, antibody):
        return antibody

    # Use /antibodies/{uuid} as url
    @property
    def __parent__(self):
        root = find_root(self.collection)
        return root.by_item_type['antibody_lot']
