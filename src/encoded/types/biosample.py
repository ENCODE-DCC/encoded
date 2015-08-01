from contentbase import (
    calculated_property,
    collection,
    load_schema,
)
from .base import (
    Item,
    paths_filtered_by_status,
)


@collection(
    name='biosamples',
    unique_key='accession',
    properties={
        'title': 'Biosamples',
        'description': 'Biosamples used in the ENCODE project',
    })
class Biosample(Item):
    item_type = 'biosample'
    schema = load_schema('encoded:schemas/biosample.json')
    name_key = 'accession'
    rev = {
        'characterizations': ('biosample_characterization', 'characterizes'),
    }
    embedded = [
        'donor',
        'donor.mutated_gene',
        'donor.organism',
        'donor.characterizations',
        'donor.characterizations.award',
        'donor.characterizations.lab',
        'donor.characterizations.submitted_by',
        'model_organism_donor_constructs',
        'model_organism_donor_constructs.submitted_by',
        'model_organism_donor_constructs.target',
        'model_organism_donor_constructs.documents',
        'model_organism_donor_constructs.documents.award',
        'model_organism_donor_constructs.documents.lab',
        'model_organism_donor_constructs.documents.submitted_by',
        'submitted_by',
        'lab',
        'award',
        'award.pi.lab',
        'source',
        'treatments.protocols.submitted_by',
        'treatments.protocols.lab',
        'treatments.protocols.award',
        'constructs.documents.submitted_by',
        'constructs.documents.award',
        'constructs.documents.lab',
        'constructs.target',
        'protocol_documents.lab',
        'protocol_documents.award',
        'protocol_documents.submitted_by',
        'derived_from',
        'part_of',
        'pooled_from',
        'characterizations.submitted_by',
        'characterizations.award',
        'characterizations.lab',
        'rnais',
        'rnais.target.organism',
        'rnais.source',
        'rnais.documents.submitted_by',
        'rnais.documents.award',
        'rnais.documents.lab',
        'organism',
        'references',
    ]

    @calculated_property(condition='biosample_term_id', schema={
        "title": "Organ slims",
        "type": "array",
        "items": {
            "type": "string",
        },
    })
    def organ_slims(self, registry, biosample_term_id):
        if biosample_term_id in registry['ontology']:
            return registry['ontology'][biosample_term_id]['organs']
        return []

    @calculated_property(condition='biosample_term_id', schema={
        "title": "System slims",
        "type": "array",
        "items": {
            "type": "string",
        },
    })
    def system_slims(self, registry, biosample_term_id):
        if biosample_term_id in registry['ontology']:
            return registry['ontology'][biosample_term_id]['systems']
        return []

    @calculated_property(condition='biosample_term_id', schema={
        "title": "Developmental slims",
        "type": "array",
        "items": {
            "type": "string",
        },
    })
    def developmental_slims(self, registry, biosample_term_id):
        if biosample_term_id in registry['ontology']:
            return registry['ontology'][biosample_term_id]['developmental']
        return []

    @calculated_property(condition='biosample_term_id', schema={
        "title": "Ontology synonyms",
        "type": "array",
        "items": {
            "type": "string",
        },
    })
    def synonyms(self, registry, biosample_term_id):
        if biosample_term_id in registry['ontology']:
            return registry['ontology'][biosample_term_id]['synonyms']
        return []

    @calculated_property(schema={
        "title": "Sex",
        "type": "string",
    })
    def sex(self, request, donor=None, model_organism_sex=None):
        if model_organism_sex is not None:
            return model_organism_sex
        if donor is not None:
            return request.embed(donor, '@@object').get('sex')

    @calculated_property(schema={
        "title": "Age",
        "type": "string",
    })
    def age(self, request, donor=None, model_organism_age=None):
        if model_organism_age is not None:
            return model_organism_age
        if donor is not None:
            return request.embed(donor, '@@object').get('age')

    @calculated_property(schema={
        "title": "Age units",
        "type": "string",
    })
    def age_units(self, request, donor=None, model_organism_age_units=None):
        if model_organism_age_units is not None:
            return model_organism_age_units
        if donor is not None:
            return request.embed(donor, '@@object').get('age_units')

    @calculated_property(schema={
        "title": "Health status",
        "type": "string",
    })
    def health_status(self, request, donor=None, model_organism_health_status=None):
        if model_organism_health_status is not None:
            return model_organism_health_status
        if donor is not None:
            return request.embed(donor, '@@object').get('health_status')

    @calculated_property(schema={
        "title": "Life stage",
        "type": "string",
    })
    def life_stage(self, request, donor=None, mouse_life_stage=None, fly_life_stage=None,
                   worm_life_stage=None):
        if mouse_life_stage is not None:
            return mouse_life_stage
        if fly_life_stage is not None:
            return fly_life_stage
        if worm_life_stage is not None:
            return worm_life_stage
        if donor is not None:
            return request.embed(donor, '@@object').get('life_stage')

    @calculated_property(schema={
        "title": "Synchronization",
        "type": "string",
    })
    def synchronization(self, request, donor=None, mouse_synchronization_stage=None,
                        fly_synchronization_stage=None, worm_synchronization_stage=None):
        # XXX mouse_synchronization_stage does not exist
        if mouse_synchronization_stage is not None:
            return mouse_synchronization_stage
        if fly_synchronization_stage is not None:
            return fly_synchronization_stage
        if worm_synchronization_stage is not None:
            return worm_synchronization_stage
        if donor is not None:
            return request.embed(donor, '@@object').get('synchronization')

    @calculated_property(schema={
        "title": "DNA constructs",
        "description":
            "Expression or targeting vectors stably or transiently transfected "
            "(not RNAi) into a donor organism.",
        "type": "array",
        "items": {
            "title": "DNA Constructs",
            "description": "An expression or targeting vector stably or transiently transfected "
            "(not RNAi) into a donor organism.",
            "comment": "See contstruct.json for available identifiers.",
            "type": "string",
            "linkTo": "construct",
        },
    })
    def model_organism_donor_constructs(self, request, donor=None):
        if donor is not None:
            return request.embed(donor, '@@object').get('constructs')

    @calculated_property(schema={
        "title": "Characterizations",
        "type": "array",
        "items": {
            "type": ['string', 'object'],
            "linkFrom": "biosample_characterization.characterizes",
        },
    })
    def characterizations(self, request, characterizations):
        return paths_filtered_by_status(request, characterizations)

    @calculated_property(schema={
        "title": "Age",
        "type": "string",
    })
    def age_display(self, request, donor=None, model_organism_age=None,
                    model_organism_age_units=None):
        if donor is not None:
            donor = request.embed(donor, '@@object')
            if 'age' in donor and 'age_units' in donor:
                if donor['age'] == 'unknown':
                    return ''
                return u'{age} {age_units}'.format(**donor)
        if model_organism_age is not None and model_organism_age_units is not None:
            return u'{age} {age_units}'.format(
                age=model_organism_age,
                age_units=model_organism_age_units,
            )
        return None
