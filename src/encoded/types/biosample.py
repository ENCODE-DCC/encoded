from snovault import (
    calculated_property,
    collection,
    load_schema,
)
from .base import (
    Item,
    paths_filtered_by_status,
)
from .shared_calculated_properties import (
    CalculatedBiosampleSlims,
    CalculatedBiosampleSynonyms
)
import re


@collection(
    name='biosamples',
    unique_key='accession',
    properties={
        'title': 'Biosamples',
        'description': 'Biosamples used in the ENCODE project',
    })
class Biosample(Item, CalculatedBiosampleSlims, CalculatedBiosampleSynonyms):
    item_type = 'biosample'
    schema = load_schema('encoded:schemas/biosample.json')
    name_key = 'accession'
    rev = {
        'characterizations': ('BiosampleCharacterization', 'characterizes'),
        'parent_of': ('Biosample', 'part_of'),
    }
    embedded = [
        'donor',
        'donor.mutated_gene',
        'donor.organism',
        'donor.characterizations',
        'donor.characterizations.award',
        'donor.characterizations.lab',
        'donor.characterizations.submitted_by',
        'donor.documents',
        'donor.documents.award',
        'donor.documents.lab',
        'donor.documents.submitted_by',
        'donor.references',
        'model_organism_donor_constructs',
        'model_organism_donor_constructs.submitted_by',
        'model_organism_donor_constructs.promoter_used',
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
        'treatments',
        'treatments.documents.submitted_by',
        'treatments.documents.lab',
        'treatments.documents.award',
        'constructs',
        'constructs.documents.submitted_by',
        'constructs.documents.award',
        'constructs.documents.lab',
        'constructs.target',
        'documents.lab',
        'documents.award',
        'documents.submitted_by',
        'originated_from',
        'part_of',
        'part_of.documents',
        'part_of.documents.award',
        'part_of.documents.lab',
        'part_of.documents.submitted_by',
        'part_of.characterizations.documents',
        'part_of.characterizations.documents.award',
        'part_of.characterizations.documents.lab',
        'part_of.characterizations.documents.submitted_by',
        'part_of.constructs.documents',
        'part_of.constructs.documents.award',
        'part_of.constructs.documents.lab',
        'part_of.constructs.documents.submitted_by',
        'part_of.rnais.documents.award',
        'part_of.rnais.documents.lab',
        'part_of.rnais.documents.submitted_by',
        'part_of.treatments.documents',
        'parent_of',
        'pooled_from',
        'characterizations.submitted_by',
        'characterizations.award',
        'characterizations.lab',
        'rnais',
        'rnais.target',
        'rnais.target.organism',
        'rnais.source',
        'rnais.documents.submitted_by',
        'rnais.documents.award',
        'rnais.documents.lab',
        'organism',
        'references',
        'genetic_modifications',
        'genetic_modifications.treatments'
    ]
    audit_inherit = [
        'donor',
        'donor.mutated_gene',
        'donor.organism',
        'donor.characterizations',
        'donor.donor_documents',
        'donor.references',
        'model_organism_donor_constructs',
        'model_organism_donor_constructs.target',
        'model_organism_donor_constructs.documents',
        'submitted_by',
        'lab',
        'award',
        'source',
        'treatments',
        'constructs',
        'constructs.target',
        'originated_from',
        'pooled_from',
        'rnais',
        'rnais.target',
        'rnais.target.organism',
        'rnais.source',
        'organism',
        'references',
        'genetic_modifications'
    ]

    @calculated_property(define=True,
                         schema={"title": "Sex",
                                 "type": "string"})
    def sex(self, request, donor=None, model_organism_sex=None, organism=None):
        humanFlag = False
        if organism is not None:
            organismObject = request.embed(organism, '@@object')
            if organismObject['scientific_name'] == 'Homo sapiens':
                humanFlag = True

        if humanFlag is True:
            if donor is not None:  # try to get the sex from the donor
                donorObject = request.embed(donor, '@@object')
                if 'sex' in donorObject:
                    return donorObject['sex']
                else:
                    return 'unknown'
            else:
                return 'unknown'
        else:
            if model_organism_sex is not None:
                return model_organism_sex
            else:
                return 'unknown'

    @calculated_property(define=True,
                         schema={"title": "Age",
                                 "type": "string"})
    def age(self, request, donor=None, model_organism_age=None, organism=None):
        humanFlag = False
        if organism is not None:
            organismObject = request.embed(organism, '@@object')
            if organismObject['scientific_name'] == 'Homo sapiens':
                humanFlag = True

        if humanFlag is True:
            if donor is not None:  # try to get the age from the donor
                donorObject = request.embed(donor, '@@object')
                if 'age' in donorObject:
                    return donorObject['age']
                else:
                    return 'unknown'
            else:
                return 'unknown'
        else:
            if model_organism_age is not None:
                return model_organism_age
            else:
                return 'unknown'

    @calculated_property(define=True,
                         schema={"title": "Age units",
                                 "type": "string"})
    def age_units(self, request, donor=None, model_organism_age_units=None, organism=None):
        humanFlag = False
        if organism is not None:
            organismObject = request.embed(organism, '@@object')
            if organismObject['scientific_name'] == 'Homo sapiens':
                humanFlag = True

        if humanFlag is True:
            if donor is not None:  # try to get the age_units from the donor
                donorObject = request.embed(donor, '@@object')
                if 'age_units' in donorObject:
                    return donorObject['age_units']
                else:
                    return None
            else:
                return None
        else:
            return model_organism_age_units

    @calculated_property(define=True,
                         schema={"title": "Health status",
                                 "type": "string"})
    def health_status(self, request, donor=None, model_organism_health_status=None, organism=None):
        humanFlag = False
        if organism is not None:
            organismObject = request.embed(organism, '@@object')
            if organismObject['scientific_name'] == 'Homo sapiens':
                humanFlag = True

        if humanFlag is True and donor is not None:
            donorObject = request.embed(donor, '@@object')
            if 'health_status' in donorObject:
                return donorObject['health_status']
            else:
                return None
        else:
            if humanFlag is False:
                return model_organism_health_status
            return None

    @calculated_property(define=True,
                         schema={"title": "Life stage",
                                 "type": "string"})
    def life_stage(self, request, donor=None, mouse_life_stage=None, fly_life_stage=None,
                   worm_life_stage=None, organism=None):
        humanFlag = False
        if organism is not None:
            organismObject = request.embed(organism, '@@object')
            if organismObject['scientific_name'] == 'Homo sapiens':
                humanFlag = True

        if humanFlag is True and donor is not None:
            donorObject = request.embed(donor, '@@object')
            if 'life_stage' in donorObject:
                return donorObject['life_stage']
            else:
                return 'unknown'
        else:
            if humanFlag is False:
                if mouse_life_stage is not None:
                    return mouse_life_stage
                if fly_life_stage is not None:
                    return fly_life_stage
                if worm_life_stage is not None:
                    return worm_life_stage
            return 'unknown'

    @calculated_property(define=True,
                         schema={"title": "Synchronization",
                                 "type": "string"})
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
        "title": "Model organism donor constructs",
        "description":
            "Expression or targeting vectors stably or transiently transfected "
            "(not RNAi) into a donor organism.",
        "type": "array",
        "items": {
            "title": "Model organism donor construct",
            "description": "An expression or targeting vector stably or transiently transfected "
            "(not RNAi) into a donor organism.",
            "comment": "See contstruct.json for available identifiers.",
            "type": "string",
            "linkTo": "Construct",
        },
    }, define=True)
    def model_organism_donor_constructs(self, request, donor=None):
        if donor is not None:
            return request.embed(donor, '@@object').get('constructs')

    @calculated_property(schema={
        "title": "Model organism genetic modifications",
        "description":
            "Genetic modifications made in the donor organism of the biosample.",
        "type": "array",
        "items": {
            "title": "Model organism genetic modification",
            "description": "Genetic modification made in the donor organism of the biosample.",
            "comment": "See genetic_modification.json for available identifiers.",
            "type": "string",
            "linkTo": "GeneticModification",
        },
    }, define=True)
    def model_organism_donor_modifications(self, request, donor=None):
        if donor is not None:
            return request.embed(donor, '@@object').get('genetic_modifications')

    @calculated_property(schema={
        "title": "All applied modifications",
        "description": "All genetic modifications made in either the donor and/or biosample.",
        "type": "array",
        "items": {
            "title": "All applied modification",
            "description": "Genetic modification made in either the donor and/or biosample.",
            "coment": "See genetic_modification.json for available identifiers.",
            "type": "string",
            "linkTo": "GeneticModification",
        }
    })
    def all_applied_modifications(self, request, genetic_modifications=None, model_organism_donor_modifications=None):
        if genetic_modifications is not None and model_organism_donor_modifications is not None:
            return list(set(genetic_modifications + model_organism_donor_modifications))
        elif genetic_modifications is not None and model_organism_donor_modifications is None:
            return genetic_modifications
        elif genetic_modifications is None and model_organism_donor_modifications is not None:
            return model_organism_donor_modifications
        else:
            return []

    @calculated_property(schema={
        "title": "Characterizations",
        "type": "array",
        "items": {
            "type": ['string', 'object'],
            "linkFrom": "BiosampleCharacterization.characterizes",
        },
    })
    def characterizations(self, request, characterizations):
        return paths_filtered_by_status(request, characterizations)

    @calculated_property(schema={
        "description": "The biosample(s) that have this biosample in their part_of property.",
        "comment": "Do not submit. Values in the list are reverse links of a biosamples that are part_of this biosample.",
        "title": "Child biosamples",
        "type": "array",
        "items": {
            "type": ['string', 'object'],
            "linkFrom": "Biosample.part_of",
        },
    })
    def parent_of(self, request, parent_of):
        return paths_filtered_by_status(request, parent_of)

    @calculated_property(schema={
        "title": "Age",
        "type": "string",
    })
    def age_display(self, request, donor=None, model_organism_age=None,
                    model_organism_age_units=None, post_synchronization_time=None,
                    post_synchronization_time_units=None):
        if post_synchronization_time is not None and post_synchronization_time_units is not None:
            return u'{sync_time} {sync_time_units}'.format(
                sync_time=post_synchronization_time,
                sync_time_units=post_synchronization_time_units)
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

    @calculated_property(condition='depleted_in_term_name', schema={
        "title": "depleted_in_term_id",
        "type": "string",
    })
    def depleted_in_term_id(self, request, depleted_in_term_name):

        term_lookup = {
            'head': 'UBERON:0000033',
            'limb': 'UBERON:0002101',
            'salivary gland': 'UBERON:0001044',
            'male accessory sex gland': 'UBERON:0010147',
            'testis': 'UBERON:0000473',
            'female gonad': 'UBERON:0000992',
            'digestive system': 'UBERON:0001007',
            'arthropod fat body': 'UBERON:0003917',
            'antenna': 'UBERON:0000972',
            'adult maxillary segment': 'FBbt:00003016',
            'female reproductive system': 'UBERON:0000474',
            'male reproductive system': 'UBERON:0000079'
        }

        term_id = list()
        for term_name in depleted_in_term_name:
            if term_name in term_lookup:
                term_id.append(term_lookup.get(term_name))
            else:
                term_id.append('Term ID unknown')

        return term_id

    @calculated_property(condition='subcellular_fraction_term_name', schema={
        "title": "subcellular_fraction_term_id",
        "type": "string",
    })
    def subcellular_fraction_term_id(self, request, subcellular_fraction_term_name):
        term_lookup = {
            'nucleus': 'GO:0005634',
            'cytosol': 'GO:0005829',
            'chromatin': 'GO:0000785',
            'membrane': 'GO:0016020',
            'mitochondria': 'GO:0005739',
            'nuclear matrix': 'GO:0016363',
            'nucleolus': 'GO:0005730',
            'nucleoplasm': 'GO:0005654',
            'polysome': 'GO:0005844',
            'insoluble cytoplasmic fraction': 'NTR:0002594'
        }

        if subcellular_fraction_term_name in term_lookup:
            return term_lookup.get(subcellular_fraction_term_name)
        else:
            return 'Term ID unknown'

    @calculated_property(schema={
        "title": "Summary",
        "type": "string",
    })
    def summary(self, request,
                organism=None,
                donor=None,
                age=None,
                age_units=None,
                life_stage=None,
                sex=None,
                biosample_term_name=None,
                biosample_type=None,
                starting_amount=None,
                starting_amount_units=None,
                depleted_in_term_name=None,
                phase=None,
                synchronization=None,
                subcellular_fraction_term_name=None,
                post_synchronization_time=None,
                post_synchronization_time_units=None,
                post_treatment_time=None,
                post_treatment_time_units=None,
                treatments=None,
                part_of=None,
                originated_from=None,
                transfection_method=None,
                transfection_type=None,
                genetic_modifications=None,
                constructs=None,
                model_organism_donor_constructs=None,
                rnais=None):

        sentence_parts = [
            'organism_name',
            'genotype_strain',
            'term_phrase',
            'phase',
            'fractionated',
            'sex_stage_age',
            'synchronization',
            'modifications_list',
            'originated_from',
            'treatments_phrase',
            'depleted_in'
        ]
        organismObject = None
        donorObject = None
        if organism is not None:
            organismObject = request.embed(organism, '@@object')
        if donor is not None:
            donorObject = request.embed(donor, '@@object')

        treatment_objects_list = None
        if treatments is not None and len(treatments) > 0:
            treatment_objects_list = []
            for t in treatments:
                treatment_objects_list.append(request.embed(t, '@@object'))

        part_of_object = None
        if part_of is not None:
            part_of_object = request.embed(part_of, '@@object')

        originated_from_object = None
        if originated_from is not None:
            originated_from_object = request.embed(originated_from, '@@object')

        modifications_list = None
        if genetic_modifications is not None and len(genetic_modifications) > 0:
            modifications_list = []
            for gm in genetic_modifications:
                gm_object = request.embed(gm, '@@object')
                if gm_object.get('modified_site_by_target_id'):
                    modification_dict['target'] = 
                        request.embed(gm_object.get('modified_site_by_target_id'),
                                                    '@@object')
                if gm_object.get('introdiced_tags_array'):
                    modification_dict['tags'] = []
                    for tag in gm_object.get('introdiced_tags_array'):
                        tag_dict = {'location': tag['location']}
                        if tag.get('promoter_used'):
                            tag_dict['promoter'] = 
                                request.embed(tag.get('promoter_used'),
                                                      '@@object').get['label']
                        modification_dict['tags'].append(tag_dict)

                modifications_list.append((gm_object['method'], modification_dict))

        '''construct_objects_list = None
        if constructs is not None and len(constructs) > 0:
            construct_objects_list = []
            for c in constructs:
                construct_object = request.embed(c, '@@object')
                target_name = construct_object['target']
                if 'promoter_used' in construct_object and \
                   construct_object['promoter_used'] is not None:
                    promo = construct_object['promoter_used']
                    item_to_add = (construct_object,
                                   request.embed(target_name, '@@object'),
                                   request.embed(promo, '@@object'))
                else:
                    item_to_add = (construct_object,
                                   request.embed(target_name, '@@object'),
                                   None)
                construct_objects_list.append(item_to_add)

        model_construct_objects_list = None
        if model_organism_donor_constructs is not None and len(model_organism_donor_constructs) > 0:
            model_construct_objects_list = []
            for c in model_organism_donor_constructs:
                construct_object = request.embed(c, '@@object')
                target_name = construct_object['target']
                if 'promoter_used' in construct_object and \
                   construct_object['promoter_used'] is not None:
                    promo = construct_object['promoter_used']
                    item_to_add = (construct_object,
                                   request.embed(target_name, '@@object'),
                                   request.embed(promo, '@@object'))
                else:
                    item_to_add = (construct_object,
                                   request.embed(target_name, '@@object'),
                                   None)
                model_construct_objects_list.append(item_to_add)

        rnai_objects = None
        if rnais is not None and len(rnais) > 0:
            rnai_objects = []
            for r in rnais:
                rnai_object = request.embed(r, '@@object')
                target_object = request.embed(rnai_object['target'], '@@object')
                rnai_info = {'rnai_type': rnai_object['rnai_type'],
                             'target': target_object['label']}
                rnai_objects.append(rnai_info)'''

        biosample_dictionary = generate_summary_dictionary(
            organismObject,
            donorObject,
            age,
            age_units,
            life_stage,
            sex,
            biosample_term_name,
            biosample_type,
            starting_amount,
            starting_amount_units,
            depleted_in_term_name,
            phase,
            subcellular_fraction_term_name,
            synchronization,
            post_synchronization_time,
            post_synchronization_time_units,
            post_treatment_time,
            post_treatment_time_units,
            treatment_objects_list,
            part_of_object,
            originated_from_object,
            modifications_list)

        return construct_biosample_summary([biosample_dictionary],
                                           sentence_parts)


