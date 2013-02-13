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


def test_login_cycle(testapp, dummy_request):
    import requests
    from pyramid.security import authenticated_userid
    import sys

    data = requests.get('http://personatestuser.org/email_with_assertion/http%3A%2F%2Flocalhost:6543').json()
    email = data['email']
    assertion = data['assertion']

    sys.stderr.write("assertion\n==================\n")
    sys.stderr.write(assertion)
    res = testapp.post_json('/login', params={'assertion': assertion, 'came_from': '/'}, status=400)

    sys.stderr.write("\nRESPONSE\n==================\n")
    sys.stderr.write(res)
    assert res.json_body['status'] == "okay"
    assert testapp.security_policy.remembered == email
    assert authenticated_userid == email

    from pyramid.security import authenticated_userid
    res2 = testapp.get('/users/', status=200)
    assert authenticated_userid == email
    assert res2.body.startswith('<!DOCTYPE html>')


def test_user_html(testapp):
    res = testapp.get('/users/', status=401)
    assert res.body.startswith('<!DOCTYPE html>')


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
    assert len(res.json['_embedded']['items']) == 1


def test_sample_data(testapp):
    from .sample_data import test_load_all
    test_load_all(testapp)
    res = testapp.get('/biosamples/', headers={'Accept': 'application/json'}, status=200)
    assert len(res.json['_embedded']['items']) == 1
    res = testapp.get('/users/', headers={'Accept': 'application/json'}, status=200)
    assert len(res.json['_embedded']['items']) == 3


def test_load_workbook(testapp):
    from ..loadxl import load_all
    from pkg_resources import resource_filename
    load_all(testapp, resource_filename('encoded', 'tests/data/AntibodySubmissionsENCODE3.xlsx'))
    res = testapp.get('/antibodies/', headers={'Accept': 'application/json'}, status=200)
    assert res.json['_embedded']['items']
