import pytest


def remote_user_testapp(app, remote_user):
    from webtest import TestApp
    environ = {
        'HTTP_ACCEPT': 'application/json',
        'REMOTE_USER': str(remote_user),
    }
    return TestApp(app, environ)


@pytest.fixture
def wrangler_testapp(wrangler, app, external_tx, zsa_savepoints):
    return remote_user_testapp(app, wrangler['uuid'])


@pytest.fixture
def submitter_testapp(submitter, app, external_tx, zsa_savepoints):
    return remote_user_testapp(app, submitter['uuid'])


@pytest.fixture
def indexer_testapp(app, external_tx, zsa_savepoints):
    return remote_user_testapp(app, 'INDEXER')


@pytest.mark.parametrize('item_type', ['organism', 'source'])
def test_wrangler_post_non_lab_collection(wrangler_testapp, item_type):
    from . import sample_data
    sample_data.load(wrangler_testapp, item_type)


@pytest.mark.parametrize('item_type', ['organism', 'source'])
def test_submitter_post_non_lab_collection(submitter_testapp, item_type):
    from .sample_data import URL_COLLECTION
    item = URL_COLLECTION[item_type][0].copy()
    del item['uuid']
    submitter_testapp.post_json('/' + item_type, item, status=403)


def test_submitter_post_update_experiment(submitter_testapp, lab, award):
    experiment = {'lab': lab['@id'], 'award': award['@id']}
    res = submitter_testapp.post_json('/experiment', experiment, status=201)
    location = res.location
    res = submitter_testapp.get(location + '@@testing-allowed?permission=edit', status=200)
    assert res.json['has_permission'] is True
    assert 'submits_for.%s' % lab['uuid'] in res.json['principals_allowed_by_permission']
    submitter_testapp.patch_json(location, {'description': 'My experiment'}, status=200)


def test_users_view_details_admin(submitter, testapp):
    res = testapp.get(submitter['@id'])
    assert 'email' in res.json


def test_users_view_details_self(submitter, submitter_testapp):
    res = submitter_testapp.get(submitter['@id'])
    assert 'email' in res.json


def test_users_view_basic_authenticated(submitter, authenticated_testapp):
    res = authenticated_testapp.get(submitter['@id'])
    assert 'title' in res.json
    assert 'email' not in res.json


def test_users_view_basic_anon(submitter, anontestapp):
    res = anontestapp.get(submitter['@id'])
    assert 'title' in res.json
    assert 'email' not in res.json


def test_users_view_basic_indexer(submitter, indexer_testapp):
    res = indexer_testapp.get(submitter['@id'])
    assert 'title' in res.json
    assert 'email' not in res.json


def test_users_list_denied_authenticated(authenticated_testapp):
    authenticated_testapp.get('/users/', status=403)
