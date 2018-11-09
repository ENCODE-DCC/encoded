from snovault import (
    calculated_property,
    collection,
    load_schema,
)
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
    embedded = ['references']

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
            properties['classification'], sorted(properties['term_ids'])[0]
        ).replace(' ', '_').replace(':', '_')

    @property
    def __name__(self):
        return self.name()

    @staticmethod
    def _get_ontology_slims(registry, term_ids, slim_key):
        slims = set()
        for term_id in term_ids:
            if term_id in registry['ontology']:
                slims.update(registry['ontology'][term_id][slim_key])
        return list(slims)

    @calculated_property(condition='term_ids', schema={
        "title": "Organ slims",
        "type": "array",
        "items": {
            "type": "string",
        },
    })
    def organ_slims(self, registry, term_ids):
        return self._get_ontology_slims(registry, term_ids, 'organs')

    @calculated_property(condition='term_ids', schema={
        "title": "Cell slims",
        "type": "array",
        "items": {
            "type": "string",
        },
    })
    def cell_slims(self, registry, term_ids):
        return self._get_ontology_slims(registry, term_ids, 'cells')

    @calculated_property(condition='term_ids', schema={
        "title": "Developmental slims",
        "type": "array",
        "items": {
            "type": "string",
        },
    })
    def developmental_slims(self, registry, term_ids):
        return self._get_ontology_slims(registry, term_ids, 'developmental')

    @calculated_property(condition='term_ids', schema={
        "title": "System slims",
        "type": "array",
        "items": {
            "type": "string",
        },
    })
    def system_slims(self, registry, term_ids):
        return self._get_ontology_slims(registry, term_ids, 'systems')

    @calculated_property(condition='term_ids', schema={
        "title": "Synonyms for biosample type",
        "type": "array",
        "items": {
            "type": "string",
        },
    })
    def synonyms(self, registry, term_ids):
        return self._get_ontology_slims(registry, term_ids, 'synonyms')
