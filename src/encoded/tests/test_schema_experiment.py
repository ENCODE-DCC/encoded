import pytest


@pytest.fixture
def experiment_pipeline_error(testapp, lab, award):
    item = {
        'lab': lab['@id'],
        'award': award['@id'],
        'assay_term_name': 'ChIP-seq',
        'internal_status': 'pipeline error'
    }
    return item


@pytest.fixture
def experiment_no_error(testapp, lab, award):
    item = {
        'lab': lab['@id'],
        'award': award['@id'],
        'assay_term_name': 'ChIP-seq',
        'biosample_type': 'in vitro sample',
        'internal_status': 'release ready'
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
