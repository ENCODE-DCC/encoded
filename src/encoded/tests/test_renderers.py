from encoded.renderers import should_transform
from unittest import mock

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

def test_should_transform_limit_all_returns_false():
    response = mock.Mock()
    request = mock.Mock()
    request.params = {'limit': 'all'}
    assert should_transform(request, response) == False

def test_should_transform_limit_1001_returns_false():
    response = mock.Mock()
    request = mock.Mock()
    request.params = {'limit': 1001}
    assert should_transform(request, response) == False
