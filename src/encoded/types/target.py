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
        namespace_from_path = {
            'organism_name': 'organism.name',
            'scientific_name': 'organism.scientific_name',
        }
        template = {
            'name': {'$value': '{label}-{organism_name}', '$templated': True},
            'title': {'$value': '{label} ({scientific_name})', '$templated': True},
        }
        embedded = ['organism']
        keys = ALIAS_KEYS + [
            {'name': '{item_type}:name', 'value': '{label}-{organism_name}', '$templated': True},
        ]

        @property
        def __name__(self):
            properties = self.upgrade_properties(finalize=False)
            root = find_root(self)
            organism = root.get_by_uuid(self.properties['organism'])
            organism_properties = organism.upgrade_properties(finalize=False)
            return u'{label}-{organism_name}'.format(
                organism_name=organism_properties['name'], **properties)
