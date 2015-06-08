import pytest


def remote_user_testapp(app, remote_user):
    from webtest import TestApp
    environ = {
        'HTTP_ACCEPT': 'application/json',
        'REMOTE_USER': str(remote_user),
    }
    return TestApp(app, environ)


@pytest.fixture
def other_lab(testapp):
    item = {
        'title': 'Other lab',
        'name': 'other-lab',
    }
    return testapp.post_json('/lab', item, status=201).json['@graph'][0]


@pytest.fixture
def wrangler_testapp(wrangler, app, external_tx, zsa_savepoints):
    return remote_user_testapp(app, wrangler['uuid'])


@pytest.fixture
def submitter_testapp(submitter, app, external_tx, zsa_savepoints):
    return remote_user_testapp(app, submitter['uuid'])


@pytest.fixture
def viewing_group_member_testapp(viewing_group_member, app, external_tx, zsa_savepoints):
    return remote_user_testapp(app, viewing_group_member['uuid'])


@pytest.fixture
def remc_member_testapp(remc_member, app, external_tx, zsa_savepoints):
    return remote_user_testapp(app, remc_member['uuid'])


@pytest.fixture
def indexer_testapp(app, external_tx, zsa_savepoints):
    return remote_user_testapp(app, 'INDEXER')


def test_wrangler_post_non_lab_collection(wrangler_testapp):
    item = {
        'name': 'human',
        'scientific_name': 'Homo sapiens',
        'taxon_id': '9606',
    }
    return wrangler_testapp.post_json('/organism', item, status=201)


def test_submitter_post_non_lab_collection(submitter_testapp):
    item = {
        'name': 'human',
        'scientific_name': 'Homo sapiens',
        'taxon_id': '9606',
    }
    return submitter_testapp.post_json('/organism', item, status=403)


def test_submitter_post_update_experiment(submitter_testapp, lab, award):
    experiment = {'lab': lab['@id'], 'award': award['@id']}
    res = submitter_testapp.post_json('/experiment', experiment, status=201)
    location = res.location
    res = submitter_testapp.get(location + '@@testing-allowed?permission=edit', status=200)
    assert res.json['has_permission'] is True
    assert 'submits_for.%s' % lab['uuid'] in res.json['principals_allowed_by_permission']
    submitter_testapp.patch_json(location, {'description': 'My experiment'}, status=200)


def test_submitter_post_other_lab(submitter_testapp, other_lab, award):
    experiment = {'lab': other_lab['@id'], 'award': award['@id']}
    res = submitter_testapp.post_json('/experiment', experiment, status=422)
    assert "not in user submits_for" in res.json['errors'][0]['description']


def test_wrangler_post_other_lab(wrangler_testapp, other_lab, award):
    experiment = {'lab': other_lab['@id'], 'award': award['@id']}
    wrangler_testapp.post_json('/experiment', experiment, status=201)


def test_users_view_details_admin(submitter, testapp):
    res = testapp.get(submitter['@id'] + '@@details')
    assert 'email' in res.json


def test_users_view_details_self(submitter, submitter_testapp):
    res = submitter_testapp.get(submitter['@id'] + '@@details')
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


def test_viewing_group_member_view(viewing_group_member_testapp, experiment):
    viewing_group_member_testapp.get(experiment['@id'], status=200)


def test_remc_member_view_disallowed(remc_member_testapp, experiment):
    remc_member_testapp.get(experiment['@id'], status=403)


def test_remc_member_view_shared(remc_member_testapp, mouse_donor):
    remc_member_testapp.get(mouse_donor['@id'], status=200)
