from snovault import upgrade_step


@upgrade_step('antibody_lot', '1', '2')
def antibody_lot_1_2(value, system):
	if 'target' in value:
		value['targets'] = [value['target']]
		del value['target']
