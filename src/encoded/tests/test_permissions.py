import pytest

@pytest.datafixture
def users(app):
    from webtest import TestApp
    environ = {
        'HTTP_ACCEPT': 'application/json',
        'REMOTE_USER': 'TEST',
    }
    testapp = TestApp(app, environ)

    from .sample_data import URL_COLLECTION
    url = '/labs/'
    for item in URL_COLLECTION[url]:
        res = testapp.post_json(url, item, status=201)

    url = '/awards/'
    for item in URL_COLLECTION[url]:
        res = testapp.post_json(url, item, status=201)

    url = '/users/'
    users = []
    for item in URL_COLLECTION[url]:
        res = testapp.post_json(url, item, status=201)
        users.append(res.json['@graph'][0])
    return users


@pytest.fixture
def wrangler(users, app, external_tx, zsa_savepoints):
    user = [u for u in users if 'wrangler' in u['groups']][0]
    from webtest import TestApp
    environ = {
        'HTTP_ACCEPT': 'application/json',
        'REMOTE_USER': str(user['uuid']),
    }
    return TestApp(app, environ)


@pytest.fixture
def submitter(users, app, external_tx, zsa_savepoints):
    user = [u for u in users if not u['groups']][0]
    from webtest import TestApp
    environ = {
        'HTTP_ACCEPT': 'application/json',
        'REMOTE_USER': str(user['uuid']),
    }
    return TestApp(app, environ)


@pytest.fixture
def lab():
    return 'b635b4ed-dba3-4672-ace9-11d76a8d03af'


@pytest.fixture
def award():
    return 'Myers'


@pytest.mark.parametrize('url', ['/organisms/', '/sources/'])
def test_wrangler_post_non_lab_collection(wrangler, url):
    from .sample_data import URL_COLLECTION
    collection = URL_COLLECTION[url]
    for item in collection:
        res = wrangler.post_json(url, item, status=201)
        assert item['name'] in res.location


@pytest.mark.parametrize('url', ['/organisms/', '/sources/'])
def test_submitter_post_non_lab_collection(submitter, url):
    from .sample_data import URL_COLLECTION
    collection = URL_COLLECTION[url]
    for item in collection:
        item = item.copy()
        del item['uuid']
        submitter.post_json(url, item, status=403)


def test_submitter_post_update_experiment(submitter, lab, award):
    experiment = {'lab': lab, 'award': award}
    res = submitter.post_json('/experiment/', experiment, status=201)
    location = res.location
    res = submitter.get(location + '@@testing-allowed?permission=edit', status=200)
    assert res.json['has_permission'] is True
    assert 'submits_for.%s' % lab in res.json['principals_allowed_by_permission']
    submitter.patch_json(location, {'description': 'My experiment'}, status=200)