def generate_summary_dictionary(
    organismObject=None,
    donorObject=None,
    age=None,
    age_units=None,
    life_stage=None,
    sex=None,
    biosample_term_name=None,
    biosample_type=None,
    starting_amount=None,
    starting_amount_units=None,
    depleted_in_term_name=None,
    phase=None,
    subcellular_fraction_term_name=None,
    synchronization=None,
    post_synchronization_time=None,
    post_synchronization_time_units=None,
    post_treatment_time=None,
    post_treatment_time_units=None,
    treatment_objects_list=None,
    part_of_object=None,
    originated_from_object=None,
    modifications_list=None,
    experiment_flag=False):
        dict_of_phrases = {
            'organism_name': '',
            'genotype_strain': '',
            'term_phrase': '',
            'phase': '',
            'fractionated': '',
            'sex_stage_age': '',
            'synchronization': '',
            'originated_from': '',
            'treatments_phrase': '',
            'depleted_in': '',
            'modifications_list': '',
            'strain_background': '',
            'experiment_term_phrase': ''
        }

        if organismObject is not None:
            if 'scientific_name' in organismObject:
                dict_of_phrases['organism_name'] = organismObject['scientific_name']
                if organismObject['scientific_name'] != 'Homo sapiens':  # model organism
                    if donorObject is not None:
                        if 'strain_name' in donorObject and donorObject['strain_name'].lower() != 'unknown':
                            dict_of_phrases['genotype_strain'] = 'strain ' + \
                                                                 donorObject['strain_name']
                        if 'genotype' in donorObject and donorObject['genotype'].lower() != 'unknown':
                            d_genotype = donorObject['genotype']
                            if organismObject['scientific_name'].find('Drosophila') == -1:
                                if d_genotype[-1] == '.':
                                    dict_of_phrases['genotype_strain'] += ' (' + \
                                                                          d_genotype[:-1] + ')'
                                else:
                                    dict_of_phrases['genotype_strain'] += ' (' + \
                                                                          d_genotype + ')'
                        if 'strain_background' in donorObject and \
                           donorObject['strain_background'].lower() != 'unknown':
                            dict_of_phrases['strain_background'] = donorObject['strain_background']
                        else:
                            dict_of_phrases['strain_background'] = dict_of_phrases['genotype_strain']
        if age is not None and age_units is not None:
            dict_of_phrases['age_display'] = str(age) + ' ' + age_units + 's'

        if life_stage is not None and life_stage != 'unknown':
            dict_of_phrases['life_stage'] = life_stage

        if sex is not None and sex != 'unknown':
            if experiment_flag is True:
                if sex != 'mixed':
                    dict_of_phrases['sex'] = sex

            else:
                dict_of_phrases['sex'] = sex

        if biosample_term_name is not None:
            dict_of_phrases['sample_term_name'] = biosample_term_name

        if biosample_type is not None and \
           biosample_type not in ['whole organisms', 'whole organism']:
            dict_of_phrases['sample_type'] = biosample_type

        term_name = ''

        if 'sample_term_name' in dict_of_phrases:
            if dict_of_phrases['sample_term_name'] == 'multi-cellular organism':
                term_name += 'whole organisms'
            else:
                term_name += dict_of_phrases['sample_term_name']

        dict_of_phrases['experiment_term_phrase'] = term_name

        term_type = ''

        if 'sample_type' in dict_of_phrases:
            term_type += dict_of_phrases['sample_type']

        term_dict = {}
        for w in term_type.split(' '):
            if w not in term_dict:
                term_dict[w] = 1

        term_phrase = ''
        for w in term_name.split(' '):
            if w not in term_dict and (w+'s') not in term_dict:
                term_dict[w] = 1
                term_phrase += ' ' + w

        term_phrase += ' ' + term_type
        if term_phrase.startswith(' of'):
            term_phrase = ' ' + term_phrase[3:]

        if len(term_phrase) > 0:
            dict_of_phrases['term_phrase'] = term_phrase[1:]

        if starting_amount is not None and starting_amount_units is not None:
            if starting_amount_units[-1] != 's':
                dict_of_phrases['sample_amount'] = str(starting_amount) + ' ' + \
                    str(starting_amount_units) + 's'
            else:
                dict_of_phrases['sample_amount'] = str(starting_amount) + ' ' + \
                    str(starting_amount_units)

        if depleted_in_term_name is not None and len(depleted_in_term_name) > 0:
            dict_of_phrases['depleted_in'] = 'depleted in ' + \
                                             str(depleted_in_term_name).replace('\'', '')[1:-1]

        if phase is not None:
            dict_of_phrases['phase'] = phase + ' phase'

        if subcellular_fraction_term_name is not None:
            if subcellular_fraction_term_name == 'nucleus':
                dict_of_phrases['fractionated'] = 'nuclear fraction'
            if subcellular_fraction_term_name == 'cytosol':
                dict_of_phrases['fractionated'] = 'cytosolic fraction'
            if subcellular_fraction_term_name == 'chromatin':
                dict_of_phrases['fractionated'] = 'chromatin fraction'
            if subcellular_fraction_term_name == 'membrane':
                dict_of_phrases['fractionated'] = 'membrane fraction'
            if subcellular_fraction_term_name == 'mitochondria':
                dict_of_phrases['fractionated'] = 'mitochondrial fraction'
            if subcellular_fraction_term_name == 'nuclear matrix':
                dict_of_phrases['fractionated'] = 'nuclear matrix fraction'
            if subcellular_fraction_term_name == 'nucleolus':
                dict_of_phrases['fractionated'] = 'nucleolus fraction'
            if subcellular_fraction_term_name == 'nucleoplasm':
                dict_of_phrases['fractionated'] = 'nucleoplasmic fraction'
            if subcellular_fraction_term_name == 'polysome':
                dict_of_phrases['fractionated'] = 'polysomic fraction'
            if subcellular_fraction_term_name == 'insoluble cytoplasmic fraction':
                dict_of_phrases['fractionated'] = 'insoluble cytoplasmic fraction'

        if post_synchronization_time is not None and \
           post_synchronization_time_units is not None:
            dict_of_phrases['synchronization'] = (post_synchronization_time +
                                                  ' ' + post_synchronization_time_units +
                                                  's post synchronization')
        if synchronization is not None:
            if synchronization.startswith('puff'):
                dict_of_phrases['synchronization'] += ' at ' + synchronization
            elif synchronization == 'egg bleaching':
                dict_of_phrases['synchronization'] += ' using ' + synchronization
            else:
                dict_of_phrases['synchronization'] += ' at ' + synchronization + ' stage'

        if post_treatment_time is not None and \
           post_treatment_time_units is not None:
            dict_of_phrases['post_treatment'] = (post_treatment_time +
                                                 ' ' + post_treatment_time_units +
                                                 's after the sample was ')

        if ('sample_type' in dict_of_phrases and
            dict_of_phrases['sample_type'] != 'immortalized cell line') or \
           ('sample_type' not in dict_of_phrases):
            phrase = ''

            if 'sex' in dict_of_phrases:
                if dict_of_phrases['sex'] == 'mixed':
                    phrase += dict_of_phrases['sex'] + ' sex'
                else:
                    phrase += dict_of_phrases['sex']

            stage_phrase = ''
            if 'life_stage' in dict_of_phrases:
                stage_phrase += ' ' + dict_of_phrases['life_stage']

            phrase += stage_phrase.replace("embryonic", "embryo")

            if 'age_display' in dict_of_phrases:
                phrase += ' (' + dict_of_phrases['age_display'] + ')'
            dict_of_phrases['sex_stage_age'] = phrase

        if treatment_objects_list is not None and len(treatment_objects_list) > 0:
            treatments_list = []
            for treatmentObject in treatment_objects_list:
                to_add = ''

                if experiment_flag is True:
                    if 'treatment_term_name' in treatmentObject:
                        to_add = treatmentObject['treatment_term_name'] + ' '
                else:
                    if 'amount' in treatmentObject and \
                       'amount_units' in treatmentObject:
                        to_add += str(treatmentObject['amount']) + ' ' + \
                            treatmentObject['amount_units'] + ' '
                    if 'treatment_term_name' in treatmentObject:
                        to_add += treatmentObject['treatment_term_name'] + ' '
                    if 'duration' in treatmentObject and \
                       'duration_units' in treatmentObject:
                        if treatmentObject['duration_units'][-1] == 's':
                            to_add += 'for ' + str(treatmentObject['duration']) + ' ' + \
                                treatmentObject['duration_units']
                        else:
                            to_add += 'for ' + str(treatmentObject['duration']) + ' ' + \
                                treatmentObject['duration_units'] + 's'
                if to_add != '':
                    treatments_list.append(to_add)

            if len(treatments_list) > 0:
                dict_of_phrases['treatments'] = treatments_list

        if 'treatments' in dict_of_phrases:
            if 'post_treatment' in dict_of_phrases:
                dict_of_phrases['treatments_phrase'] = dict_of_phrases['post_treatment']

            if len(dict_of_phrases['treatments']) == 1:
                dict_of_phrases['treatments_phrase'] += 'treated with ' + \
                                                        dict_of_phrases['treatments'][0]
            else:
                if len(dict_of_phrases['treatments']) > 1:
                    dict_of_phrases[
                        'treatments_phrase'] += 'treated with ' + \
                                                ', '.join(map(str, dict_of_phrases['treatments']))

        if part_of_object is not None:
            dict_of_phrases['part_of'] = 'separated from biosample '+part_of_object['accession']

        if originated_from_object is not None:
            if 'biosample_term_name' in originated_from_object:
                dict_of_phrases['originated_from'] = ('originated from ' +
                                                      originated_from_object['biosample_term_name'])

        '''if transfection_type is not None:  # stable/transient
            if transfection_type == 'stable':
                dict_of_phrases['transfection_type'] = 'stably'
            else:
                dict_of_phrases['transfection_type'] = transfection_type + 'ly''''

        ''' modification .method               
                "CRISPR", V
                "TALEN", V
                "stable transfection", V
                "transient transfection", V
                "site-specific recombination",
                "transduction",
                "RNAi", V
                "mutagen treatment",
                "microinjection",
                "bombardment"
                
        modification.category
                        "deletion",
                "insertion",
                "replacement",
                "mutagenesis",
                "interference"        
                
                for biosample:
                    for CRISPR and TALEN:

                        'genetically modified (' + modification.category + ') using ' + modification.method + ' '

                    for RNAi:

                        if modified_site_by_target_id is present then:
                            'expressing RNAi targeting ' + modification.modified_site_by_target_id.label
                        otherwise:
                            'expressing RNAi'
                    
                    for constructs:
                        stably/transiently expressing 

                            if introdiced_tags then:
                                for tag in cons['tags']:
                                    
> for every tag we have : name, location, promoter_used (name and location are required)

                                    if tag['location'] in ['N-terminal', 'C-terminal']:
                                        addition += tag['location'] + ' '
                                    
                                    if promoter is not None:
                                        addition += tar['label'] + ' ' + \
                                            cons['construct_type'] + \
                                            ' under ' + promoter['label'] + \
                                            ' promoter'
                                    else:
                                        addition += tar['label'] + ' ' + \
                                            cons['construct_type']

                            else:
                                    construct_object,
                                   request.embed(target_name, '@@object'),
                                   request.embed(promo, '@@object')




            FOR ALL THE REST:
             "site-specific recombination",
                "transduction",
                "mutagen treatment",
                "microinjection",
                "bombardment"

    do modification.method ' targeting' target if present!!

                for experiment:

                    >to all:

                    genetically modified using 'method'

                    

                '''

        if modifications_list is not None and len(modifications_list) > 0:
            gm_methods = set()
            gm_summaries = []
            for (gm_method, gm_object) in modifications_list:
                gm_methods.add(gm_method)
                gm_summaries.append(generate_modification_summary(gm_method, gm_object))
                
            if experiment_flag is True:
                dict_of_phrases['modifications_list'] = 'genetically modified using ' + 
                    ', '.join(map(str, list(gm_methods)))
            else:
                dict_of_phrases['modifications_list'] = ', '.join(map(str, list(gm_summaries)))
        '''    result_set = set()
            talen_flag = False
            for (gm_type, gm_technique) in modifications_list:
                if 'Tale' in gm_technique['@type']:
                    result_set.add(gm_type)
                    talen_flag = True
            if experiment_flag is True:
                if talen_flag is True:
                    dict_of_phrases['modifications_list'] = 'genetically modified using TALEs '
            else:
                if talen_flag is True:
                    tale_string = ''
                    for x in sorted(list(result_set)):
                        tale_string += str(x) + ', '
                    dict_of_phrases['modifications_list'] = 'genetically modified (' + \
                                                            tale_string[:-2] + ') using TALEs '

        if construct_objects_list is not None and len(construct_objects_list) > 0:
            constructs_list = []
            construct_types = set()
            for construct_data in construct_objects_list:
                cons = construct_data[0]
                tar = construct_data[1]
                promoter = construct_data[2]
                if 'tags' in cons:
                    for tag in cons['tags']:
                        addition = ''
                        if experiment_flag is True:
                            addition += tar['label'] + ' ' + \
                                cons['construct_type']
                        else:
                            if tag['location'] in ['N-terminal', 'C-terminal']:
                                addition += tag['location'] + ' '
                            if promoter is not None:
                                addition += tar['label'] + ' ' + \
                                    cons['construct_type'] + \
                                    ' under ' + promoter['label'] + \
                                    ' promoter'
                            else:
                                addition += tar['label'] + ' ' + \
                                    cons['construct_type']
                        constructs_list.append(addition)
                        construct_types.add(cons['construct_type'])
                else:
                    constructs_list.append(tar['label'])
            if experiment_flag is True:
                dict_of_phrases['constructs'] = 'expressing ' + ', '.join(
                    sorted(list(construct_types)))
            else:
                if len(constructs_list) == 1:
                    dict_of_phrases['constructs'] = 'expressing ' + constructs_list[0]
                elif len(constructs_list) > 1:
                    dict_of_phrases['constructs'] = 'expressing ' + \
                        ', '.join(map(str, list(set(constructs_list))))

        if model_construct_objects_list is not None and len(model_construct_objects_list) > 0:
            constructs_list = []
            construct_types = set()
            for construct_data in model_construct_objects_list:
                cons = construct_data[0]
                tar = construct_data[1]
                promoter = construct_data[2]
                if 'tags' in cons:
                    for tag in cons['tags']:
                        addition = ''
                        if experiment_flag is True:
                            addition += tar['label'] + ' ' + \
                                cons['construct_type']
                        else:
                            if tag['location'] in ['N-terminal', 'C-terminal']:
                                addition += tag['location'] + ' '
                            if promoter is not None:
                                addition += tar['label'] + ' ' + \
                                    cons['construct_type'] + \
                                    ' under ' + promoter['label'] + \
                                    ' promoter'
                            else:
                                addition += tar['label'] + ' ' + \
                                    cons['construct_type']
                        constructs_list.append(addition)
                        construct_types.add(cons['construct_type'])
                else:
                    constructs_list.append(tar['label'])
            if experiment_flag is True:
                dict_of_phrases['model_organism_constructs'] = 'expressing ' + ', '.join(
                    sorted(list(construct_types)))
            else:

                if len(constructs_list) == 1:
                    dict_of_phrases['model_organism_constructs'] = 'expressing ' + constructs_list[0]
                elif len(constructs_list) > 1:
                    dict_of_phrases['model_organism_constructs'] = 'expressing ' + \
                        ', '.join(map(str, list(set(constructs_list))))

        if rnai_objects is not None and len(rnai_objects) > 0:
            if experiment_flag is True:
                dict_of_phrases['rnais'] = 'expressing RNAi '
            else:
                rnais_list = []
                for rnaiObject in rnai_objects:
                    rnais_list.append('expressing ' + rnaiObject['rnai_type'] +
                                      ' targeting ' + rnaiObject['target'])
                dict_of_phrases['rnais'] = ', '.join(map(str, list(set(rnais_list))))'''

        return dict_of_phrases


