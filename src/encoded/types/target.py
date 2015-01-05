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
    name='targets',
    unique_key='target:name',
    properties={
        'title': 'Targets',
        'description': 'Listing of ENCODE3 targets',
    })
class Target(Item):
    item_type = 'target'
    schema = load_schema('target.json')
    namespace_from_path = {
        'organism_name': 'organism.name',
        'scientific_name': 'organism.scientific_name',
    }
    template = {
        'name': {'$value': '{label}-{organism_name}', '$templated': True},
        'title': {'$value': '{label} ({scientific_name})', '$templated': True},
    }
    embedded = ['organism']
    template_keys = [
        {'name': '{item_type}:name', 'value': '{label}-{organism_name}', '$templated': True},
    ]

    @property
    def __name__(self):
        properties = self.upgrade_properties(finalize=False)
        root = find_root(self)
        organism = root.get_by_uuid(properties['organism'])
        organism_properties = organism.upgrade_properties(finalize=False)
        return u'{label}-{organism_name}'.format(
            organism_name=organism_properties['name'], **properties)

    def __resource_url__(self, request, info):
        request._linked_uuids.add(str(self.uuid))
        # Record organism uuid in linked_uuids so linking objects record
        # the rename dependency.
        properties = self.upgrade_properties(finalize=False)
        request._linked_uuids.add(str(properties['organism']))
        return None
