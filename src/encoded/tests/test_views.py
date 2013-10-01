import pytest


def _type_length():
    # Not a fixture as we need to parameterize tests on this
    import os.path
    from ..loadxl import ORDER
    from pkg_resources import resource_filename
    inserts = resource_filename('encoded', 'tests/data/inserts/')
    lengths = {}
    for name in ORDER:
        with open(os.path.join(inserts, name + '.tsv'), 'U') as f:
            lengths[name] = len([l for l in f.readlines() if l.strip()]) - 1

    return lengths


TYPE_LENGTH = _type_length()


def test_home(htmltestapp):
    res = htmltestapp.get('/', status=200)
    assert res.body.startswith('<!DOCTYPE html>')


def test_home_json(testapp):
    res = testapp.get('/', status=200)
    assert res.json['@type']


@pytest.mark.parametrize('item_type', [k for k in TYPE_LENGTH if k != 'user'])
def test_html(htmltestapp, item_type):
    res = htmltestapp.get('/' + item_type).follow(status=200)
    assert res.body.startswith('<!DOCTYPE html>')


@pytest.mark.parametrize('item_type', TYPE_LENGTH)
def test_json(testapp, item_type):
    res = testapp.get('/' + item_type).follow(status=200)
    assert res.json['@type']


def test_json_basic_auth(htmltestapp):
    import base64
    url = '/'
    value = "Authorization: Basic %s" % base64.b64encode('nobody:pass')
    res = htmltestapp.get(url, headers={'Authorization': value}, status=200)
    assert res.json['@id']


def _test_antibody_approval_creation(testapp):
    from urlparse import urlparse
    new_antibody = {'foo': 'bar'}
    res = testapp.post_json('/antibodies/', new_antibody, status=201)
    assert res.location
    assert '/profiles/result' in res.json['@type']['profile']
    assert res.json['@graph'] == [{'href': urlparse(res.location).path}]
    res = testapp.get(res.location, status=200)
    assert '/profiles/antibody_approval' in res.json['@type']
    data = res.json
    for key in new_antibody:
        assert data[key] == new_antibody[key]
    res = testapp.get('/antibodies/', status=200)
    assert len(res.json['@graph']) == 1


@pytest.mark.xfail
def test_load_sample_data(testapp):
    from .sample_data import URL_COLLECTION
    for url, collection in URL_COLLECTION.iteritems():
        for item in collection:
            testapp.post_json(url, item, status=201)
        res = testapp.get(url + '?limit=all')
        assert len(res.json['@graph']) == len(collection)


@pytest.mark.slow
@pytest.mark.parametrize(('item_type', 'length'), TYPE_LENGTH.items())
def test_load_workbook(workbook, testapp, item_type, length):
    # testdata must come before testapp in the funcargs list for their
    # savepoints to be correctly ordered.
    res = testapp.get('/%s/?limit=all' % item_type).maybe_follow(status=200)
    assert len(res.json['@graph']) == length


@pytest.mark.slow
def test_collection_limit(workbook, testapp):
    res = testapp.get('/antibodies/?limit=2', status=200)
    assert len(res.json['@graph']) == 2


@pytest.mark.parametrize('url', ['/organisms/', '/sources/'])
def test_collection_post(testapp, url):
    from .sample_data import URL_COLLECTION
    collection = URL_COLLECTION[url]
    for item in collection:
        res = testapp.post_json(url, item, status=201)
        assert item['name'] in res.location


@pytest.mark.parametrize('url', ['/organisms/', '/sources/'])
def test_collection_post_bad_json(testapp, url):
    collection = [{'foo': 'bar'}]
    for item in collection:
        res = testapp.post_json(url, item, status=422)
        assert res.json['errors']


def test_actions_filtered_by_permission(testapp, anontestapp):
    from .sample_data import URL_COLLECTION
    url = '/sources/'
    collection = URL_COLLECTION[url]
    item = collection[0]
    res = testapp.post_json(url, item, status=201)
    location = res.location

    res = testapp.get(location)
    assert any(action for action in res.json['actions'] if action['name'] == 'edit')

    res = anontestapp.get(location)
    assert not any(action for action in res.json['actions'] if action['name'] == 'edit')


@pytest.mark.parametrize('url', ['/organisms/', '/sources/'])
def test_collection_put(testapp, url, execute_counter):
    from .sample_data import URL_COLLECTION
    collection = URL_COLLECTION[url]
    initial = collection[0]
    res = testapp.post_json(url, initial, status=201)
    item_url = res.json['@graph'][0]
    uuid = initial['uuid']

    with execute_counter.expect(2):
        res = testapp.get(item_url).json

    del initial['uuid']
    for key in initial:
        assert res[key] == initial[key]

    update = collection[1].copy()
    del update['uuid']
    testapp.put_json(item_url, update, status=200)

    with execute_counter.expect(4):
        res = testapp.get('/' + uuid).follow().json

    for key in update:
        assert res[key] == update[key]


# Error due to test savepoint setup
@pytest.mark.xfail
def test_post_duplicate_uuid(testapp):
    from .sample_data import BAD_LABS
    testapp.post_json('/labs/', BAD_LABS[0], status=201)
    testapp.post_json('/labs/', BAD_LABS[1], status=409)


def test_users_post(users, anontestapp):
    email = users[0]['email']
    res = anontestapp.get('/@@testing-user',
                          extra_environ={'REMOTE_USER': str(email)})
    assert sorted(res.json['effective_principals']) == [
        'lab:2c334112-288e-4d45-9154-3f404c726daf',
        'remoteuser:%s' % email,
        'submits_for:2c334112-288e-4d45-9154-3f404c726daf',
        'system.Authenticated',
        'system.Everyone',
        'userid:e9be360e-d1c7-4cae-9b3a-caf588e8bb6f',
    ]


def test_users_view_details_admin(users, testapp):
    res = testapp.get(users[0]['@id'])
    assert 'email' in res.json


def test_users_view_basic_anon(users, anontestapp):
    res = anontestapp.get(users[0]['@id'])
    assert 'title' in res.json
    assert 'email' not in res.json


def test_users_list_denied_anon(anontestapp):
    anontestapp.get('/users/', status=403)


def test_etags(testapp):
    url = '/organisms/'
    from .sample_data import URL_COLLECTION
    collection = URL_COLLECTION[url]
    item = collection[0]
    res = testapp.post_json(url, item, status=201)
    res = testapp.get(url, status=200)
    etag = res.etag
    res = testapp.get(url, headers={'If-None-Match': etag}, status=304)
    item = collection[1]
    res = testapp.post_json(url, item, status=201)
    res = testapp.get(url, headers={'If-None-Match': etag}, status=200)
    assert res.etag != etag
