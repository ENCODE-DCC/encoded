def test_home_html(testapp):
    res = testapp.get('/', status=200)
    assert res.body.startswith('<!DOCTYPE html>')


def test_antibodies_html(testapp):
    res = testapp.get('/antibodies/', status=200)
    assert res.body.startswith('<!DOCTYPE html>')
