import pytest


@pytest.fixture
def base_analysis(testapp, experiment):
    return testapp.post_json(
        '/analyses',
        {'dataset': experiment['@id']},
        status=201
    ).json['@graph'][0]


@pytest.fixture
def base_pipeline(testapp, award, lab):
    pipeline = {
        'title': 'Test pipeline',
        'award': award['@id'],
        'lab': lab['@id'],
    }
    return testapp.post_json('/pipelines', pipeline, status=201).json['@graph'][0]


@pytest.fixture
def base_analysis_step(testapp):
    analysis_step = {
        'step_label': 'do-thing-step',
        'major_version': 1,
        'title': 'Do The Thing Step By Step',
        'analysis_step_types': ["QA calculation"],
        'input_file_types':  ['raw data']
    }
    return testapp.post_json('/analysis-steps', analysis_step, status=201).json['@graph'][0]


def test_audit_mismatch_pipeline(testapp, award, lab, base_analysis,
                                 base_pipeline, base_analysis_step):
    software = {
        'name': 'do-thing',
        'description': 'It does the thing',
        'title': 'THING_DOER',
        'award': award['@id'],
        'lab': lab['@id']
    }
    sw = testapp.post_json('/software', software, status=201).json['@graph'][0]

    software_version = {
        'version': '0.1',
        'software': sw['@id']
    }
    swv = testapp.post_json(
        '/software-versions',
        software_version,
        status=201
    ).json['@graph'][0]

    analysis_step_version = {
        'software_versions': [swv['@id']],
        'analysis_step':  base_analysis_step['@id'],
        'minor_version': 1
    }
    asv = testapp.post_json(
        '/analysis-step-versions',
        analysis_step_version,
        status=201
    ).json['@graph'][0]

    analysis_step_run = {
        'analysis_step_version': asv['@id'],
        'analysis': base_analysis['@id'],
        'status': "released"
    }
    testapp.post_json(
        '/analysis-step-runs',
        analysis_step_run,
        status=201
    ).json['@graph'][0]

    # The pipeline property is optional for analysis object. No audit check if
    # pipeline is not specified.
    res = testapp.get(base_analysis['@id'] + '@@index-data')
    errors = res.json['audit']
    errors_list = []
    for error_type in errors:
        errors_list.extend(errors[error_type])
    assert all(error['category'] != 'mismatch pipeline' for error in errors_list)

    # Will show mismatch even when pipeline doesn't have defined analysis_step.
    testapp.patch_json(base_analysis['@id'], {'pipeline': base_pipeline['@id']})
    res = testapp.get(base_analysis['@id'] + '@@index-data')
    errors = res.json['audit']
    errors_list = []
    for error_type in errors:
        errors_list.extend(errors[error_type])
    assert any(error['category'] == 'mismatch pipeline' for error in errors_list)

    testapp.patch_json(base_pipeline['@id'], {'analysis_steps': [base_analysis_step['@id']]})
    res = testapp.get(base_analysis['@id'] + '@@index-data')
    errors = res.json['audit']
    errors_list = []
    for error_type in errors:
        errors_list.extend(errors[error_type])
    assert all(error['category'] != 'mismatch pipeline' for error in errors_list)
