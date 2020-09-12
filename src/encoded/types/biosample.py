from snovault import (
    abstract_collection,
    calculated_property,
    collection,
    CONNECTION,
    load_schema,
)
from .base import (
    Item,
    paths_filtered_by_status,
)
import re


def property_closure(request, propname, root_uuid):
    conn = request.registry[CONNECTION]
    seen = set()
    remaining = {str(root_uuid)}
    while remaining:
        seen.update(remaining)
        next_remaining = set()
        for uuid in remaining:
            obj = conn.get_by_uuid(uuid)
            next_remaining.update(obj.__json__(request).get(propname, ()))
        remaining = next_remaining - seen
    return seen


def caclulate_donor_prop(self, request, donors, propname):
    collected_values = []

    if donors is not None:  # try to get the sex from the donor
        for donor_id in donors:
            donorObject = request.embed(donor_id, '@@object')
            if propname in donorObject and donorObject[propname] not in collected_values:
                collected_values.append(donorObject[propname])

    if not collected_values:
        return ['unknown']
    else:
        return collected_values


@abstract_collection(
    name='biosamples',
    unique_key='accession',
    properties={
        'title': 'Biosamples',
        'description': 'Listing of all types of biosample.',
    })
class Biosample(Item):
    base_types = ['Biosample'] + Item.base_types
    name_key = 'accession'
    rev = {}
    embedded = [
        'biosample_ontology'
    ]

    @calculated_property(define=True,
                         schema={"title": "Donors",
                                 "type": "array",
                                 "items": {
                                    "type": "string",
                                    "linkTo": "Donor"
                                    }
                                })
    def donors(self, request, registry):
        connection = registry[CONNECTION]
        derived_from_closure = property_closure(request, 'derived_from', self.uuid) - {str(self.uuid)}
        obj_props = (request.embed(uuid, '@@object') for uuid in derived_from_closure)
        all_donors = {
            props['accession']
            for props in obj_props
            if 'Donor' in props['@type']
        }
        return sorted(all_donors)

    @calculated_property(define=True,
                         schema={"title": "Organism",
                                 "type": "string",
                                 "linkTo": "Organism"
                                })
    def organism(self, request, registry, donors=None):
        if donors is not None:
            for donor_id in donors:
                donorObject = request.embed(donor_id, '@@object')
                if 'organism' in donorObject:
                    return donorObject['organism']

    @calculated_property(define=True,
                         schema={"title": "Sex",
                                 "type": "array",
                                 "items": {
                                    "type": "string"
                                    }
                                 })
    def sex(self, request, donors=None, model_organism_sex=None, organism=None):
        humanFlag = False
        if organism is not None:
            organismObject = request.embed(organism, '@@object')
            if organismObject['scientific_name'] == 'Homo sapiens':
                humanFlag = True

        if humanFlag is True:
            if donors is not None:
                return caclulate_donor_prop(self, request, donors, 'sex')
            else:
                return ['unknown']

        else:
            if model_organism_sex is not None:
                return [model_organism_sex]
            else:
                return ['unknown']

    @calculated_property(define=True,
                         schema={"title": "Age",
                                 "type": "array",
                                 "items": {
                                    "type": "string"
                                    }
                                 })
    def age(self, request, donors=None, model_organism_age=None, organism=None):
        humanFlag = False
        if organism is not None:
            organismObject = request.embed(organism, '@@object')
            if organismObject['scientific_name'] == 'Homo sapiens':
                humanFlag = True

        if humanFlag is True:
            if donors is not None:
                return caclulate_donor_prop(self, request, donors, 'age')
            else:
                return ['unknown']

        else:
            if model_organism_age is not None:
                return [model_organism_age]
            else:
                return ['unknown']

    @calculated_property(define=True,
                         schema={"title": "Age units",
                                 "type": "array",
                                 "items": {
                                    "type": "string"
                                    }
                                 })
    def age_units(self, request, donors=None, model_organism_age_units=None, organism=None):
        humanFlag = False
        if organism is not None:
            organismObject = request.embed(organism, '@@object')
            if organismObject['scientific_name'] == 'Homo sapiens':
                humanFlag = True

        if humanFlag is True:
            if donors is not None:
                return caclulate_donor_prop(self, request, donors, 'age_units')
            else:
                return ['unknown']

        else:
            if model_organism_age_units is not None:
                return [model_organism_age_units]
            else:
                return ['unknown']


    @calculated_property(define=True,
                        schema={
                        "title": "Age display",
                                 "type": "array",
                                 "items": {
                                    "type": "string"
                                    }
                                 })
    def age_display(self, request, donors=None):
        if donors is not None:
            return caclulate_donor_prop(self, request, donors, 'age_display')
        else:
            return ['unknown']


    @calculated_property(define=True,
                         schema={"title": "Donor diseases",
                                 "type": "array",
                                 "items": {
                                    "type": "string"
                                    }
                                 })
    def donor_diseases(self, request, donors=None, organism=None):
        humanFlag = False
        if organism is not None:
            organismObject = request.embed(organism, '@@object')
            if organismObject['scientific_name'] == 'Homo sapiens':
                humanFlag = True

        if humanFlag is True:
            if donors is not None:
                return caclulate_donor_prop(self, request, donors, 'diseases')
            else:
                return ['unknown']

        else:
            return ['unknown']

    @calculated_property(define=True,
                         schema={"title": "Life stage",
                                 "type": "array",
                                 "items": {
                                    "type": "string"
                                    }
                                 })
    def life_stage(self, request, donors=None, mouse_life_stage=None, organism=None):
        humanFlag = False
        if organism is not None:
            organismObject = request.embed(organism, '@@object')
            if organismObject['scientific_name'] == 'Homo sapiens':
                humanFlag = True

        if humanFlag is True:
            if donors is not None:
                return caclulate_donor_prop(self, request, donors, 'life_stage')
            else:
                return ['unknown']

        else:
            if mouse_life_stage is not None:
                return [mouse_life_stage]
            else:
                return ['unknown']

    @calculated_property(schema={
        "title": "Summary",
        "type": "string",
    })
    def summary(self, request,
                item_type=None,
                organism=None,
                donors=None,
                age_display=None,
                life_stage=None,
                sex=None,
                biosample_ontology=None,
                starting_amount=None,
                starting_amount_units=None,
                depleted_in_term_name=None,
                post_treatment_time=None,
                post_treatment_time_units=None,
                treatments=None,
                transfection_method=None,
                transfection_type=None,
                preservation_method=None):

        sentence_parts = [
            'organism_name',
            'genotype_strain',
            'sex_stage_age',
            'term_phrase',
            'treatments_phrase',
            'preservation_method',
            'depleted_in'
        ]
        organismObject = None
        donorObject = []
        if organism is not None:
            organismObject = request.embed(organism, '@@object')
        if donors is not None:
            for donor_id in donors:
                donorObject.append(request.embed(donor_id, '@@object'))

        treatment_objects_list = None
        if treatments is not None and len(treatments) > 0:
            treatment_objects_list = []
            for t in treatments:
                treatment_objects_list.append(request.embed(t, '@@object'))

        if biosample_ontology:
            biosample_type_object = request.embed(biosample_ontology, '@@object')
            biosample_term_name = biosample_type_object['term_name']
        else:
            biosample_term_name = None

        biosample_type = item_type

        biosample_dictionary = generate_summary_dictionary(
            request,
            organismObject,
            donorObject,
            age_display,
            life_stage,
            sex,
            biosample_term_name,
            biosample_type,
            starting_amount,
            starting_amount_units,
            depleted_in_term_name,
            post_treatment_time,
            post_treatment_time_units,
            treatment_objects_list,
            preservation_method)

        return construct_biosample_summary([biosample_dictionary],
                                           sentence_parts)

    @calculated_property(schema={
        "title": "Perturbed",
        "description": "A flag to indicate whether the biosample has been perturbed with a treatment.",
        "type": "boolean",
        "notSubmittable": True,
    })
    def perturbed(
        self,
        request,
        treatments=None,
    ):
        return bool(treatments)


