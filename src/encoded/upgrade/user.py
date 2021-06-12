from snovault import upgrade_step


@upgrade_step('user', '1', '2')
def user_1_2(value, system):
	if 'job_title' in value:
		value['job_title'] = value['job_title'].split(',')
