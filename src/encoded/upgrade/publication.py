from snovault import upgrade_step


@upgrade_step('publication', '1', '2')
def publication_1_2(value, system):
	if 'identifiers' in value:
		for i in value['identifiers']:
			path = i.split(':')
			if path[0] == 'doi':
				value['doi'] = path[1]
			elif path[0] == 'PMID':
				value['pmid'] = path[1]
		del value['identifiers']
