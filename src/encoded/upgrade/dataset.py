from snovault import upgrade_step


@upgrade_step('dataset', '1', '2')
def dataset_1_2(value, system):
	if 'corresponding_contributor' in value:
		value['corresponding_contributors'] = [value['corresponding_contributor']]
		del value['corresponding_contributor']
