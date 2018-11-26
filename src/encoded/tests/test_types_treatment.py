import pytest


@pytest.fixture
def treatment():
    return {
        'treatment_type': 'chemical',
        'treatment_term_name': 'estradiol',
        'treatment_term_id': 'CHEBI:23965'
    }


@pytest.fixture
def submitter_treatment(submitter, lab):
    return {
        'treatment_type': 'chemical',
        'treatment_term_name': 'estradiol',
        'treatment_term_id': 'CHEBI:23965',
        'submitted_by': submitter['@id']
    }


def test_admin_allowed_add_treatment(testapp, treatment):
    testapp.post_json('/treatments/', treatment, status=201)


def test_submitter_denied_add_treatment(submitter_testapp, treatment):
    submitter_testapp.post_json('/treatments/', treatment, status=403)


def test_admin_allowed_add_submitter_treatment(testapp, submitter_treatment):
    testapp.post_json('/treatments/', submitter_treatment, status=201)


def test_submitter_denied_add_submitter_treatment(submitter_testapp, submitter_treatment):
    submitter_testapp.post_json('/treatments/', submitter_treatment, status=422)


def test_admin_allowed_edit_submitter_treatment(submitter_treatment, testapp):
    res = testapp.post_json('/treatments/', submitter_treatment, status=201)
    testapp.patch_json(res.json['@graph'][0]['@id'], {'status': 'released'}, status=200)


def test_submitter_denied_edit_submitter_treatment(submitter_testapp, submitter_treatment, testapp):
    res = testapp.post_json('/treatments/', submitter_treatment, status=201)
    submitter_testapp.patch_json(res.json['@graph'][0]['@id'], {'status': 'released'}, status=403)
