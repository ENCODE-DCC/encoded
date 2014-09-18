from ..schema_utils import (
    load_schema,
)
from ..contentbase import (
    location,
)
from .base import (
    ACCESSION_KEYS,
    ALIAS_KEYS,
    Collection,
)
from pyramid.traversal import (
    find_root,
)


@location('biosamples')
class Biosample(Collection):
    item_type = 'biosample'
    schema = load_schema('biosample.json')
    properties = {
        'title': 'Biosamples',
        'description': 'Biosamples used in the ENCODE project',
    }

    class Item(Collection.Item):
        template = {
            'organ_slims': [
                {'$value': '{slim}', '$repeat': 'slim organ_slims', '$templated': True}
            ],
            'system_slims': [
                {'$value': '{slim}', '$repeat': 'slim system_slims', '$templated': True}
            ],
            'developmental_slims': [
                {'$value': '{slim}', '$repeat': 'slim developmental_slims', '$templated': True}
            ],
            'synonyms': [
                {'$value': '{synonym}', '$repeat': 'synonym synonyms', '$templated': True}
            ],
            'sex': {'$value': '{sex}', '$templated': True, '$condition': 'sex'},
            'age': {'$value': '{age}', '$templated': True, '$condition': 'age'},
            'age_units': {'$value': '{age_units}', '$templated': True, '$condition': 'age_units'},
            'health_status': {'$value': '{health_status}', '$templated': True, '$condition': 'health_status'},
            'life_stage': {'$value': '{life_stage}', '$templated': True, '$condition': 'life_stage'},
            'synchronization': {'$value': '{synchronization}', '$templated': True, '$condition': 'synchronization'},
            'model_organism_donor_constructs': [
                {'$value': lambda model_organism_donor_construct: model_organism_donor_construct, '$repeat': 'model_organism_donor_construct model_organism_donor_constructs', '$templated': True}
            ]
        }
        embedded = set([
            'donor',
            'donor.organism',
            'donor.characterizations',
            'donor.characterizations.award',
            'donor.characterizations.lab',
            'donor.characterizations.submitted_by',
            'model_organism_donor_constructs',
            'model_organism_donor_constructs.target',
            'model_organism_donor_constructs.documents',
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
        ])
        name_key = 'accession'

        keys = ACCESSION_KEYS + ALIAS_KEYS
        rev = {
            'characterizations': ('biosample_characterization', 'characterizes'),
        }

        def template_namespace(self, properties, request=None):
            ns = Collection.Item.template_namespace(self, properties, request)
            if request is None:
                return ns
            terms = request.registry['ontology']
            if 'biosample_term_id' in ns:
                if ns['biosample_term_id'] in terms:
                    ns['organ_slims'] = terms[ns['biosample_term_id']]['organs']
                    ns['system_slims'] = terms[ns['biosample_term_id']]['systems']
                    ns['developmental_slims'] = terms[ns['biosample_term_id']]['developmental']
                    ns['synonyms'] = terms[ns['biosample_term_id']]['synonyms']
                else:
                    ns['organ_slims'] = ns['system_slims'] = ns['developmental_slims'] = ns['synonyms'] = []
            else:
                ns['organ_slims'] = ns['system_slims'] = ns['developmental_slims'] = ns['synonyms'] = []

            fly_organisms = [
                "/organisms/dmelanogaster/",
                "/organisms/dananassae/",
                "/organisms/dmojavensis/",
                "/organisms/dpseudoobscura/",
                "/organisms/dsimulans/",
                "/organisms/dvirilis/",
                "/organisms/dyakuba/"
            ]

            worm_organisms = [
                "/organisms/celegans/",
                "/organisms/cbrenneri/",
                "/organisms/cbriggsae/",
                "/organisms/cremanei/",
                "/organisms/cjaponica/"
            ]

            human_donor_properties = [
                "sex",
                "age",
                "age_units",
                "health_status",
                "life_stage",
                "synchronization"
            ]
            mouse_biosample_properties = {
                "model_organism_sex": "sex",
                "model_organism_age": "age",
                "model_organism_age_units": "age_units",
                "model_organism_health_status": "health_status",
                "mouse_life_stage": "life_stage",
                "mouse_synchronization_stage": "synchronization"
            }
            fly_biosample_properties = {
                "model_organism_sex": "sex",
                "model_organism_age": "age",
                "model_organism_age_units": "age_units",
                "model_organism_health_status": "health_status",
                "fly_life_stage": "life_stage",
                "fly_synchronization_stage": "synchronization"
            }
            worm_biosample_properties = {
                "model_organism_sex": "sex",
                "model_organism_age": "age",
                "model_organism_age_units": "age_units",
                "model_organism_health_status": "health_status",
                "worm_life_stage": "life_stage",
                "worm_synchronization_stage": "synchronization"
            }

            model_organism_donor_constructs = []

            if properties['organism'] == '/organisms/human/' and 'donor' in ns:
                root = find_root(self)
                donor = root.get_by_uuid(self.properties['donor'])
                for value in human_donor_properties:
                    if value in donor.properties:
                        ns[value] = donor.properties[value]
            elif properties['organism'] == "/organisms/mouse/":
                for key, value in mouse_biosample_properties.items():
                    if key in ns:
                        ns[value] = ns[key]
            elif properties['organism'] in fly_organisms:
                root = find_root(self)
                donor = root.get_by_uuid(self.properties['donor'])
                for key, value in fly_biosample_properties.items():
                    if key in ns:
                        ns[value] = ns[key]
                if donor.properties['constructs']:
                    model_organism_donor_constructs = donor.properties['constructs']
            elif properties['organism'] in worm_organisms:
                root = find_root(self)
                donor = root.get_by_uuid(self.properties['donor'])
                for key, value in worm_biosample_properties.items():
                    if key in ns:
                        ns[value] = ns[key]
                if donor.properties['constructs']:
                    model_organism_donor_constructs = donor.properties['constructs']
            else:
                pass

            ns['model_organism_donor_constructs'] = model_organism_donor_constructs
            return ns
