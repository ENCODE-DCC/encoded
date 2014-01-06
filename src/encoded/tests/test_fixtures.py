import pytest


@pytest.yield_fixture(scope='session')
def minitestdata(app, connection):
    tx = connection.begin_nested()

    from webtest import TestApp
    environ = {
        'HTTP_ACCEPT': 'application/json',
        'REMOTE_USER': 'TEST',
    }
    testapp = TestApp(app, environ)

    from .sample_data import URL_COLLECTION
    for url in ['/organisms/']:  # , '/sources/', '/users/']:
        collection = URL_COLLECTION[url]
        for item in collection[:1]:
            testapp.post_json(url, item, status=201)

    yield
    tx.rollback()


@pytest.yield_fixture(scope='session')
def minitestdata2(app, connection):
    tx = connection.begin_nested()

    from webtest import TestApp
    environ = {
        'HTTP_ACCEPT': 'application/json',
        'REMOTE_USER': 'TEST',
    }
    testapp = TestApp(app, environ)

    from .sample_data import URL_COLLECTION
    for url in ['/organisms/']:  # , '/sources/', '/users/']:
        collection = URL_COLLECTION[url]
        for item in collection:
            testapp.post_json(url, item, status=201)

    yield
    tx.rollback()


@pytest.mark.usefixtures('minitestdata')
def test_fixtures1(testapp):
    """ This test is not really exhaustive.

    Still need to inspect the sql log to verify fixture correctness.
    """
    url = '/organisms/'
    res = testapp.get(url)
    items = res.json['@graph']
    count1 = len(items)
    assert len(items)

    # Trigger an error
    item = {'foo': 'bar'}
    res = testapp.post_json(url, item, status=422)
    assert res.json['errors']

    res = testapp.get(url)
    items = res.json['@graph']
    assert len(items)

    from .sample_data import URL_COLLECTION
    item = URL_COLLECTION[url][1]
    testapp.post_json(url, item, status=201)

    res = testapp.get(url)
    items = res.json['@graph']
    count2 = len(items)
    assert count2 == count1 + 1

    # Trigger an error
    item = {'foo': 'bar'}
    res = testapp.post_json(url, item, status=422)
    assert res.json['errors']

    res = testapp.get(url)
    items = res.json['@graph']
    assert len(items) == count2


def test_fixtures2(minitestdata2, testapp):
    # http://stackoverflow.com/questions/15775601/mutually-exclusive-fixtures
    res = testapp.get('/organisms/')
    items = res.json['@graph']
    assert len(items)
