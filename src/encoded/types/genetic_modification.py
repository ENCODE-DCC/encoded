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
        'modified_site_by_target_id',
        'modified_site_by_target_id.genes',
        'treatments'
    ]
    set_status_up = [
        'reagents.source',
        'modified_site_by_target_id',
        'modified_site_by_target_id.genes',
        'treatments',
        'documents',
    ]
    set_status_down = []

    rev = {
        'biosamples_modified': ('Biosample', 'genetic_modifications'),
        'donors_modified': ('Donor', 'genetic_modifications')
    }

    @calculated_property(schema={
        "title": "Biosamples modified",
        "description": "Biosamples genetically altered using this modification",
        "type": "array",
        "items": {
            "type": ['string', 'object'],
            "linkFrom": "Biosample.genetic_modifications",
        },
        "notSubmittable": True,
    })
    def biosamples_modified(self, request, biosamples_modified):
        return paths_filtered_by_status(request, biosamples_modified)

    @calculated_property(schema={
        "title": "Donors modified",
        "description": "Donors genetically altered using this modification",
        "type": "array",
        "items": {
            "type": ['string', 'object'],
            "linkFrom": "Donor.genetic_modifications",
        },
        "notSubmittable": True,
    })
    def donors_modified(self, request, donors_modified):
        return paths_filtered_by_status(request, donors_modified)

    @calculated_property(schema={
        "title": "Perturbation",
        "description": "A flag to indicate whether the genetic modification caused a genetic perturbation. Only genetic modifications that are insertions for the purpose of tagging are considered unperturbed.",
        "type": "boolean",
        "notSubmittable": True
    })
    def perturbation(self, category, purpose):
        if (
            (category == 'insertion' and purpose == 'tagging')
            or purpose == 'non-specific target control'
        ):
            return False
        else:
            return True