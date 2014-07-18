import pytest


def _type_length():
    # Not a fixture as we need to parameterize tests on this
    from ..loadxl import ORDER
    from pkg_resources import resource_stream
    import json
    return {
        name: len(json.load(resource_stream('encoded', 'tests/data/inserts/%s.json' % name)))
        for name in ORDER
    }


TYPE_LENGTH = _type_length()

PUBLIC_COLLECTIONS = [
    'source',
    'platform',
    'treatment',
    'lab',
    'award',
    'target',
    'organism',
]


def test_home(anonhtmltestapp):
    res = anonhtmltestapp.get('/', status=200)
    assert res.body.startswith('<!DOCTYPE html>')


def test_home_json(testapp):
    res = testapp.get('/', status=200)
    assert res.json['@type']


def test_vary_html(anonhtmltestapp):
    res = anonhtmltestapp.get('/', status=200)
    assert res.vary is not None
    assert 'Accept' in res.vary


def test_vary_json(anontestapp):
    res = anontestapp.get('/', status=200)
    assert res.vary is not None
    assert 'Accept' in res.vary


@pytest.mark.parametrize('item_type', [k for k in TYPE_LENGTH if k != 'user'])
def test_collections_anon(workbook, anontestapp, item_type):
    res = anontestapp.get('/' + item_type).follow(status=200)
    assert '@graph' in res.json


@pytest.mark.parametrize('item_type', [k for k in TYPE_LENGTH if k != 'user'])
def test_html_collections_anon(workbook, anonhtmltestapp, item_type):
    res = anonhtmltestapp.get('/' + item_type).follow(status=200)
    assert res.body.startswith('<!DOCTYPE html>')


@pytest.mark.parametrize('item_type', TYPE_LENGTH)
def test_html_collections(workbook, htmltestapp, item_type):
    res = htmltestapp.get('/' + item_type).follow(status=200)
    assert res.body.startswith('<!DOCTYPE html>')


@pytest.mark.slow
@pytest.mark.parametrize('item_type', TYPE_LENGTH)
def test_html_pages(workbook, testapp, htmltestapp, item_type):
    res = testapp.get('/%s?limit=all' % item_type).follow(status=200)
    for item in res.json['@graph']:
        res = htmltestapp.get(item['@id'])
        assert res.body.startswith('<!DOCTYPE html>')


@pytest.mark.slow
@pytest.mark.parametrize('item_type', [k for k in TYPE_LENGTH if k != 'user'])
def test_html_server_pages(workbook, item_type, server):
    from webtest import TestApp
    testapp = TestApp(server)
    res = testapp.get('/%s?limit=all' % item_type,
        headers={'Accept': 'application/json'},
    ).follow(
        status=200,
        headers={'Accept': 'application/json'},
    )
    for item in res.json['@graph']:
        res = testapp.get(item['@id'], status=200)
        assert res.body.startswith('<!DOCTYPE html>')
        assert 'Internal Server Error' not in res.body


@pytest.mark.parametrize('item_type', TYPE_LENGTH)
def test_json(testapp, item_type):
    res = testapp.get('/' + item_type).follow(status=200)
    assert res.json['@type']


def test_json_basic_auth(anonhtmltestapp):
    import base64
    url = '/'
    value = "Authorization: Basic %s" % base64.b64encode('nobody:pass')
    res = anonhtmltestapp.get(url, headers={'Authorization': value}, status=200)
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


def test_load_sample_data(testapp):
    from . import sample_data
    for item_type in sample_data.URL_COLLECTION:
        sample_data.load(testapp, item_type)


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


@pytest.mark.parametrize('item_type', ['organism', 'source'])
def test_collection_post(testapp, item_type):
    from . import sample_data
    sample_data.load(testapp, item_type)


@pytest.mark.parametrize('item_type', ['organism', 'source'])
def test_collection_post_bad_json(testapp, item_type):
    collection = [{'foo': 'bar'}]
    for item in collection:
        res = testapp.post_json('/' + item_type, item, status=422)
        assert res.json['errors']


