from snovault import upgrade_step


@upgrade_step('suspension', '1', '2')
def suspension_1_2(value, system):
	if 'biosample_ontology' in value:
		del value['biosample_ontology']
