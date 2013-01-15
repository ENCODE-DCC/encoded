def test_home_html(testapp):
    res = testapp.get('/', status=200)
    assert res.body.startswith('<!DOCTYPE html>')


def test_antibodies_html(testapp):
    res = testapp.get('/antibodies/', status=200)
    assert res.body.startswith('<!DOCTYPE html>')


def test_antibody_creation(testapp):
    new_antibody = {'foo': 'bar'}
    res = testapp.post_json('/antibodies/', new_antibody, status=201)
    assert res.location
    assert res.json['class'] == ['result:success', 'result']
    assert res.json['entities'] == [{'rel': ['item'], 'href': res.location}]
    res = testapp.get(res.location, headers={'Accept': 'application/json'}, status=200)
    assert res.json['class'] == ['antibody']
    assert res.json['properties'] == new_antibody
    res = testapp.get('/antibodies/', headers={'Accept': 'application/json'}, status=200)
    assert len(res.json['entities']) == 1