def test_collection_post_malformed_json(testapp):
    item = '{'
    headers = {'Content-Type': 'application/json'}
    res = testapp.post('/organism', item, status=400, headers=headers)
    assert res.json['detail'].startswith('Expecting')


def test_collection_post_missing_content_type(testapp):
    item = '{}'
    testapp.post('/organism', item, status=415)


def test_collection_post_bad_(anontestapp):
    import base64
    value = "Authorization: Basic %s" % base64.b64encode('nobody:pass')
    anontestapp.post_json('/organism', {}, headers={'Authorization': value}, status=401)


def test_collection_actions_filtered_by_permission(workbook, testapp, anontestapp):
    res = testapp.get('/about/')
    assert any(action for action in res.json['actions'] if action['name'] == 'add')

    res = anontestapp.get('/about/')
    assert not any(action for action in res.json['actions'] if action['name'] == 'add')


def test_item_actions_filtered_by_permission(testapp, authenticated_testapp, sources):
    location = sources[0]['@id']

    res = testapp.get(location)
    assert any(action for action in res.json['actions'] if action['name'] == 'edit')

    res = authenticated_testapp.get(location)
    assert not any(action for action in res.json['actions'] if action['name'] == 'edit')


@pytest.mark.parametrize('item_type', ['organism', 'source'])
def test_collection_put(testapp, item_type, execute_counter):
    from .sample_data import URL_COLLECTION
    collection = URL_COLLECTION[item_type]
    initial = collection[0].copy()
    res = testapp.post_json('/' + item_type, initial, status=201)
    item_url = res.json['@graph'][0]['@id']
    uuid = initial['uuid']

    with execute_counter.expect(1):
        res = testapp.get(item_url).json

    for key in initial:
        assert res[key] == initial[key]

    update = collection[1].copy()
    del update['uuid']
    testapp.put_json(item_url, update, status=200)

    with execute_counter.expect(2):
        res = testapp.get('/' + uuid).follow().json

    for key in update:
        assert res[key] == update[key]


def test_post_duplicate_uuid(testapp):
    from .sample_data import BAD_LABS
    testapp.post_json('/labs/', BAD_LABS[0], status=201)
    testapp.post_json('/labs/', BAD_LABS[1], status=409)


def test_user_effective_principals(users, anontestapp, execute_counter):
    email = users[0]['email']
    with execute_counter.expect(1):
        res = anontestapp.get('/@@testing-user',
                              extra_environ={'REMOTE_USER': str(email)})
    assert sorted(res.json['effective_principals']) == [
        'group.admin',
        'group.programmer',
        'group.submitter',
        'lab.cfb789b8-46f3-4d59-a2b3-adc39e7df93a',
        'remoteuser.%s' % email,
        'submits_for.cfb789b8-46f3-4d59-a2b3-adc39e7df93a',
        'system.Authenticated',
        'system.Everyone',
        'userid.e9be360e-d1c7-4cae-9b3a-caf588e8bb6f',
    ]


def test_page_toplevel(workbook, anontestapp):
    res = anontestapp.get('/test-section/', status=200)
    assert res.json['@id'] == '/test-section/'

    res = anontestapp.get('/pages/test-section/', status=301)
    assert res.location == 'http://localhost/test-section/'


def test_page_nested(workbook, anontestapp):
    res = anontestapp.get('/test-section/subpage/', status=200)
    assert res.json['@id'] == '/test-section/subpage/'


def test_page_homepage(workbook, anontestapp):
    # res = anontestapp.get('/pages/homepage/', status=301)
    # assert res.location == 'http://localhost/'

    res = anontestapp.get('/', status=200)
    assert 'default_page' in res.json
    assert res.json['default_page']['@id'] == '/pages/homepage/'


def test_page_collection_default(workbook, anontestapp):
    # res = anontestapp.get('/pages/images/', status=301)
    # assert res.location == 'http://localhost/images/'

    res = anontestapp.get('/images/', status=200)
    assert 'default_page' in res.json
    assert res.json['default_page'] == '/pages/images/'
