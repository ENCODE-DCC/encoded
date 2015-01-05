from ..schema_utils import (
    load_schema,
)
from ..contentbase import (
    location,
)
from .base import (
    Item,
    paths_filtered_by_status,
)


def calculate_age_display(
        request, donor=None, model_organism_age=None, model_organism_age_units=None):
    if donor is not None:
        donor = request.embed(donor, '@@object')
        if 'age' in donor and 'age_units' in donor:
            if donor['age'] == 'unknown':
                return ''
            return '{age} {age_units}'.format(**donor)
    if model_organism_age is not None and model_organism_age_units is not None:
        return '{age} {age_units}'.format(
            age=model_organism_age,
            age_units=model_organism_age_units,
        )
    return ''


@location(
    name='biosamples',
    unique_key='accession',
    properties={
        'title': 'Biosamples',
        'description': 'Biosamples used in the ENCODE project',
    })
class Biosample(Item):
    item_type = 'biosample'
    schema = load_schema('biosample.json')
    name_key = 'accession'
    rev = {
        'characterizations': ('biosample_characterization', 'characterizes'),
    }
    namespace_from_path = {
        'model_organism_donor_constructs': 'donor.constructs',
        # The lists here are search paths
        'sex': ['model_organism_sex', 'donor.sex'],
        'age': ['model_organism_age', 'donor.age'],
        'age_units': ['model_organism_age_units', 'donor.age_units'],
        'health_status': ['model_organism_health_status', 'donor.health_status'],
        'life_stage': [
            'mouse_life_stage',
            'fly_life_stage',
            'worm_life_stage',
            'donor.life_stage',
        ],
        'synchronization': [
            'mouse_synchronization_stage',  # XXX mouse_synchronization_stage does not exist
            'fly_synchronization_stage',
            'worm_synchronization_stage',
            'donor.synchronization',
        ],
    }
    template = {
        'organ_slims': {
            '$value': (
                lambda registry, biosample_term_id:
                    registry['ontology'][biosample_term_id]['organs']
                    if biosample_term_id in registry['ontology'] else []
            ),
            '$condition': 'biosample_term_id',
        },
        'system_slims': {
            '$value': (
                lambda registry, biosample_term_id:
                    registry['ontology'][biosample_term_id]['systems']
                    if biosample_term_id in registry['ontology'] else []
            ),
            '$condition': 'biosample_term_id',
        },
        'developmental_slims': {
            '$value': (
                lambda registry, biosample_term_id:
                    registry['ontology'][biosample_term_id]['developmental']
                    if biosample_term_id in registry['ontology'] else []
            ),
            '$condition': 'biosample_term_id',
        },
        'synonyms': {
            '$value': (
                lambda registry, biosample_term_id:
                    registry['ontology'][biosample_term_id]['synonyms']
                    if biosample_term_id in registry['ontology'] else []
            ),
            '$condition': 'biosample_term_id',
        },
        'sex': {'$value': '{sex}', '$condition': 'sex'},
        'age': {'$value': '{age}', '$condition': 'age'},
        'age_units': {
            '$value': '{age_units}',
            '$condition': 'age_units',
        },
        'health_status': {
            '$value': '{health_status}',
            '$condition': 'health_status',
        },
        'life_stage': {
            '$value': '{life_stage}',
            '$condition': 'life_stage',
        },
        'synchronization': {
            '$value': '{synchronization}',
            '$condition': 'synchronization',
        },
        'model_organism_donor_constructs': {
            '$value': lambda model_organism_donor_constructs: model_organism_donor_constructs,
            '$condition': 'model_organism_donor_constructs',
        },
        'characterizations': (
            lambda request, characterizations: paths_filtered_by_status(request, characterizations)
        ),
        'age_display': calculate_age_display,
    }
    embedded = [
        'donor',
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
        'rnais.target.organism',
        'rnais.source',
        'rnais.documents.submitted_by',
        'rnais.documents.award',
        'rnais.documents.lab',
        'organism',
    ]
