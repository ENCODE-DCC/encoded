import pytest


def _remote_user_testapp(app, remote_user):
    from webtest import TestApp
    environ = {
        'HTTP_ACCEPT': 'application/json',
        'REMOTE_USER': str(remote_user),
    }
    return TestApp(app, environ)


@pytest.fixture
def remote_user_testapp(app, remote_user):
    return _remote_user_testapp(app, remote_user)


@pytest.fixture
def wrangler_testapp(wrangler, app, external_tx, zsa_savepoints):
    return _remote_user_testapp(app, wrangler['uuid'])


@pytest.fixture
def submitter_testapp(submitter, app, external_tx, zsa_savepoints):
    return _remote_user_testapp(app, submitter['uuid'])


@pytest.fixture
def viewing_group_member_testapp(viewing_group_member, app, external_tx, zsa_savepoints):
    return _remote_user_testapp(app, viewing_group_member['uuid'])


@pytest.fixture
def indexer_testapp(app, external_tx, zsa_savepoints):
    return _remote_user_testapp(app, 'INDEXER')


def test_wrangler_post_non_lab_collection(wrangler_testapp):
    item = {
        'name': 'human',
        'scientific_name': 'Homo sapiens',
        'ncbi_taxon_id': '9606',
    }
    return wrangler_testapp.post_json('/organism', item, status=201)


def test_submitter_post_non_lab_collection(submitter_testapp):
    item = {
        'name': 'human',
        'scientific_name': 'Homo sapiens',
        'ncbi_taxon_id': '9606',
    }
    return submitter_testapp.post_json('/organism', item, status=403)


def test_wrangler_post_lab_base(wrangler_testapp, award_base):
    dataset = {'award': award_base['@id']}
    wrangler_testapp.post_json('/dataset', dataset, status=201)


def test_user_view_details_admin(submitter, access_key_2, testapp):
    res = testapp.get(submitter['@id'])
    assert 'email' in res.json
    assert 'access_keys' in res.json
    assert 'access_key_id' in res.json['access_keys'][0]


def test_users_view_details_self(submitter, access_key_2, submitter_testapp):
    res = submitter_testapp.get(submitter['@id'])
    assert 'email' in res.json
    assert 'access_keys' in res.json
    assert 'access_key_id' in res.json['access_keys'][0]


def test_users_patch_self(submitter, access_key, submitter_testapp):
    submitter_testapp.patch_json(submitter['@id'], {})


def test_users_post_disallowed(submitter, access_key, submitter_testapp):
    item = {
        'first_name': 'ENCODE',
        'last_name': 'Submitter2',
        'email': 'encode_submitter2@example.org',
    }
    submitter_testapp.post_json('/user', item, status=403)


def test_users_view_basic_indexer(submitter, indexer_testapp):
    res = indexer_testapp.get(submitter['@id'])
    assert 'title' in res.json
    assert 'email' not in res.json
    assert 'access_keys' not in res.json


def test_viewing_group_member_view(viewing_group_member_testapp, dataset_base):
    viewing_group_member_testapp.get(dataset_base['@id'], status=200)


def test_submitter_patch_lab_disallowed(submitter, lab_base, submitter_testapp):
    res = submitter_testapp.get(submitter['@id'])
    lab = {'lab': lab_base['@id']}
    submitter_testapp.patch_json(res.json['@id'], lab, status=422)  # is that the right status?


def test_wrangler_patch_lab_allowed(submitter, lab_base, wrangler_testapp):
    res = wrangler_testapp.get(submitter['@id'])
    lab = {'lab': lab_base['@id']}
    wrangler_testapp.patch_json(res.json['@id'], lab, status=200)


def test_submitter_patch_submits_for_disallowed(submitter, lab_base, submitter_testapp):
    res = submitter_testapp.get(submitter['@id'])
    submits_for = {'submits_for': res.json['submits_for'] + [lab_base['@id']]}
    submitter_testapp.patch_json(res.json['@id'], submits_for, status=422)


def test_disabled_user_denied_authenticated(authenticated_testapp, disabled_user):
    authenticated_testapp.get(disabled_user['@id'], status=403)


def test_disabled_user_denied_submitter(submitter_testapp, disabled_user):
    submitter_testapp.get(disabled_user['@id'], status=403)


def test_disabled_user_wrangler(wrangler_testapp, disabled_user):
    wrangler_testapp.get(disabled_user['@id'], status=200)


def test_labs_view_wrangler(wrangler_testapp, lab_base):
    labs = wrangler_testapp.get('/labs/', status=200)
    assert(len(labs.json['@graph']) == 1)


def test_experiment_submitter_no_edit_status(submitter_testapp, lab_base, award_base, dataset_base):
    submitter_testapp.patch_json(dataset_base['@id'], {'status': 'submitted'}, status=422)
