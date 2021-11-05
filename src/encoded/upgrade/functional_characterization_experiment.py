from snovault import upgrade_step


@upgrade_step('functional_characterization_experiment', '2', '3')
def functional_characterization_experiment_2_3(value, system):
    # http://encodedcc.atlassian.net/browse/ENCD-5081
    if value['assay_term_name'] == 'pooled clone sequencing' and 'plasmids_library_type' not in value:
        value['plasmids_library_type'] = 'other'


@upgrade_step('functional_characterization_experiment', '4', '5')
def functional_characterization_experiment_4_5(value, system):
    if 'biosample_ontology' not in value:
        value['biosample_ontology'] = '09e6c39a-92af-41fc-a535-7a86d5e9590a'


@upgrade_step('functional_characterization_experiment', '5', '6')
def functional_characterization_experiment_5_6(value, system):
    # https://encodedcc.atlassian.net/browse/ENCD-5303
    lib_type = value.get('plasmids_library_type', None)
    notes = value.get('notes', '')

    if lib_type == 'other':
        value['plasmids_library_type'] = 'elements cloning'
        value['notes'] = (notes + ' The plasmids_library_type of this pooled clone sequencing experiment needs to be checked as it was automatically upgraded by ENCD-5303.').strip()
    return


@upgrade_step('functional_characterization_experiment', '7', '8')
def functional_characterization_experiment_7_8(value, system):
    if 'examined_loci' in value:
        for locus in value['examined_loci']:
            if 'expression_measurement_method' in locus:
                if locus['expression_measurement_method'] == 'HCR-FlowFish':
                    locus['expression_measurement_method'] = 'HCR-FlowFISH'


@upgrade_step('functional_characterization_experiment', '8', '9')
def functional_characterization_experiment_8_9(value, system):
    if 'elements_mapping' in value:
        value['elements_mappings'] = [value['elements_mapping']]
        value.pop('elements_mapping')


@upgrade_step('functional_characterization_experiment', '9', '10')
def functional_characterization_experiment_9_10(value, system):
    if value.get('assay_term_name', "") == "pooled clone sequencing" and "control_type" not in value:
        value['control_type'] = "control"


@upgrade_step('functional_characterization_experiment', '10', '11')
def functional_characterization_experiment_10_11(value, system):
    if 'examined_loci' in value:
        for locus in value['examined_loci']:
            if 'expression_measurement_method' in locus:
                if locus['expression_measurement_method'] == 'CRISPRi-FlowFISH':
                    locus['expression_measurement_method'] = 'PrimeFlow'
            else:
                gene = locus['gene']
                locus['expression_measurement_method'] = 'qPCR'
                if 'notes' in value:
                    value['notes'] = f'{value.get("notes")} Upgraded expression_measurement_method to qPCR for examined_loci gene {gene}.'
                else:
                    value['notes'] = f'Upgraded expression_measurement_method to qPCR for examined_loci gene {gene}.'


@upgrade_step('functional_characterization_experiment', '11', '12')
def functional_characterization_experiment_11_12(value, system):
    convert_name = {
        'HCR-FlowFISH': 'Flow-FISH CRISPR screen',
        'PrimeFlow': 'Flow-FISH CRISPR screen',
        'antibody Sort-seq': 'FACS CRISPR screen',
        'endogenous protein Sort-seq': 'FACS CRISPR screen',
        'magnetic separation Sort-seq': 'FACS CRISPR screen',
        'fluorescence activated cell sorting': 'FACS CRISPR screen',
        'qPCR': 'FACS CRISPR screen'
    }
    convert_id = {
        'FACS CRISPR screen': 'NTR:0000658',
        'Flow-FISH CRISPR screen': 'NTR:0000659'
    }
    if value.get('assay_term_name', "") == 'CRISPR screen':
        if value.get('examined_loci') == None  or value.get('examined_loci') == []:
            value['assay_term_name'] = 'proliferation CRISPR screen'
            value['assay_term_id'] = 'NTR:0000657'
        else:
            methods = []
            for locus in value['examined_loci']:
                if 'expression_measurement_method' in locus:
                    methods.append(locus['expression_measurement_method'])
            if len(set(methods)) == 1 and (str(methods[0]) in convert_name):
                    value['assay_term_name'] = convert_name[str(methods[0])]
                    value['assay_term_id'] = convert_id[value['assay_term_name']]