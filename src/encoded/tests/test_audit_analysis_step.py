import pytest


def test_audit_analysis_step_multiple_pipelines(testapp, analysis_step_bam, pipeline_chip_encode4, pipeline_short_rna, remc_award, remc_lab):

	testapp.patch_json(pipeline_chip_encode4['@id'], {'analysis_steps': [analysis_step_bam['@id']]})
	res = testapp.get(analysis_step_bam['@id'] + '@@index-data')
	errors = res.json['audit']
	errors_list = []
	for error_type in errors:
		errors_list.extend(errors[error_type])
	assert 'analysis step used by multiple pipelines' not in (error['category']
            for error in errors_list)

	testapp.patch_json(pipeline_chip_encode4['@id'], {'award': remc_award['@id'], 'lab': remc_lab['@id']})
	res = testapp.get(analysis_step_bam['@id'] + '@@index-data')
	errors = res.json['audit']
	errors_list = []
	for error_type in errors:
		errors_list.extend(errors[error_type])
	assert any(error['category'] ==
		'analysis step used by multiple pipelines' for error in errors_list)
