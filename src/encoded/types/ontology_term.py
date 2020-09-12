from snovault import (
    calculated_property,
    collection,
    load_schema,
)
from .base import (
    SharedItem,
)


@collection(
    name='ontology-terms',
    unique_key='ontology_term:name',
    properties={
        'title': 'Ontology term',
        'description': 'Ontology terms in the Lattice metadata.',
    })
class OntologyTerm(SharedItem):
    item_type = 'ontology_term'
    schema = load_schema('encoded:schemas/ontology_term.json')
    embedded = ['references']

    def unique_keys(self, properties):
        keys = super(OntologyTerm, self).unique_keys(properties)
        keys.setdefault('ontology_term:name', []).append(self.name(properties))
        return keys

    @calculated_property(schema={
        "title": "Name",
        "type": "string",
    })
    def name(self, properties=None):
        if properties is None:
            properties = self.upgrade_properties()
        return properties['term_id'].replace(':', '_')

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
        "title": "Disease slims",
        "type": "array",
        "items": {
            "type": "string",
        },
    })
    def disease_slims(self, registry, term_id):
        return self._get_ontology_slims(registry, term_id, 'disease_categories')

    @calculated_property(condition='term_id', schema={
        "title": "Synonyms",
        "type": "array",
        "items": {
            "type": "string",
        },
    })
    def synonyms(self, registry, term_id):
        return self._get_ontology_slims(registry, term_id, 'synonyms')

    @calculated_property(condition='term_id', schema={
        "title": "Ontology DB",
        "type": "string",
    })
    def ontology_database(self, registry, term_id):
        return term_id.split(':')[0]
