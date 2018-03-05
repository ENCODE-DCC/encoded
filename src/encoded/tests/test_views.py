import pytest


def _type_length():
    # Not a fixture as we need to parameterize tests on this
    from ..loadxl import ORDER
    from pkg_resources import resource_stream
    import codecs
    import json
    utf8 = codecs.getreader("utf-8")
    return {
        name: len(json.load(utf8(resource_stream('encoded', 'tests/data/inserts/%s.json' % name))))
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
    assert res.body.startswith(b'<!DOCTYPE html>')


def test_home_json(testapp):
    res = testapp.get('/', status=200)
    assert res.json['@type']


def test_home_app_version(testapp):
    res = testapp.get('/', status=200)
    assert 'app_version' in res.json


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
    assert res.body.startswith(b'<!DOCTYPE html>')


@pytest.mark.parametrize('item_type', TYPE_LENGTH)
def test_html_collections(workbook, htmltestapp, item_type):
    res = htmltestapp.get('/' + item_type).follow(status=200)
    assert res.body.startswith(b'<!DOCTYPE html>')


@pytest.mark.slow
@pytest.mark.parametrize('item_type', TYPE_LENGTH)
def test_html_pages(workbook, testapp, htmltestapp, item_type):
    res = testapp.get('/%s?limit=all' % item_type).follow(status=200)
    for item in res.json['@graph']:
        res = htmltestapp.get(item['@id'])
        assert res.body.startswith(b'<!DOCTYPE html>')


@pytest.mark.slow
@pytest.mark.parametrize('item_type', [k for k in TYPE_LENGTH if k != 'user'])
def test_html_server_pages(workbook, item_type, wsgi_server):
    from webtest import TestApp
    testapp = TestApp(wsgi_server)
    res = testapp.get(
        '/%s?limit=all' % item_type,
        headers={'Accept': 'application/json'},
    ).follow(
        status=200,
        headers={'Accept': 'application/json'},
    )
    for item in res.json['@graph']:
        res = testapp.get(item['@id'], status=200)
        assert res.body.startswith(b'<!DOCTYPE html>')
        assert b'Internal Server Error' not in res.body


@pytest.mark.parametrize('item_type', TYPE_LENGTH)
def test_json(testapp, item_type):
    res = testapp.get('/' + item_type).follow(status=200)
    assert res.json['@type']


def test_json_basic_auth(anonhtmltestapp):
    from base64 import b64encode
    from pyramid.compat import ascii_native_
    url = '/'
    value = "Authorization: Basic %s" % ascii_native_(b64encode(b'nobody:pass'))
    res = anonhtmltestapp.get(url, headers={'Authorization': value}, status=401)
    assert res.content_type == 'application/json'


def test_load_sample_data(
        analysis_step,
        analysis_step_run,
        antibody_characterization,
        antibody_lot,
        award,
        biosample,
        biosample_characterization,
        document,
        experiment,
        file,
        lab,
        library,
        mouse_donor,
        organism,
        pipeline,
        publication,
        publication_data,
        replicate,
        software,
        software_version,
        source,
        submitter,
        target,
        ucsc_browser_composite,
        ):
    assert True, 'Fixtures have loaded sample data'


def test_abstract_collection(testapp, experiment):
    testapp.get('/Dataset/{accession}'.format(**experiment))
    testapp.get('/datasets/{accession}'.format(**experiment))


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


def test_collection_post(testapp):
    item = {
        'name': 'human',
        'scientific_name': 'Homo sapiens',
        'taxon_id': '9606',
    }
    return testapp.post_json('/organism', item, status=201)


def test_collection_post_bad_json(testapp):
    item = {'foo': 'bar'}
    res = testapp.post_json('/organism', item, status=422)
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
    from base64 import b64encode
    from pyramid.compat import ascii_native_
    value = "Authorization: Basic %s" % ascii_native_(b64encode(b'nobody:pass'))
    anontestapp.post_json('/organism', {}, headers={'Authorization': value}, status=401)


def test_collection_actions_filtered_by_permission(workbook, testapp, anontestapp):
    res = testapp.get('/pages/')
    assert any(action for action in res.json.get('actions', []) if action['name'] == 'add')

    res = anontestapp.get('/pages/')
    assert not any(action for action in res.json.get('actions', []) if action['name'] == 'add')


def test_item_actions_filtered_by_permission(testapp, authenticated_testapp, source):
    location = source['@id']

    res = testapp.get(location)
    assert any(action for action in res.json.get('actions', []) if action['name'] == 'edit')

    res = authenticated_testapp.get(location)
    assert not any(action for action in res.json.get('actions', []) if action['name'] == 'edit')


def test_collection_put(testapp, execute_counter):
    initial = {
        'name': 'human',
        'scientific_name': 'Homo sapiens',
        'taxon_id': '9606',
    }
    item_url = testapp.post_json('/organism', initial).location

    with execute_counter.expect(1):
        item = testapp.get(item_url).json

    for key in initial:
        assert item[key] == initial[key]

    update = {
        'name': 'mouse',
        'scientific_name': 'Mus musculus',
        'taxon_id': '10090',
    }
    testapp.put_json(item_url, update, status=200)

    res = testapp.get('/' + item['uuid']).follow().json

    for key in update:
        assert res[key] == update[key]


def test_post_duplicate_uuid(testapp, mouse):
    item = {
        'uuid': mouse['uuid'],
        'name': 'human',
        'scientific_name': 'Homo sapiens',
        'taxon_id': '9606',
    }
    testapp.post_json('/organism', item, status=409)


def test_user_effective_principals(submitter, lab, anontestapp, execute_counter):
    email = submitter['email']
    with execute_counter.expect(1):
        res = anontestapp.get('/@@testing-user',
                              extra_environ={'REMOTE_USER': str(email)})
    assert sorted(res.json['effective_principals']) == [
        'group.submitter',
        'lab.%s' % lab['uuid'],
        'remoteuser.%s' % email,
        'submits_for.%s' % lab['uuid'],
        'system.Authenticated',
        'system.Everyone',
        'userid.%s' % submitter['uuid'],
        'viewing_group.ENCODE3',
    ]


def test_page_toplevel(workbook, anontestapp):
    res = anontestapp.get('/test-section/', status=200)
    assert res.json['@id'] == '/test-section/'

    res = anontestapp.get('/pages/test-section/', status=301)
    assert res.location == 'http://localhost/test-section/'


def test_page_nested(workbook, anontestapp):
    res = anontestapp.get('/test-section/subpage/', status=200)
    assert res.json['@id'] == '/test-section/subpage/'


def test_page_nested_in_progress(workbook, anontestapp):
    return anontestapp.get('/test-section/subpage-in-progress/', status=403)


def test_page_homepage(workbook, anontestapp):
    res = anontestapp.get('/pages/homepage/', status=200)
    assert res.json['canonical_uri'] == '/'

    res = anontestapp.get('/', status=200)
    assert 'default_page' in res.json
    assert res.json['default_page']['@id'] == '/pages/homepage/'


def test_page_collection_default(workbook, anontestapp):
    res = anontestapp.get('/pages/images/', status=200)
    assert res.json['canonical_uri'] == '/images/'

    res = anontestapp.get('/images/', status=200)
    assert 'default_page' in res.json
    assert res.json['default_page']['@id'] == '/pages/images/'


def test_jsonld_context(testapp):
    res = testapp.get('/terms/')
    assert res.json


def test_jsonld_term(testapp):
    res = testapp.get('/terms/submitted_by')
    assert res.json


@pytest.mark.slow
@pytest.mark.parametrize('item_type', TYPE_LENGTH)
def test_index_data_workbook(workbook, testapp, indexer_testapp, item_type):
    res = testapp.get('/%s?limit=all' % item_type).follow(status=200)
    for item in res.json['@graph']:
        indexer_testapp.get(item['@id'] + '@@index-data')


@pytest.mark.parametrize('item_type', TYPE_LENGTH)
def test_profiles(testapp, item_type):
    from jsonschema_serialize_fork import Draft4Validator
    res = testapp.get('/profiles/%s.json' % item_type).maybe_follow(status=200)
    errors = Draft4Validator.check_schema(res.json)
    assert not errors


def test_bad_frame(testapp, human):
    res = testapp.get(human['@id'] + '?frame=bad', status=404)
    assert res.json['detail'] == '?frame=bad'
