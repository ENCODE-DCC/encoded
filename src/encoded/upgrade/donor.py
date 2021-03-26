from snovault import upgrade_step


@upgrade_step('human_postnatal_donor', '1', '2')
def human_postnatal_donor_1_2(value, system):
	if 'family_history_breast_cancer' in value:
		value['family_members_history_breast_cancer'] = value['family_history_breast_cancer']
		del value['family_history_breast_cancer']
