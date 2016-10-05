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
    properties={
        'title': 'Genetic modifications',
        'description': 'Listing of genetic modifications',
    })
class GeneticModification(Item):
    item_type = 'genetic_modification'
    schema = load_schema('encoded:schemas/genetic_modification.json')
    embedded = [
        'award',
        'award.pi',
        'award.pi.lab',
        'lab',
        'source',
        'submitted_by',
        'target',
        'documents',
        'documents.award',
        'documents.lab',
        'documents.submitted_by',
        'characterizations.documents',
        'characterizations.documents.award',
        'characterizations.documents.lab',
        'characterizations.documents.submitted_by',
        'modification_techniques',
        'modification_techniques.award.pi.lab',
        'modification_techniques.lab',
        'modification_techniques.source',
        'modification_techniques.documents',
        'modification_techniques.documents.award',
        'modification_techniques.documents.lab',
        'modification_techniques.documents.submitted_by',
        'biosamples_modified.documents',
        'donors_modified.documents',
        'treatments'
    ]

    rev = {
        'biosamples_modified': ('Biosample', 'genetic_modifications'),
        'mouse_donors_modified': ('MouseDonor', 'genetic_modifications'),
        'fly_donors_modified': ('FlyDonor', 'genetic_modifications'),
        'worm_donors_modified': ('WormDonor', 'genetic_modifications'),
        'human_donors_modified': ('HumanDonor', 'genetic_modifications'),
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
    def donors_modified(self, request, fly_donors_modified,
                        worm_donors_modified, human_donors_modified,
                        mouse_donors_modified):
        returnList = paths_filtered_by_status(request, fly_donors_modified)
        returnList.extend(paths_filtered_by_status(request, worm_donors_modified))
        returnList.extend(paths_filtered_by_status(request, human_donors_modified))
        returnList.extend(paths_filtered_by_status(request, mouse_donors_modified))
        return returnList

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
