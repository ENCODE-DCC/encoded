from snovault import (
    AuditFailure,
    audit_checker,
)
from .formatter import (
    audit_link,
    path_to_text,
)


def generate_formatted_list_of_experiments(list_of_experiments):
	if len(list_of_experiments) < 3:
		formatted_list = ' and '.join([audit_link(path_to_text(item),item) for item in list_of_experiments])
	else:
		formatted_list = '{}, and {}'.format(
			', '.join([audit_link(path_to_text(item),item) for item in list_of_experiments[0:-1]]),
			audit_link(path_to_text(list_of_experiments[-1]),list_of_experiments[-1])
			)
	return formatted_list


@audit_checker('ExperimentSeries', frame=['related_datasets',
                                          'related_datasets.replicates',
                                          'related_datasets.replicates.library',
                                          'related_datasets.replicates.library.biosample',
                                          'related_datasets.replicates.library.biosample.treatments',
                                          ])
def audit_mismatched_properties(value, system):
	excluded_statuses = ['deleted', 'replaced', 'revoked']
	assays = dict()
	biosample_types = dict()
	targets = {'no target': []}
	donors = dict()
	treatments = {'no treatment': []}
	genetic_modifications = {'no genetic modification': []}

	filtered_datasets = [dataset for dataset in value['related_datasets'] if dataset['status'] not in excluded_statuses]

	for dataset in filtered_datasets:
		if dataset['assay_title'] in assays:
			assays[dataset['assay_title']].append(dataset['@id'])
		else:
			assays[dataset['assay_title']] = [dataset['@id']]

		if dataset['biosample_ontology'] in biosample_types:
			biosample_types[dataset['biosample_ontology']].append(dataset['@id'])
		else:
			biosample_types[dataset['biosample_ontology']] = [dataset['@id']]

		if 'target' not in dataset:
			targets['no target'].append(dataset['@id'])
		else:
			if dataset['target'] in targets:
				targets[dataset['target']].append(dataset['@id'])
			else:
				targets[dataset['target']] = [dataset['@id']]	

		if 'replicates' in dataset:
			for replicate in dataset['replicates']:
				if replicate['status'] not in ['deleted'] and \
				'library' in replicate and 'biosample' in replicate['library']:
					biosample = replicate['library']['biosample']
					if 'donor' in biosample:
						if biosample['donor'] in donors:
							donors[biosample['donor']].append(dataset['@id'])
						else:
							donors[biosample['donor']] = [dataset['@id']]

					if not biosample['treatments']:
						treatments['no treatment'].append(dataset['@id'])
					else:
						treatments_combined = ', '.join(
							sorted([treatment['treatment_term_name'] for treatment in biosample['treatments']]))
						if treatments_combined in treatments:
							treatments[treatments_combined].append(dataset['@id'])
						else:
							treatments[treatments_combined] = [dataset['@id']]
						
					if not biosample['genetic_modifications']: 
						genetic_modifications['no genetic modification'].append(dataset['@id'])
					else:
						gm_combined = ', '.join(sorted(biosample['genetic_modifications']))
						if gm_combined in genetic_modifications:
							genetic_modifications[gm_combined].append(dataset['@id'])
						else:
							genetic_modifications[gm_combined] = [dataset['@id']]

	# Remove unused keys.
	if len(targets['no target']) == 0:
		targets.pop('no target')
	if len(treatments['no treatment']) == 0:
		treatments.pop('no treatment')
	if len(genetic_modifications['no genetic modification']) == 0:
		genetic_modifications.pop('no genetic modification')

	if len(assays) > 1:
		detail = 'Experiment series {} contains mismatched assays.'.format(
			audit_link(path_to_text(value['@id']),value['@id']))
		for assay_type in assays:
			expt_list = generate_formatted_list_of_experiments(assays[assay_type])
			detail = '{} Experiments {} are {} assays.'.format(
				detail,
				expt_list,
				assay_type
				)
		yield AuditFailure('Mismatched assays', detail, level='WARNING')

	if len(biosample_types) > 1:
		detail = 'Experiment series {} contains experiments on mismatched biosamples.'.format(
			audit_link(path_to_text(value['@id']),value['@id']))
		for biosample_type in biosample_types:
			expt_list = generate_formatted_list_of_experiments(biosample_types[biosample_type])
			detail = '{} Biosamples of Experiments {} are {}.'.format(
				detail,
				expt_list,
				audit_link(path_to_text(biosample_type),biosample_type)
				)
		yield AuditFailure('Mismatched biosamples', detail, level='WARNING')

	if len(targets) > 1:
		detail = 'Experiment series {} contains experiments with mismatched targets.'.format(
			audit_link(path_to_text(value['@id']),value['@id']))
		for target in targets:
			expt_list = generate_formatted_list_of_experiments(targets[target])
			detail = '{} Experiments {} target {}.'.format(
				detail,
				expt_list,
				audit_link(path_to_text(target),target)
				)
		yield AuditFailure('Mismatched targets', detail, level='WARNING')

	if len(donors) > 1:
		detail = 'Experiment series {} contains experiments on biosamples from mismatched donors.'.format(
			audit_link(path_to_text(value['@id']),value['@id']))
		for donor_id_key in donors:
			expt_list = generate_formatted_list_of_experiments(donors[donor_id_key])
			detail = '{} Biosamples of Experiments {} are from donor {}.'.format(
				detail,
				expt_list,
				audit_link(path_to_text(donor_id_key),donor_id_key)
				)
		yield AuditFailure('Mismatched donors', detail, level='WARNING')

	if len(treatments) > 1: 
		detail = 'Experiment series {} contains experiments on biosamples with mismatched treatments.'.format(
			audit_link(path_to_text(value['@id']),value['@id']))
		for treatment_key in treatments:
			expt_list = generate_formatted_list_of_experiments(treatments[treatment_key])
			detail = '{} Biosamples of Experiments {} were treated with {}.'.format(
				detail,
				expt_list,
				treatment_key
				)
		yield AuditFailure('Mismatched biosample treatments', detail, level='WARNING')

	if len(genetic_modifications) > 1:
		detail = 'Experiment series {} contains experiments on biosamples with mismatched genetic modifications.'.format(
			audit_link(path_to_text(value['@id']),value['@id']))
		for gm_key in genetic_modifications:
			expt_list = generate_formatted_list_of_experiments(genetic_modifications[gm_key])
			detail = '{} Biosamples of Experiments {} were modified by {}.'.format(
				detail,
				expt_list,
				gm_key
				)
		yield AuditFailure('Mismatched genetic modifications', detail, level='WARNING') #this text doesn't make sense for unmodified
	return
