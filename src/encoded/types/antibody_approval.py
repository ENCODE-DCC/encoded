from ..schema_utils import (
    load_schema,
)
from ..contentbase import (
    location,
)
from .base import (
    Collection,
)
from pyramid.traversal import (
    find_root,
)


@location('antibody-approvals')
class AntibodyApproval(Collection):
    schema = load_schema('antibody_approval.json')
    item_type = 'antibody_approval'
    properties = {
        'title': 'Antibody Approvals',
        'description': 'Listing of characterization approvals for ENCODE antibodies',
    }

    class Item(Collection.Item):
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
        keys = [
            {'name': '{item_type}:lot_target', 'value': '{antibody}/{target}', '$templated': True}
        ]

        @property
        def __parent__(self):
            # Use /antibodies/{uuid} as url
            root = find_root(self.collection)
            return root.by_item_type['antibody_lot']

        def template_namespace(self, properties, request=None):
            ns = Collection.Item.template_namespace(self, properties, request)
            root = find_root(self)
            # self.properties as we need uuid here
            antibody = root.get_by_uuid(self.properties['antibody'])
            ns['accession'] = antibody.properties['accession']
            target = root.get_by_uuid(self.properties['target'])
            ns['label'] = target.properties['label']
            organism = root.get_by_uuid(target.properties['organism'])
            ns['scientific_name'] = organism.properties['scientific_name']
            return ns
