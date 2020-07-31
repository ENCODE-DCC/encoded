from .biosample import generate_summary_dictionary

def biosample_summary_information(request, biosampleObject):
    drop_age_sex_flag = False

    biosampleTypeObject = request.embed(biosampleObject['biosample_ontology'], '@@object')
    if biosampleTypeObject.get('classification') in ['in vitro differentiated cells']:
        drop_age_sex_flag = True

    organismObject = None
    if 'organism' in biosampleObject:
        organismObject = request.embed(biosampleObject['organism'], '@@object')

    donorObject = None
    if 'donor' in biosampleObject:
        donorObject = request.embed(biosampleObject['donor'], '@@object')

    treatment_objects_list = None
    treatments = biosampleObject.get('treatments')
    if treatments is not None and len(treatments) > 0:
        treatment_objects_list = []
        for t in treatments:
            treatment_objects_list.append(request.embed(t, '@@object'))

    part_of_object = None
    if 'part_of' in biosampleObject:
        part_of_object = request.embed(biosampleObject['part_of'], '@@object')

    originated_from_object = None
    if 'originated_from' in biosampleObject:
        originated_from_object = request.embed(biosampleObject['originated_from'], '@@object')

    modifications_list = None
    genetic_modifications = biosampleObject.get('applied_modifications')
    if genetic_modifications:
        modifications_list = []
        for gm in genetic_modifications:
            gm_object = request.embed(gm, '@@object')
            modification_dict = {'category': gm_object.get('category')}
            if gm_object.get('modified_site_by_target_id'):
                modification_dict['target'] = request.embed(gm_object.get('modified_site_by_target_id'), '@@object')['label']
            if gm_object.get('introduced_tags_array'):
                modification_dict['tags'] = []
                for tag in gm_object.get('introduced_tags_array'):
                    tag_dict = {'location': tag['location']}
                    if tag.get('promoter_used'):
                        tag_dict['promoter'] = request.embed(tag.get('promoter_used'), '@@object').get['label']
                    modification_dict['tags'].append(tag_dict)
            if 'method' in gm_object:
                modifications_list.append((gm_object['method'], modification_dict))
            elif 'nucleic_acid_delivery_method' in gm_object:
                if len(gm_object['nucleic_acid_delivery_method']) < 3:
                    delivery_methods = ' and '.join(gm_object['nucleic_acid_delivery_method'])
                else:
                    delivery_methods = ', '.join(gm_object['nucleic_acid_delivery_method'][:-1]) + ', and ' + gm_object['nucleic_acid_delivery_method'][-1]
                modifications_list.append((delivery_methods, modification_dict))

    preservation_method = None
    dictionary_to_add = generate_summary_dictionary(
        request,
        organismObject,
        donorObject,
        biosampleObject.get('age'),
        biosampleObject.get('age_units'),
        biosampleObject.get('life_stage'),
        biosampleObject.get('sex'),
        biosampleTypeObject.get('term_name'),
        biosampleTypeObject.get('classification'),
        biosampleObject.get('starting_amount'),
        biosampleObject.get('starting_amount_units'),
        biosampleObject.get('depleted_in_term_name'),
        biosampleObject.get('disease_term_name'),
        biosampleObject.get('phase'),
        biosampleObject.get('subcellular_fraction_term_name'),
        biosampleObject.get('synchronization'),
        biosampleObject.get('post_synchronization_time'),
        biosampleObject.get('post_synchronization_time_units'),
        biosampleObject.get('post_treatment_time'),
        biosampleObject.get('post_treatment_time_units'),
        biosampleObject.get('post_nucleic_acid_delivery_time'),
        biosampleObject.get('post_nucleic_acid_delivery_time_units'),
        treatment_objects_list,
        preservation_method,
        part_of_object,
        originated_from_object,
        modifications_list,
        True)

    return (dictionary_to_add, drop_age_sex_flag)