def generate_summary_dictionary(
        request,
        organismObject=None,
        donorObject=None,
        age_display=None,
        life_stage=None,
        sex=None,
        biosample_term_name=None,
        biosample_type=None,
        starting_amount=None,
        starting_amount_units=None,
        depleted_in_term_name=None,
        post_treatment_time=None,
        post_treatment_time_units=None,
        treatment_objects_list=None,
        preservation_method=None,
        experiment_flag=False):
    dict_of_phrases = {
        'organism_name': '',
        'genotype_strain': '',
        'term_phrase': '',
        'sex_stage_age': '',
        'treatments_phrase': '',
        'depleted_in': '',
        'strain_background': '',
        'preservation_method': '',
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
    if age_display is not None and age_display != ['unknown']:
        if len(age_display) == 1:
            dict_of_phrases['age_display'] = age_display[0]
        else:
            dict_of_phrases['age_display'] = 'mixed age'

    if life_stage is not None and life_stage != ['unknown']:
        if len(life_stage) == 1:
            dict_of_phrases['life_stage'] = life_stage[0]
        else:
            dict_of_phrases['life_stage'] = 'mixed life stage'

    if sex is not None and sex != ['unknown']:
        if sex != 'mixed' and len(sex) == 1:
            dict_of_phrases['sex'] = sex[0]
        else:
            dict_of_phrases['sex'] = 'mixed sex'

    if preservation_method is not None:
        if len(preservation_method) == 1:
            dict_of_phrases['preservation_method'] = 'preserved by ' + \
                                                            str(preservation_method)
    if biosample_term_name is not None:
        dict_of_phrases['sample_term_name'] = str(biosample_term_name)

    if biosample_type is not None:
        dict_of_phrases['sample_type'] = biosample_type

    term_name = ''

    if 'sample_term_name' in dict_of_phrases:
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
        if str(starting_amount_units)[-1] != 's':
            dict_of_phrases['sample_amount'] = str(starting_amount) + ' ' + \
                str(starting_amount_units) + 's'
        else:
            dict_of_phrases['sample_amount'] = str(starting_amount) + ' ' + \
                str(starting_amount_units)

    if depleted_in_term_name is not None and len(depleted_in_term_name) > 0:
        dict_of_phrases['depleted_in'] = 'depleted in ' + \
                                            str(depleted_in_term_name).replace('\'', '')[1:-1]

    if post_treatment_time is not None and \
        post_treatment_time_units is not None:
        dict_of_phrases['post_treatment'] = '{} after the sample was '.format(
            pluralize(post_treatment_time, post_treatment_time_units)
            )

    phrase = ''

    stage_phrase = ''
    if 'life_stage' in dict_of_phrases:
        phrase += ' ' + dict_of_phrases['life_stage']

    if 'sex' in dict_of_phrases and 'age_display' in dict_of_phrases:
        phrase +=' (' + dict_of_phrases['sex'] + ', ' + dict_of_phrases['age_display'] + ')'
    elif 'sex' in dict_of_phrases:
        phrase += ' (' + dict_of_phrases['sex'] + ')'
    elif 'age_display' in dict_of_phrases:
        phrase += ' (' + dict_of_phrases['age_display'] + ')'
    dict_of_phrases['sex_stage_age'] = phrase

    if treatment_objects_list is not None and len(treatment_objects_list) > 0:
        treatments_list = []
        for treatment_object in treatment_objects_list:
            to_add = ''
            amt = treatment_object.get('amount', '')
            amt_units = treatment_object.get('amount_units', '')
            treatment_term_name = treatment_object.get('treatment_term_name', '')
            dur = treatment_object.get('duration', '')
            dur_units = treatment_object.get('duration_units', '')
            to_add = "{}{}{}".format(
                (str(amt) + ' ' + amt_units + ' ' if amt and amt_units else ''),
                (treatment_term_name + ' ' if treatment_term_name else ''),
                ('for ' + pluralize(dur, dur_units) if dur and dur_units else '')
            )
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

    return dict_of_phrases


def generate_sentence(phrases_dict, values_list):
    sentence = ''
    for key in values_list:
        if phrases_dict[key] != '':
            if 'preservation_method' in key:
                sentence = sentence.strip() + ', ' + \
                                    phrases_dict[key].strip() + ' '
            else:
                sentence += phrases_dict[key].strip() + ' '
    return sentence.strip()


def is_identical(list_of_dicts, key):
    initial_value = list_of_dicts[0][key]
    for d in list_of_dicts:
        if d[key] != initial_value:
            return False
    return True


def pluralize(value, value_units):
    try:
        if float(value) == 1:
            return str(value) + ' ' + value_units
        else:
            return str(value) + ' ' + value_units + 's'
    except:
        return str(value) + ' ' + value_units + 's'


def construct_biosample_summary(phrases_dictionarys, sentence_parts):
    negations_dict = {
        'treatments_phrase': 'not treated',
        'depleted_in': 'not depleted'
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
        '.0 ': ' ',
    }
    rep = dict((re.escape(k), v) for k, v in rep.items())
    pattern = re.compile("|".join(rep.keys()))
    return pattern.sub(lambda m: rep[re.escape(m.group(0))], sentence_to_return)


@abstract_collection(
    name='cultures',
    unique_key='accession',
    properties={
        'title': 'Cultures',
        'description': 'Listing of all types of culture.',
    })
class Culture(Biosample):
    item_type = 'analysis_file'
    base_types = ['Culture'] + Biosample.base_types
    schema = load_schema('encoded:schemas/culture.json')
    embedded = Biosample.embedded + []


@collection(
    name='cell-cultures',
    unique_key='accession',
    properties={
        'title': 'Cell cultures',
        'description': 'Listing of Cell cultures',
    })
class CellCulture(Culture):
    item_type = 'cell_culture'
    schema = load_schema('encoded:schemas/cell_culture.json')
    embedded = Culture.embedded + []


@collection(
    name='suspensions',
    unique_key='accession',
    properties={
        'title': 'Suspensions',
        'description': 'Listing of Suspensions',
    })
class Suspension(Biosample):
    item_type = 'suspension'
    schema = load_schema('encoded:schemas/suspension.json')
    embedded = Biosample.embedded + []


@collection(
    name='organoids',
    unique_key='accession',
    properties={
        'title': 'Organoids',
        'description': 'Listing of Organoids',
    })
class Organoid(Culture):
    item_type = 'organoid'
    schema = load_schema('encoded:schemas/organoid.json')
    embedded = Culture.embedded + []


@collection(
    name='tissues',
    unique_key='accession',
    properties={
        'title': 'Tissues',
        'description': 'Listing of Tissues',
    })
class Tissue(Biosample):
    item_type = 'tissue'
    schema = load_schema('encoded:schemas/tissue.json')
    embedded = Biosample.embedded + []
