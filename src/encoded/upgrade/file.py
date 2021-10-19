from snovault import upgrade_step


@upgrade_step('raw_sequence_file', '1', '2')
@upgrade_step('sequence_alignment_file', '1', '2')
def analysis_file_1_2(value, system):
	if 'award' in value:
		del value['award']


@upgrade_step('processed_matrix_file', '3', '4')
def processed_matrix_file_3_4(value, system):
	if 'assembly' in value:
		del value['assembly']
	if 'genome_annotation' in value:
		del value['genome_annotation']


@upgrade_step('processed_matrix_file', '4', '5')
def processed_matrix_file_4_5(value, system):
	if 'layers' in value:
		for l in value['layers']:
			l['is_primary_data'] = True


@upgrade_step('processed_matrix_file', '5', '6')
def processed_matrix_file_5_6(value, system):
	if 'layers' in value:
		primary_value = value['layers'][0]['is_primary_data']
		value['is_primary_data'] = primary_value
