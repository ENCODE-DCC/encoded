'''py.test fixtures for Pyramid.

http://pyramid.readthedocs.org/en/latest/narr/testing.html
'''
from pytest import fixture


@fixture
def config(fixture_request):
    from pyramid.testing import setUp, tearDown
    fixture_request.addfinalizer(tearDown)
    return setUp()


@fixture
def request():
    from pyramid.testing import DummyRequest
    return DummyRequest()


@fixture
def testapp():
    '''WSGI application level functional testing.
    '''
    from encoded import main
    from webtest import TestApp
    app = main({})
    return TestApp(app)
