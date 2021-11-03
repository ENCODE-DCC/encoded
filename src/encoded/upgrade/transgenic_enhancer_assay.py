from snovault import upgrade_step


@upgrade_step('transgenic_enhancer_experiment', '1', '2')
def transgenic_enhancer_experiment_1_2(value, system):
    value['assay_term_name'] = 'enhancer reporter assay'
    value['assay_term_id'] = 'OBI:0002083'
