from ..schema_utils import (
    load_schema,
)
from ..contentbase import (
    location,
)
from .base import (
    ALIAS_KEYS,
    Collection,
)
from pyramid.traversal import (
    find_root,
)


@location('targets')
class Target(Collection):
    item_type = 'target'
    schema = load_schema('target.json')
    properties = {
        'title': 'Targets',
        'description': 'Listing of ENCODE3 targets',
    }
    unique_key = 'target:name'

    class Item(Collection.Item):
        template = {
            'name': {'$value': '{label}-{organism_name}', '$templated': True},
            'title': {'$value': '{label} ({scientific_name})', '$templated': True},
        }
        embedded = set(['organism'])
        keys = ALIAS_KEYS + [
            {'name': '{item_type}:name', 'value': '{label}-{organism_name}', '$templated': True},
        ]

        def template_namespace(self, properties, request=None):
            ns = Collection.Item.template_namespace(self, properties, request)
            root = find_root(self)
            # self.properties as we need uuid here
            organism = root.get_by_uuid(self.properties['organism'])
            ns['organism_name'] = organism.properties['name']
            ns['scientific_name'] = organism.properties['scientific_name']
            return ns

        @property
        def __name__(self):
            properties = self.upgrade_properties(finalize=False)
            root = find_root(self)
            organism = root.get_by_uuid(self.properties['organism'])
            return u'{label}-{organism_name}'.format(
                organism_name=organism.properties['name'], **properties)
