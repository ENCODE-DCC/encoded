from contentbase import (
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
    }
    embedded = [
        'donor',
        'donor.mutated_gene',
        'donor.organism',
        'donor.characterizations',
        'donor.characterizations.award',
        'donor.characterizations.lab',
        'donor.characterizations.submitted_by',
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
            if organismObject['scientific_name']=='Homo sapiens':
                humanFlag = True

        if humanFlag == True:
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
            if organismObject['scientific_name']=='Homo sapiens':
                humanFlag = True

        if humanFlag == True:
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
                treatments=None,
                part_of=None,
                derived_from=None,
                transfection_method=None,
                transfection_type=None,
                talens=None,
                constructs=None,
                model_organism_donor_constructs=None,
                rnais=None):

        dict_of_phrases = {}

        if organism is not None:
            organismObject = request.embed(organism, '@@object')
            if 'scientific_name' in organismObject:
                dict_of_phrases['organism_name'] = organismObject['scientific_name']

                if organismObject['scientific_name'] != 'Homo sapiens':  # model organism
                    if donor is not None:
                        donorObject = request.embed(donor, '@@object')
                        if 'strain_name' in donorObject:
                            dict_of_phrases['strain_name'] = donorObject['strain_name']
                        if 'genotype' in donorObject:
                            dict_of_phrases['genotype'] = donorObject['genotype']

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

        if starting_amount is not None and starting_amount_units is not None:
            if starting_amount_units[-1] != 's':
                dict_of_phrases['sample_type'] = str(starting_amount) + ' ' + \
                    str(starting_amount_units) + 's'
            else:
                dict_of_phrases['sample_type'] = str(starting_amount) + ' ' + \
                    str(starting_amount_units)

        if depleted_in_term_name is not None and len(depleted_in_term_name) > 0:
            dict_of_phrases['depleted_in'] = 'depleted in '+str(depleted_in_term_name)

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
        # relevant only in worms and flys

        if post_synchronization_time is not None and post_synchronization_time_units is not None:
            dict_of_phrases['synchronization'] = (post_synchronization_time +
                                                  ' ' + post_synchronization_time_units +
                                                  's post synchronization')

        if treatments is not None and len(treatments) > 0:
            treatments_list = []
            for t in treatments:
                treatmentObject = request.embed(t, '@@object')
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

        if part_of is not None:
            part_ofObject = request.embed(part_of, '@@object')
            dict_of_phrases['part_of'] = 'separated from biosample '+part_ofObject['accession']

        if derived_from is not None:
            derived_fromObject = request.embed(derived_from, '@@object')
            if 'biosample_term_name' in derived_fromObject:
                dict_of_phrases['derived_from'] = ('derived from ' +
                                                   derived_fromObject['biosample_term_name'])

        if transfection_type is not None:  # stable/transient
                dict_of_phrases['transfection'] = transfection_type

        if talens is not None and len(talens) > 0:
            talens_list = []
            for t in talens:
                talenObject = request.embed(t, '@@object')
                if 'name' in talenObject:
                    talens_list.append(talenObject['name'])
            dict_of_phrases['talens'] = 'talens: '+str(talens_list)

        '''* * * *
        * transfection is true also for constructs !!!!
        * still have to solve multile similar words problem in bio_type/term for exmple
        * Homo sapiens endothelial cell of umbilical vein primary cell newborn
        * * * *'''

        if constructs is not None and len(constructs) > 0:
            constructs_list = []
            for c in constructs:
                constructObject = request.embed(c, '@@object')
                to_add = ''
                if 'target' in constructObject:
                    targetObject = request.embed(constructObject['target'], '@@object')
                    to_add += targetObject['name']
                if to_add != '':
                    constructs_list.append(to_add)

            if len(constructs_list) == 1:
                dict_of_phrases['constructs'] = 'expressing ' + constructs_list[0]
            else:
                if len(constructs_list) > 1:
                    dict_of_phrases['constructs'] = 'expressing ' + \
                        ', '.join(map(str, constructs_list))

        if model_organism_donor_constructs is not None and len(model_organism_donor_constructs) > 0:
            constructs_list = []
            for c in model_organism_donor_constructs:
                constructObject = request.embed(c, '@@object')
                to_add = ''
                if 'target' in constructObject:
                    targetObject = request.embed(constructObject['target'], '@@object')
                    to_add += targetObject['name']

                if to_add != '':
                    constructs_list.append(to_add)

            if len(constructs_list) == 1:
                dict_of_phrases['model_organism_constructs'] = 'expressing ' + constructs_list[0]
            else:
                if len(constructs_list) > 1:
                    dict_of_phrases['model_organism_constructs'] = 'expressing ' + \
                        ', '.join(map(str, constructs_list))

        if rnais is not None and len(rnais) > 0:
            rnais_list = []
            for r in rnais:
                rnaiObject = request.embed(r, '@@object')
                to_add = ''
                if 'rnai_type' in rnaiObject:
                    to_add += rnaiObject['rnai_type'] + ' '

                if 'target' in rnaiObject:
                    targetObject = request.embed(rnaiObject['target'], '@@object')
                    to_add += targetObject['name']

                if to_add != '':
                    rnais_list.append(to_add)

            dict_of_phrases['rnais'] = rnais_list

        summary_phrase = ''

        if 'organism_name' in dict_of_phrases:
            summary_phrase += dict_of_phrases['organism_name']

        if 'strain_name' in dict_of_phrases:
            summary_phrase += ' (' + dict_of_phrases['strain_name'] + ')'

        term_name = ''

        if 'sample_term_name' in dict_of_phrases:
            if dict_of_phrases['sample_term_name'] != 'multi-cellular organism':
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

        summary_phrase += ' ' + term_phrase

        if 'phase' in dict_of_phrases:
            summary_phrase += ' at ' + dict_of_phrases['phase']

        if 'fractionated' in dict_of_phrases:
            summary_phrase += ' ' + dict_of_phrases['fractionated']

        if ('sample_type' in dict_of_phrases and
            dict_of_phrases['sample_type'] != 'immortalized cell line') or \
           ('sample_type' not in dict_of_phrases):
            if 'sex' in dict_of_phrases:
                if dict_of_phrases['sex'] == 'mixed':
                    summary_phrase += ' ' + dict_of_phrases['sex'] + ' sex'
                else:
                    summary_phrase += ' ' + dict_of_phrases['sex']

            stage_phrase = ''
            if 'life_stage' in dict_of_phrases:
                stage_phrase += ' ' + dict_of_phrases['life_stage']

            summary_phrase += stage_phrase.replace("embryonic", "embryo")

            if 'age_display' in dict_of_phrases:
                summary_phrase += ' (' + dict_of_phrases['age_display'] + ')'
            else:
                if 'synchronization' in dict_of_phrases:
                    summary_phrase += ' (' + dict_of_phrases['synchronization'] + ')'
                #else:
                #    summary_phrase += ''

        if 'derived_from' in dict_of_phrases:
            summary_phrase += ' ' + dict_of_phrases['derived_from']

        if 'transfection' in dict_of_phrases and 'rnais' in dict_of_phrases:
            if len(dict_of_phrases['rnais']) == 1:
                summary_phrase += ' ' + dict_of_phrases['transfection'] + ' RNAi knockdown ' + \
                    dict_of_phrases['rnais'][0]
            else:
                if len(dict_of_phrases['rnais']) > 1:
                    summary_phrase += dict_of_phrases['transfection'] + ' RNAi knockdown ' + \
                        ', '.join(map(str, dict_of_phrases['rnais']))

        if 'treatments' in dict_of_phrases:
            if len(dict_of_phrases['treatments']) == 1:
                summary_phrase += ' treated with '+dict_of_phrases['treatments'][0]
            else:
                if len(dict_of_phrases['treatments']) > 1:
                    summary_phrase += ' treated with ' + \
                                      ', '.join(map(str, dict_of_phrases['treatments']))

        # need to rephrase later on I guess
        if 'depleted_in' in dict_of_phrases:
            summary_phrase += ' ' + dict_of_phrases['depleted_in']

        if 'talens' in dict_of_phrases:
            summary_phrase += ' ' + dict_of_phrases['talens']

        if 'constructs' in dict_of_phrases:
            summary_phrase += ' ' + dict_of_phrases['constructs']
        if 'model_organism_constructs' in dict_of_phrases:
            summary_phrase += ' ' + dict_of_phrases['model_organism_constructs']

        if summary_phrase.strip()[-1] == ';':
            return summary_phrase.strip()[:-1]  # , str(dict_of_phrases))
        else:
            return summary_phrase.strip()
