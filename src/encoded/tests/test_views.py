import pytest

COLLECTION_URLS = [
    '/',
    '/antibodies/',
    '/targets/',
    '/organisms/',
    '/sources/',
    '/validations/',
    '/antibody-lots/',
    ]


@pytest.mark.parametrize('url', COLLECTION_URLS)
def test_html(testapp, url):
    res = testapp.get(url, status=200)
    assert res.body.startswith('<!DOCTYPE html>')


@pytest.mark.parametrize('url', COLLECTION_URLS)
def test_json(jsontestapp, url):
    res = jsontestapp.get(url, status=200)
    assert res.json['_links']


@pytest.mark.persona
@pytest.mark.slow
def test_bad_audience(testapp, dummy_request):
    import requests

    data = requests.get('http://personatestuser.org/email_with_assertion/http%3A%2F%2Fsomeaudience').json()
    assertion = data['assertion']

    res = testapp.post_json('/login', params={'assertion': assertion, 'came_from': '/'}, status=400)


def _test_login_cycle(testapp, dummy_request):
    import requests
    from pyramid.security import authenticated_userid

    data = requests.get('http://personatestuser.org/email_with_assertion/http%3A%2F%2Flocalhost:6543').json()
    try:
        email = data['email']
        assertion = data['assertion']
    except KeyError:
        import sys
        sys.stderr.write("Something is foul with personatestuser: %s" % data)

    res = testapp.post_json('/login', params={'assertion': assertion, 'came_from': '/'}, status=200)

    assert res.json_body['status'] == "okay"
    #assert res.vary == 'Accept'  res.vary or res.headers['vary'] does not exist
    #assert res.cookies['auth_tkt'] != ''  ## or something.
    ## assert testapp.security_policy.remembered == email

    res2 = testapp.get('/users/', status=200)
    '''
    I clearly don't understand the testapp.testResponse
    import sys
    sys.stderr.write(res2)
    assert res2.cookies['auth_tkt'] != ''  ## or something.
    '''
    assert res2.body.startswith('<!DOCTYPE html>')


def _test_user_html(testapp):
    ''' this test should return 403 forbidden but cannot currently load data
        via post_json with authz on.
    '''
    res = testapp.get('/users/', status=403)


def _test_antibody_approval_creation(testapp):
    from urlparse import urlparse
    new_antibody = {'foo': 'bar'}
    res = testapp.post_json('/antibodies/', new_antibody, status=201)
    assert res.location
    assert res.json['_links']['profile'] == {'href': '/profiles/result'}
    assert res.json['_links']['items'] == [{'href': urlparse(res.location).path}]
    res = testapp.get(res.location, headers={'Accept': 'application/json'}, status=200)
    assert res.json['_links']['profile'] == {'href': '/profiles/antibody_approval'}
    data = dict(res.json)
    del data['_links']
    assert data == new_antibody
    res = testapp.get('/antibodies/', headers={'Accept': 'application/json'}, status=200)
    assert len(res.json['_links']['items']) == 1


def __test_sample_data(testapp):

    from .sample_data import test_load_all
    test_load_all(testapp)
    res = testapp.get('/biosamples/', headers={'Accept': 'application/json'}, status=200)
    assert len(res.json['_embedded']['items']) == 1
    res = testapp.get('/labs/', headers={'Accept': 'application/json'}, status=200)
    assert len(res.json['_embedded']['items']) == 2


@pytest.mark.slow
def test_load_workbook(testapp, collection_test):
    from ..loadxl import load_all
    from pkg_resources import resource_filename
    assert type(collection_test) == dict
    workbook = resource_filename('encoded', 'tests/data/test_encode3_interface_submissions.xlsx')
    docsdir = resource_filename('encoded', 'tests/data/validation-docs/')
    from conftest import app_settings
    load_test_only = app_settings.get('load_test_only', False)
    assert load_test_only
    load_all(testapp, workbook, docsdir, test=load_test_only)
    for content_type, expect in collection_test.iteritems():
        url = '/'+content_type+'/'
        res = testapp.get(url, headers={'Accept': 'application/json'}, status=200)
        assert res.json['_links']['items']
        assert len(res.json['_links']['items']) == expect

    # test limit
    res = testapp.get('/antibodies/?limit=10', headers={'Accept': 'application/json'}, status=200)
    assert res.json['_links']['items']
    assert len(res.json['_links']['items']) == 10


def test_organisms_post(testapp):
    from .sample_data import ORGANISMS as items
    url = '/organisms/'
    for item in items:
        testapp.post_json(url, item, status=201)


def test_organisms_post_bad_json(testapp):
    items = [{'foo': 'bar'}]
    url = '/organisms/'
    for item in items:
        testapp.post_json(url, item, status=422)
