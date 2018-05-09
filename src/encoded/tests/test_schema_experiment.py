import pytest
from datetime import datetime


@pytest.fixture
def experiment_pipeline_error(testapp, lab, award):
    item = {
        'lab': lab['@id'],
        'award': award['@id'],
        'assay_term_name': 'ChIP-seq',
        'biosample_type': 'cell-free sample',
        'biosample_term_id': 'NTR:0000471',
        'biosample_term_name': 'none',
        'internal_status': 'pipeline error'
    }
    return item


@pytest.fixture
def experiment_no_error(testapp, lab, award):
    item = {
        'lab': lab['@id'],
        'award': award['@id'],
        'assay_term_name': 'ChIP-seq',
        'biosample_type': 'cell-free sample',
        'biosample_term_id': 'NTR:0000471',
        'biosample_term_name': 'none',
        'internal_status': 'release ready'
    }
    return item

@pytest.fixture
def matched_set(testapp, lab, award):
    item = {
        'lab': lab['@id'],
        'award': award['@id']
    }
    return item

def test_not_pipeline_error_without_message_ok(testapp, experiment_no_error):
    # internal_status != pipeline error, so an error detail message is not required.
    res = testapp.post_json('/experiment', experiment_no_error, expect_errors=False)
    assert res.status_code == 201


def test_pipeline_error_without_message_bad(testapp, experiment_pipeline_error):
    # internal_status == pipeline error, so an error detail message is required.
    res = testapp.post_json('/experiment', experiment_pipeline_error, expect_errors=True)
    assert res.status_code == 422


def test_pipeline_error_with_message_ok(testapp, experiment_pipeline_error):
    # internal_status == pipeline error and we have a message, yay!
    experiment_pipeline_error.update({'pipeline_error_detail': 'Pipeline says error'})
    res = testapp.post_json('/experiment', experiment_pipeline_error, expect_errors=False)
    assert res.status_code == 201


def test_not_pipeline_error_with_message_bad(testapp, experiment_no_error):
    # We shouldn't use the error detail property if internal_status != pipeline error
    experiment_no_error.update({'pipeline_error_detail': 'I am not the pipeline, I cannot use this.'})
    res = testapp.post_json('/experiment', experiment_no_error, expect_errors=True)
    assert res.status_code == 422


def test_bad_alias_namespace(testapp, experiment):
    experiment.update({'aliases': ['jobb-dekker:job not jobb', 'encode:these are bad:!%^#@[]']})
    res = testapp.post_json('/experiment', experiment, expect_errors=True)
    print(experiment)
    assert res.status_code == 422

def test_alt_accession_ENCSR_regex(testapp, experiment_no_error):
    expt = testapp.post_json('/experiment', experiment_no_error).json['@graph'][0]
    res = testapp.patch_json(expt['@id'], {'status': 'replaced', 'alternate_accessions': ['ENCAB123ABC']}, expect_errors=True)
    assert res.status_code == 422
    res = testapp.patch_json(expt['@id'], {'status': 'replaced', 'alternate_accessions': ['ENCSR123ABC']})
    assert res.status_code == 200

def test_submission_date(testapp, experiment_no_error):
    expt = testapp.post_json('/experiment', experiment_no_error).json['@graph'][0]
    res = testapp.patch_json(expt['@id'], {'date_submitted': '2000-10-10'}, expect_errors=True)
    assert res.status_code == 200


@pytest.mark.parametrize(
    'status',
    [
        'in progress',
        'submitted',
        'released',
        'archived',
        'deleted',
        'revoked'
    ]
)
def test_experiment_valid_statuses(status, testapp, experiment):
    # Need date_released for released/revoked experiment dependency.
    # Need date_submitted for submitted experiment dependency.
    testapp.patch_json(
        experiment['@id'],
        {'date_released': datetime.now().strftime('%Y-%m-%d'),
         'date_submitted': datetime.now().strftime('%Y-%m-%d')}
    )
    testapp.patch_json(experiment['@id'], {'status': status})
    res = testapp.get(experiment['@id'] + '@@embedded').json
    assert res['status'] == status


@pytest.mark.parametrize(
    'status',
    [
        'ready for review',
        'started'
    ]
)
def test_experiment_invalid_statuses(status, testapp, experiment):
    with pytest.raises(Exception):
        testapp.patch_json(experiment['@id'], {'status': status})


def test_experiment_submission_date_dependency(testapp, experiment_no_error):
    expt = testapp.post_json('/experiment', experiment_no_error).json['@graph'][0]
    testapp.patch_json(
        expt['@id'], {
        'status': 'submitted'},
        status=422)
    testapp.patch_json(
        expt['@id'], {
        'status': 'submitted',
        'date_submitted': '2000-10-10'},
        status=200)
    
def test_experiment_possible_controls(testapp, experiment_no_error, matched_set):
    expt = testapp.post_json('/experiment', experiment_no_error).json['@graph'][0]
    matched_set_control = testapp.post_json('/matched_set', matched_set).json['@graph'][0]
    testapp.patch_json(
        expt['@id'], {
        'possible_controls': [matched_set_control['@id']]},
        status=200)