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
