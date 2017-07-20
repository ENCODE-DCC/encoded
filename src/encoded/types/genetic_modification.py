from snovault import (
    calculated_property,
    collection,
    load_schema,
)

from .base import (
    Item,
    paths_filtered_by_status,
)


@collection(
    name='genetic-modifications',
    unique_key='accession',
    properties={
        'title': 'Genetic modifications',
        'description': 'Listing of genetic modifications',
    })
class GeneticModification(Item):
    item_type = 'genetic_modification'
    schema = load_schema('encoded:schemas/genetic_modification.json')
    name_key = 'accession'
    embedded = [
        'modified_location_by_target_id',
        'reagent_repository',
        'documents',
        'characterizations.documents'
    ]

    rev = {
        'biosamples_modified': ('Biosample', 'genetic_modifications'),
        'donors_modified': ('Donor', 'genetic_modifications'),
        'characterizations': ('GeneticModificationCharacterization', 'characterizes')
    }

    @calculated_property(schema={
        "title": "Biosamples genetically altered using this modification",
        "type": "array",
        "items": {
            "type": ['string', 'object'],
            "linkFrom": "Biosample.genetic_modifications",
        },
    })
    def biosamples_modified(self, request, biosamples_modified):
        return paths_filtered_by_status(request, biosamples_modified)

    @calculated_property(schema={
        "title": "Donors genetically altered using this modification",
        "type": "array",
        "items": {
            "type": ['string', 'object'],
            "linkFrom": "Donor.genetic_modifications",
        },
    })
    def donors_modified(self, request, donors_modified):
        return paths_filtered_by_status(request, donors_modified)

    @calculated_property(schema={
        "title": "Characterizations",
        "type": "array",
        "items": {
            "type": ['string', 'object'],
            "linkFrom": "GeneticModificationCharacterization.characterizes",
        },
    })
    def characterizations(self, request, characterizations):
        return paths_filtered_by_status(request, characterizations)
