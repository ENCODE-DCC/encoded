from snovault import upgrade_step


@upgrade_step('human_postnatal_donor', '1', '2')
def human_postnatal_donor_1_2(value, system):
	if 'family_history_breast_cancer' in value:
		value['family_members_history_breast_cancer'] = value['family_history_breast_cancer']
		del value['family_history_breast_cancer']


@upgrade_step('human_postnatal_donor', '2', '3')
def human_postnatal_donor_2_3(value, system):
	if 'height' in value:
		value['height'] = str(value['height'])
	if 'body_mass_index' in value:
		value['body_mass_index'] = str(value['body_mass_index'])
