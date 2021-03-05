from snovault import upgrade_step


@upgrade_step('tissue', '1', '2')
@upgrade_step('cell_culture', '1', '2')
@upgrade_step('organoid', '1', '2')
def biosample_1_2(value, system):
	if 'url' in value:
		value['urls'] = [value['url']]
		del value['url']
