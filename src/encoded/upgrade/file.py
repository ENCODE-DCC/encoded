from snovault import upgrade_step


@upgrade_step('raw_sequence_file', '1', '2')
@upgrade_step('sequence_alignment_file', '1', '2')
def analysis_file_1_2(value, system):
	if 'award' in value:
		del value['award']
