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
    # https://encodedcc.atlassian.net/browse/ENCD-5911
    notes = value.get('notes', '')
    if value['assay_term_name'] == 'CRISPR screen' and 'examined_loci' not in value:
        value['proliferation_screen'] = True
        value['notes'] = (notes + ' The proliferation_screen property should be verified; it was automatically added by ENCD-5911 upgrade.').strip()
