def test_home_html(testapp):
    res = testapp.get('/', status=200)
    assert res.body.startswith('<!DOCTYPE html>')


## these could all be tested with ?format=json as well.
def test_antibodies_html(testapp):
    res = testapp.get('/antibodies/', status=200)
    assert res.body.startswith('<!DOCTYPE html>')


def test_targets_html(testapp):
    res = testapp.get('/targets/', status=200)
    assert res.body.startswith('<!DOCTYPE html>')


def test_organisms_html(testapp):
    res = testapp.get('/organisms/', status=200)
    assert res.body.startswith('<!DOCTYPE html>')


def test_sources_html(testapp):
    res = testapp.get('/sources/', status=200)
    assert res.body.startswith('<!DOCTYPE html>')


def test_validations_html(testapp):
    res = testapp.get('/validations/', status=200)
    assert res.body.startswith('<!DOCTYPE html>')


def test_antibody_lots_html(testapp):
    res = testapp.get('/antibody-lots/', status=200)
    assert res.body.startswith('<!DOCTYPE html>')


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


def test_sample_data(testapp):

    from .sample_data import test_load_all
    test_load_all(testapp)
    res = testapp.get('/biosamples/', headers={'Accept': 'application/json'}, status=200)
    assert len(res.json['_embedded']['items']) == 1
    res = testapp.get('/labs/', headers={'Accept': 'application/json'}, status=200)
    assert len(res.json['_embedded']['items']) == 2


def test_load_workbook(testapp):
    from ..loadxl import load_all
    from pkg_resources import resource_filename
    workbook = resource_filename('encoded', 'tests/data/ENCODE_DCC_TestMetadata.xlsx')
    docsdir = resource_filename('encoded', 'tests/data/validation-docs/')
    load_all(testapp, workbook, docsdir)
    res = testapp.get('/antibodies/', headers={'Accept': 'application/json'}, status=200)
    assert res.json['_links']['items']
    assert len(res.json['_links']['items']) == 21
    res = testapp.get('/antibodies/?limit=10', headers={'Accept': 'application/json'}, status=200)
    assert res.json['_links']['items']
    assert len(res.json['_links']['items']) == 10