def generate_modification_summary(method, modification):
    
    # modification_object
    # modified_site_by_target_id_object
    # introdiced_tags_array
    # introduced_tags_promoter_object   tags list and target

    if method in ['stable transfection', 'transient transfection'] and modification.get('target'):
        sentence = 'stably'
        if method == 'transient transfection':
            sentence = 'transiently'
        sentence += ' expressing'
        
        tags_list = []
        for tag in modification.get('tags'):
            addition = ''
            if tag.get('location') in ['N-terminal', 'C-terminal']:
                addition += ' ' + tag.get('location')
            addition += ' ' + modification.get('target')
            if tag.get('promoter'):
                addition += ' under ' + tag.get('promoter') + ' promoter'
            tags_list.append(addition)
        return (sentence + ', '.join(map(str, list(set(tags_list)).strip()    
    else:
        sentence = 'genetically modified (' + modification['category'] + ') using ' + method
        if method == 'RNAi':
            sentence = 'expressing RNAi'

        if modification.get('target'):
            sentence += ' targeting ' + modification.get('target')
        return sentence.strip()


def generate_sentence(phrases_dict, values_list):
    sentence = ''
    for key in values_list:
        if phrases_dict[key] != '':
            sentence += phrases_dict[key].strip() + ' '
    return sentence.strip()


def is_identical(list_of_dicts, key):
    initial_value = list_of_dicts[0][key]
    for d in list_of_dicts:
        if d[key] != initial_value:
            return False
    return True


def construct_biosample_summary(phrases_dictionarys, sentence_parts):

    negations_dict = {
        'phase': 'unspecified phase',
        'fractionated': 'unspecified fraction',
        'synchronization': 'not synchronized',
        'treatments_phrase': 'not treated',
        'depleted_in': 'not depleted',
        'genetic_modifications': 'not modified'
    }
    if len(phrases_dictionarys) > 1:
        index = 0
        min_index = len(sentence_parts)
        max_index = -1
        for part in sentence_parts:
            if is_identical(phrases_dictionarys, part) is False:
                if min_index > index:
                    min_index = index
                if max_index < index:
                    max_index = index
            index += 1

        if max_index == -1:
            sentence_to_return = generate_sentence(phrases_dictionarys[0], sentence_parts)
        else:
            if min_index == 0:
                prefix = ''
            else:
                prefix = generate_sentence(phrases_dictionarys[0], sentence_parts[0:min_index])
            if (max_index+1) == len(sentence_parts):
                suffix = ''
            else:
                suffix = generate_sentence(phrases_dictionarys[0], sentence_parts[max_index+1:])
            middle = []
            for d in phrases_dictionarys:
                part_to_add = generate_sentence(d, sentence_parts[min_index:max_index+1])
                if part_to_add != '':
                    middle.append(part_to_add)
                else:
                    constructed_middle = []
                    for x in range(min_index, max_index+1):
                        if sentence_parts[x] in negations_dict:
                            constructed_middle.append(negations_dict[sentence_parts[x]])
                    if len(constructed_middle) == 0:
                        middle.append('NONE')
                    elif len(constructed_middle) == 1:
                        middle.append(constructed_middle[0])
                    else:
                        middle.append(', '.join(map(str, constructed_middle)))
            sentence_middle = sorted(list(set(middle)))
            if prefix == '':
                sentence_to_return = ' and '.join(map(str, sentence_middle))
            else:
                sentence_to_return = prefix.strip() + ' ' + \
                    ' and '.join(map(str, sentence_middle))
            if suffix != '':
                sentence_to_return += ', ' + suffix
    else:
        sentence_to_return = generate_sentence(phrases_dictionarys[0], sentence_parts)

    words = sentence_to_return.split(' ')
    if words[-1] in ['transiently', 'stably']:
        sentence_to_return = ' '.join(words[:-1])

    rep = {
        ' percent': '%',
        '1 hours': '1 hour',
        '1 days': '1 day',
        '1 minutes': '1 minute',
        '1 months': '1 month',
        '1 weeks': '1 week',
        '1 years': '1 year',
        '.0 ': ' ',
    }
    rep = dict((re.escape(k), v) for k, v in rep.items())
    pattern = re.compile("|".join(rep.keys()))
    return pattern.sub(lambda m: rep[re.escape(m.group(0))], sentence_to_return)
