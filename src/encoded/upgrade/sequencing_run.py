from snovault import upgrade_step


@upgrade_step('sequencing_run', '1', '2')
def sequencing_run_1_2(value, system):
	if 'derived_from' in value:
		value['derived_from'] = [value['derived_from']]
