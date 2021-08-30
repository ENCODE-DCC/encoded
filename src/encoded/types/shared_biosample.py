from .biosample import generate_summary_dictionary

def biosample_summary_information(request, biosampleObject):
    drop_age_sex_flag = False
    add_classification_flag = False
    drop_originated_from_flag = False

    biosampleTypeObject = request.embed(biosampleObject['biosample_ontology'], '@@object')
    if biosampleTypeObject.get('classification') in ['in vitro differentiated cells']:
        drop_age_sex_flag = True
    if biosampleTypeObject.get('classification') in ['tissue', 'organoid']:
        add_classification_flag = True

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
    originated_from_ontology_object = None
    if 'originated_from' in biosampleObject:
        originated_from_object = request.embed(biosampleObject['originated_from'], '@@object')
        originated_from_ontology_object = request.embed(originated_from_object['biosample_ontology'], '@@object')
    if originated_from_ontology_object and biosampleTypeObject.get('term_name') == \
            originated_from_ontology_object.get('term_name'):
        drop_originated_from_flag = True

    modifications_list = None
    genetic_modifications = biosampleObject.get('applied_modifications')
    if genetic_modifications:
        modifications_list = []
        guides = ''
        for gm in genetic_modifications:
            gm_object = request.embed(gm, '@@object')
            if 'guide_type' in gm_object:
                guides = gm_object['guide_type']
        for gm in genetic_modifications:
            gm_object = request.embed(gm, '@@object')
            modification_dict = {'category': gm_object.get('category')}
            if gm_object.get('modified_site_by_target_id'):
                target = request.embed(gm_object.get('modified_site_by_target_id'),'@@object')
                if 'genes' in target:
                    genes = target['genes']
                    if len(genes) == 1:
                        gene_object = request.embed(''.join(str(gene) for gene in genes), '@@object?skip_calculated=true')
                        modification_dict['target_gene'] = gene_object.get('symbol')
                        modification_dict['organism'] = request.embed(gene_object['organism'], '@@object?skip_calculated=true').get('name')
                else:
                    modification_dict['target'] = target['label']
            if gm_object.get('introduced_tags_array'):
                modification_dict['tags'] = []
                for tag in gm_object.get('introduced_tags_array'):
                    tag_dict = {'location': tag['location']}
                    if tag.get('promoter_used'):
                        tag_dict['promoter'] = request.embed(tag.get('promoter_used'), '@@object').get['label']
                    modification_dict['tags'].append(tag_dict)
            if gm_object.get('introduced_gene'):
                gene_object = request.embed(gm_object['introduced_gene'], '@@object?skip_calculated=true')
                modification_dict['gene'] = gene_object.get('symbol')
                modification_dict['organism'] = request.embed(gene_object['organism'], '@@object?skip_calculated=true').get('name')
            if 'method' in gm_object:
                if (gm_object['method'] == 'CRISPR' and guides != ''):
                    entry = f'CRISPR ({guides})'
                    modifications_list.append((entry, modification_dict))
                else:
                    modifications_list.append((gm_object['method'], modification_dict))
            elif 'nucleic_acid_delivery_method' in gm_object:
                for item in gm_object['nucleic_acid_delivery_method']:
                    if (item == 'transduction' and 'MOI' in gm_object):
                        moi = gm_object['MOI']
                        entry = f'transduction ({moi} MOI)'
                        modifications_list.append((entry, modification_dict))
                    else:
                        modifications_list.append((item, modification_dict))

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
        biosampleObject.get('post_differentiation_time'),
        biosampleObject.get('post_differentiation_time_units'),
        biosampleObject.get('pulse_chase_time'),
        biosampleObject.get('pulse_chase_time_units'),
        treatment_objects_list,
        preservation_method,
        part_of_object,
        originated_from_object,
        modifications_list,
        True)

    return (dictionary_to_add, drop_age_sex_flag, add_classification_flag, drop_originated_from_flag)
