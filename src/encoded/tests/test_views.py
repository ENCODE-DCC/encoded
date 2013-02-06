def test_home_html(testapp):
    res = testapp.get('/', status=200)
    assert res.body.startswith('<!DOCTYPE html>')


def test_antibodies_html(testapp):
    res = testapp.get('/antibodies/', status=200)
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
    from .sample_data import load_all
    load_all(testapp)
    res = testapp.get('/antibodies/', headers={'Accept': 'application/json'}, status=200)
    assert len(res.json['_embedded']['items']) == 1


def test_load_workbook(testapp):
    from ..loadxl import load_all
    load_all(testapp, 'AntibodySubmissionsENCODE3.xlsx')
