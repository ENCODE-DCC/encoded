from snovault import (
    calculated_property,
    collection,
    load_schema,
)
from .base import (
    SharedItem,
)
from pyramid.traversal import (
    find_root,
)


@collection(
    name='targets',
    unique_key='target:name',
    properties={
        'title': 'Targets',
        'description': 'Listing of ENCODE3 targets',
    })
class Target(SharedItem):
    item_type = 'target'
    schema = load_schema('encoded:schemas/target.json')
    embedded = ['organism', 'genes']

    def unique_keys(self, properties):
        keys = super(Target, self).unique_keys(properties)
        keys.setdefault('target:name', []).append(self._name(properties))
        return keys

    @calculated_property(schema={
        "title": "Organism",
        "description": "Organism bearing the target.",
        "comment": "Calculated from either target_organism or genes",
        "type": "string",
        "linkTo": "Organism"
    })
    def organism(self, properties=None):
        if properties is None:
            properties = self.upgrade_properties()
        if 'target_organism' in properties:
            return properties['target_organism']
        else:
            root = find_root(self)
            organism_uuids = set(
                root.get_by_uuid(gene).upgrade_properties()['organism']
                for gene in properties['genes']
            )
            return organism_uuids.pop()

    @calculated_property(schema={
        "title": "Name",
        "type": "string",
    })
    def name(self):
        return self.__name__

    @calculated_property(schema={
        "title": "Title",
        "type": "string",
    })
    def title(self, request, label):
        organism = self.organism()
        organism_props = request.embed(organism, '@@object')
        return u'{} ({})'.format(label, organism_props['scientific_name'])

    @property
    def __name__(self):
        properties = self.upgrade_properties()
        return self._name(properties)

    def _name(self, properties):
        root = find_root(self)
        organism = root.get_by_uuid(self.organism(properties))
        organism_props = organism.upgrade_properties()
        return u'{}-{}'.format(properties['label'], organism_props['name'])

    def __resource_url__(self, request, info):
        request._linked_uuids.add(str(self.uuid))
        # Record organism uuid in linked_uuids so linking objects record
        # the rename dependency.
        request._linked_uuids.add(str(self.organism()))
        return None
