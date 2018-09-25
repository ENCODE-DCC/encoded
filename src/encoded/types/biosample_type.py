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
            properties['classification'],
            '_'.join(properties['term_ids'])
        ).replace(' ', '_').replace(':', '_')

    @property
    def __name__(self):
        return self.name()

    @calculated_property(condition='term_ids', schema={
        "title": "Organ slims",
        "type": "array",
        "items": {
            "type": "string",
        },
    })
    def organ_slims(self, registry, term_ids):
        slims = set()
        for term_id in term_ids:
            if term_id in registry['ontology']:
                slims.update(registry['ontology'][term_id]['organs'])
        return list(slims)

    @calculated_property(condition='biosample_term_id', schema={
        "title": "Cell slims",
        "type": "array",
        "items": {
            "type": "string",
        },
    })
    def cell_slims(self, registry, term_ids):
        slims = set()
        for term_id in term_ids:
            if term_id in registry['ontology']:
                slims.update(registry['ontology'][term_id]['cells'])
        return list(slims)

    @calculated_property(condition='term_ids', schema={
        "title": "Developmental slims",
        "type": "array",
        "items": {
            "type": "string",
        },
    })
    def developmental_slims(self, registry, term_ids):
        slims = set()
        for term_id in term_ids:
            if term_id in registry['ontology']:
                slims.update(registry['ontology'][term_id]['developmental'])
        return list(slims)

    @calculated_property(condition='biosample_term_id', schema={
        "title": "System slims",
        "type": "array",
        "items": {
            "type": "string",
        },
    })
    def system_slims(self, registry, term_ids):
        slims = set()
        for term_id in term_ids:
            if term_id in registry['ontology']:
                slims.update(registry['ontology'][term_id]['systems'])
        return list(slims)

    @calculated_property(condition='term_ids', schema={
        "title": "Synonyms for biosample type",
        "type": "array",
        "items": {
            "type": "string",
        },
    })
    def synonyms(self, registry, term_ids):
        syns = set()
        for term_id in term_ids:
            if term_id in registry['ontology']:
                syns.update(registry['ontology'][term_id]['synonyms'])
        return list(syns)
