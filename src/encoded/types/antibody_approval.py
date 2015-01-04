from ..schema_utils import (
    load_schema,
)
from ..contentbase import (
    location,
)
from .base import (
    Item,
)
from pyramid.traversal import (
    find_root,
)


@location(
    name='antibody-approvals',
    properties={
        'title': 'Antibody Approvals',
        'description': 'Listing of characterization approvals for ENCODE antibodies',
    })
class AntibodyApproval(Item):
    schema = load_schema('antibody_approval.json')
    item_type = 'antibody_approval'
    namespace_from_path = {
        'accession': 'antibody.accession',
        'label': 'target.label',
        'scientific_name': 'target.organism.scientific_name'
    }
    template = {
        # trigger redirect to antibody_lot
        '@id': {'$value': '{antibody}', '$templated': True},
        'title': {'$value': '{accession} in {scientific_name} {label}', '$templated': True},
    }
    embedded = [
        'antibody.host_organism',
        'antibody.source',
        'characterizations.award',
        'characterizations.lab',
        'characterizations.submitted_by',
        'characterizations.target.organism',
        'target.organism',
    ]
    template_keys = [
        {'name': '{item_type}:lot_target', 'value': '{antibody}/{target}', '$templated': True}
    ]

    @property
    def __parent__(self):
        # Use /antibodies/{uuid} as url
        root = find_root(self.collection)
        return root.by_item_type['antibody_lot']
