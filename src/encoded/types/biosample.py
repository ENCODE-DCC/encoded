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
        'treatments.protocols.submitted_by',
        'treatments.protocols.lab',
        'treatments.protocols.award',
        'constructs',
        'constructs.documents.submitted_by',
        'constructs.documents.award',
        'constructs.documents.lab',
        'constructs.target',
        'protocol_documents.lab',
        'protocol_documents.award',
        'protocol_documents.submitted_by',
        'derived_from',
        'part_of',
        'part_of.protocol_documents',
        'part_of.protocol_documents.award',
        'part_of.protocol_documents.lab',
        'part_of.protocol_documents.submitted_by',
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
        'part_of.treatments.protocols',
        'part_of.talens.documents',
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
        'talens',
        'talens.documents',
        'talens.documents.award',
        'talens.documents.lab',
        'talens.documents.submitted_by',
    ]
    audit_inherit = [
        'donor',
        'donor.mutated_gene',
        'donor.organism',
        'donor.characterizations',
        'donor.characterizations.award',
        'donor.characterizations.lab',
        'donor.characterizations.submitted_by',
        'donor.donor_documents',
        'donor.donor_documents.award',
        'donor.donor_documents.lab',
        'donor.donor_documents.submitted_by',
        'donor.references',
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
        'treatments',
        'treatments.protocols.submitted_by',
        'treatments.protocols.lab',
        'treatments.protocols.award',
        'constructs',
        'constructs.documents.submitted_by',
        'constructs.documents.award',
        'constructs.documents.lab',
        'constructs.target',
        'protocol_documents.lab',
        'protocol_documents.award',
        'protocol_documents.submitted_by',
        'derived_from',
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
        'talens',
        'talens.documents',
        'talens.documents.award',
        'talens.documents.lab',
        'talens.documents.submitted_by'
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
            "linkTo": "Construct",
        },
    }, define=True)
    def model_organism_donor_constructs(self, request, donor=None):
        if donor is not None:
            return request.embed(donor, '@@object').get('constructs')

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
                subcellular_fraction_term_name=None,
                post_synchronization_time=None,
                post_synchronization_time_units=None,
                post_treatment_time=None,
                post_treatment_time_units=None,
                treatments=None,
                part_of=None,
                derived_from=None,
                transfection_method=None,
                transfection_type=None,
                talens=None,
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
            'derived_from',
            'transfection_type',
            'rnais',
            'treatments_phrase',
            'depleted_in',
            'talens',
            'constructs',
            'model_organism_constructs'
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

        derived_from_object = None
        if derived_from is not None:
            derived_from_object = request.embed(derived_from, '@@object')

        talen_objects_list = None
        if talens is not None and len(talens) > 0:
            talen_objects_list = []
            for t in talens:
                talen_objects_list.append(request.embed(t, '@@object'))

        construct_objects_list = None
        if constructs is not None and len(constructs) > 0:
            construct_objects_list = []
            for c in constructs:
                construct_object = request.embed(c, '@@object')
                target_name = construct_object['target']
                construct_objects_list.append(request.embed(target_name, '@@object'))

        model_construct_objects_list = None
        if model_organism_donor_constructs is not None and len(model_organism_donor_constructs) > 0:
            model_construct_objects_list = []
            for c in model_organism_donor_constructs:
                construct_object = request.embed(c, '@@object')
                target_name = construct_object['target']
                model_construct_objects_list.append(request.embed(target_name, '@@object'))

        rnai_objects = None
        if rnais is not None and len(rnais) > 0:
            rnai_objects = []
            for r in rnais:
                rnai_object = request.embed(r, '@@object')
                target_object = request.embed(rnai_object['target'], '@@object')
                rnai_info = {'rnai_type': rnai_object['rnai_type'],
                             'target': target_object['label']}
                rnai_objects.append(rnai_info)

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
            post_synchronization_time,
            post_synchronization_time_units,
            post_treatment_time,
            post_treatment_time_units,
            transfection_type,
            treatment_objects_list,
            part_of_object,
            derived_from_object,
            talen_objects_list,
            construct_objects_list,
            model_construct_objects_list,
            rnai_objects)

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
    post_synchronization_time=None,
    post_synchronization_time_units=None,
    post_treatment_time=None,
    post_treatment_time_units=None,
    transfection_type=None,
    treatment_objects_list=None,
    part_of_object=None,
    derived_from_object=None,
    talen_objects_list=None,
    construct_objects_list=None,
    model_construct_objects_list=None,
    rnai_objects=None
):
        dict_of_phrases = {
            'organism_name': '',
            'genotype_strain': '',
            'term_phrase': '',
            'phase': '',
            'fractionated': '',
            'sex_stage_age': '',
            'synchronization': '',
            'derived_from': '',
            'transfection_type': '',
            'rnais': '',
            'treatments_phrase': '',
            'depleted_in': '',
            'talens': '',
            'constructs': '',
            'model_organism_constructs': ''
        }

        if organismObject is not None:
            if 'scientific_name' in organismObject:
                dict_of_phrases['organism_name'] = organismObject['scientific_name']
                if organismObject['scientific_name'] != 'Homo sapiens':  # model organism
                    if donorObject is not None:
                        if 'strain_name' in donorObject:
                            dict_of_phrases['genotype_strain'] = 'strain ' + \
                                                                 donorObject['strain_name']
                        if 'genotype' in donorObject:
                            d_genotype = donorObject['genotype']
                            if organismObject['scientific_name'].find('Drosophila') == -1:
                                if d_genotype[-1] == '.':
                                    dict_of_phrases['genotype_strain'] += ' (' + \
                                                                          d_genotype[:-1] + ')'
                                else:
                                    dict_of_phrases['genotype_strain'] += ' (' + \
                                                                          d_genotype + ')'

        if age is not None and age_units is not None:
            dict_of_phrases['age_display'] = str(age) + ' ' + age_units + 's'

        if life_stage is not None and life_stage != 'unknown':
            dict_of_phrases['life_stage'] = life_stage

        if sex is not None and sex != 'unknown':
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

        if post_synchronization_time is not None and post_synchronization_time_units is not None:
            dict_of_phrases['synchronization'] = (post_synchronization_time +
                                                  ' ' + post_synchronization_time_units +
                                                  's post synchronization')

        if post_treatment_time is not None and post_treatment_time_units is not None:
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
                if 'concentration' in treatmentObject and \
                   'concentration_units' in treatmentObject:
                    to_add += str(treatmentObject['concentration']) + ' ' + \
                        treatmentObject['concentration_units'] + ' '
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

        if derived_from_object is not None:
            if 'biosample_term_name' in derived_from_object:
                dict_of_phrases['derived_from'] = ('derived from ' +
                                                   derived_from_object['biosample_term_name'])

        if transfection_type is not None:  # stable/transient
            if transfection_type == 'stable':
                dict_of_phrases['transfection_type'] = 'stably'
            else:
                dict_of_phrases['transfection_type'] = transfection_type + 'ly'

        if talen_objects_list is not None and len(talen_objects_list) > 0:
            talens_list = []
            for talenObject in talen_objects_list:
                if 'name' in talenObject:
                    talens_list.append(talenObject['name'])
            dict_of_phrases['talens'] = 'with talens: '+str(talens_list)

        if construct_objects_list is not None and len(construct_objects_list) > 0:
            constructs_list = []
            for target in construct_objects_list:
                constructs_list.append(target['label'])

            if len(constructs_list) == 1:
                dict_of_phrases['constructs'] = 'expressing ' + constructs_list[0]
            else:
                if len(constructs_list) > 1:
                    dict_of_phrases['constructs'] = 'expressing ' + \
                        ', '.join(map(str, list(set(constructs_list))))

        if model_construct_objects_list is not None and len(model_construct_objects_list) > 0:
            constructs_list = []
            for target in model_construct_objects_list:
                constructs_list.append(target['label'])

            if len(constructs_list) == 1:
                dict_of_phrases['model_organism_constructs'] = 'expressing ' + constructs_list[0]
            else:
                if len(constructs_list) > 1:
                    dict_of_phrases['model_organism_constructs'] = 'expressing ' + \
                        ', '.join(map(str, list(set(constructs_list))))

        if rnai_objects is not None and len(rnai_objects) > 0:
            rnais_list = []
            for rnaiObject in rnai_objects:
                    rnais_list.append(rnaiObject['rnai_type'] + ' ' + rnaiObject['target'])

            dict_of_phrases['rnais'] = ', '.join(map(str, list(set(rnais_list))))

        return dict_of_phrases


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
        'transfection_type': 'not transfected',
        'rnais': 'no RNAis',
        'treatments_phrase': 'not treated',
        'depleted_in': 'not depleted',
        'talens': 'no TALENs',
        'constructs': 'no constructs',
        'model_organism_constructs': 'no constructs',
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
