from snovault import (
    calculated_property,
    collection,
    load_schema,
)
from snovault.util import Path
from .base import (
    SharedItem,
)


@collection(
    name='biosample-types',
    unique_key='biosample_type:name',
    properties={
        'title': 'Biosample type',
        'description': 'General types of biosample used in the ENCODE project',
    })
class BiosampleType(SharedItem):
    item_type = 'biosample_type'
    schema = load_schema('encoded:schemas/biosample_type.json')
    embedded = []
    embedded_with_frame = [
        Path('references', exclude=['datasets', 'publication_data']
    ]

    def unique_keys(self, properties):
        keys = super(BiosampleType, self).unique_keys(properties)
        keys.setdefault('biosample_type:name', []).append(self.name(properties))
        return keys

    @calculated_property(schema={
        "title": "Name",
        "type": "string",
    })
    def name(self, properties=None):
        if properties is None:
            properties = self.upgrade_properties()
        return u'{}_{}'.format(
            properties['classification'], properties['term_id']
        ).replace(' ', '_').replace(':', '_')

    @property
    def __name__(self):
        return self.name()

    @staticmethod
    def _get_ontology_slims(registry, term_id, slim_key):
        if term_id not in registry['ontology']:
            return []
        return list(set(
            slim for slim in registry['ontology'][term_id][slim_key]
        ))

    @calculated_property(condition='term_id', schema={
        "title": "Organ",
        "type": "array",
        "items": {
            "type": "string",
        },
    })
    def organ_slims(self, registry, term_id):
        return self._get_ontology_slims(registry, term_id, 'organs')

    @calculated_property(condition='term_id', schema={
        "title": "Cell",
        "type": "array",
        "items": {
            "type": "string",
        },
    })
    def cell_slims(self, registry, term_id):
        return self._get_ontology_slims(registry, term_id, 'cells')

    @calculated_property(condition='term_id', schema={
        "title": "Developmental slims",
        "type": "array",
        "items": {
            "type": "string",
        },
    })
    def developmental_slims(self, registry, term_id):
        return self._get_ontology_slims(registry, term_id, 'developmental')

    @calculated_property(condition='term_id', schema={
        "title": "System slims",
        "type": "array",
        "items": {
            "type": "string",
        },
    })
    def system_slims(self, registry, term_id):
        return self._get_ontology_slims(registry, term_id, 'systems')

    @calculated_property(condition='term_id', schema={
        "title": "Synonyms",
        "type": "array",
        "items": {
            "type": "string",
        },
    })
    def synonyms(self, registry, term_id):
        return self._get_ontology_slims(registry, term_id, 'synonyms')
