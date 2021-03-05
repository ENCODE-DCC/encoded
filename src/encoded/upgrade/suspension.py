from snovault import upgrade_step


@upgrade_step('suspension', '1', '2')
def suspension_1_2(value, system):
	if 'biosample_ontology' in value:
		del value['biosample_ontology']

@upgrade_step('suspension', '2', '3')
def suspension_2_3(value, system):
	if 'url' in value:
		value['urls'] = [value['url']]
		del value['url']
