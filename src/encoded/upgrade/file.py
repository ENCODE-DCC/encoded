from snovault import upgrade_step


@upgrade_step('raw_sequence_file', '1', '2')
@upgrade_step('sequence_alignment_file', '1', '2')
@upgrade_step('matrix_file', '1', '2')
def analysis_file_1_2(value, system):
	if 'award' in value:
		del value['award']


@upgrade_step('matrix_file', '2', '3')
def matrix_file_2_3(value, system):
	properties = [
		'feature_counts',
		'value_scale',
		'value_units',
		'normalized',
		'normalization_method',
		'filtering_cutoffs'
	]
	temp = {}
	temp['label'] = 'raw'
	for prop in properties:
		if prop in value:
			temp[prop] = value[prop]
			del value[prop]
	value['layers'] = [temp]
