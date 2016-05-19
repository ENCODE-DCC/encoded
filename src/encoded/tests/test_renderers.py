def test_render_error(anonhtmltestapp):
    res = anonhtmltestapp.get('/testing-render-error', status=500)
    assert res.body.startswith(b'<!DOCTYPE html>')


def test_render_error_multiple_times(anonhtmltestapp):
    anonhtmltestapp.get('/testing-render-error', status=500)
    res = anonhtmltestapp.get('/testing-render-error', status=500)
    assert res.body.startswith(b'<!DOCTYPE html>')


def test_render_error_then_success(anonhtmltestapp):
    anonhtmltestapp.get('/testing-render-error', status=500)
    res = anonhtmltestapp.get('/', status=200)
    assert res.body.startswith(b'<!DOCTYPE html>')
