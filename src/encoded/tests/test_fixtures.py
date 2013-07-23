import pytest


@pytest.datafixture
def minitestdata(app, data_fixture_manager):
    assert data_fixture_manager._current_connection == 'minitestdata'

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


@pytest.datafixture
def minitestdata2(app, data_fixture_manager):
    assert data_fixture_manager._current_connection == 'minitestdata2'

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


@pytest.mark.usefixtures('minitestdata')
def test_fixtures1(testapp):
    """ This test is not really exhaustive.

    Still need to inspect the sql log to verify fixture correctness.
    """
    url = '/organisms/'
    res = testapp.get(url)
    items = res.json['items']
    count1 = len(items)
    assert len(items)

    # Trigger an error
    item = {'foo': 'bar'}
    res = testapp.post_json(url, item, status=422)
    assert res.json['errors']

    res = testapp.get(url)
    items = res.json['items']
    assert len(items)

    from .sample_data import URL_COLLECTION
    item = URL_COLLECTION[url][1]
    testapp.post_json(url, item, status=201)

    res = testapp.get(url)
    items = res.json['items']
    count2 = len(items)
    assert count2 == count1 + 1

    # Trigger an error
    item = {'foo': 'bar'}
    res = testapp.post_json(url, item, status=422)
    assert res.json['errors']

    res = testapp.get(url)
    items = res.json['items']
    assert len(items) == count2


def test_fixtures2(minitestdata2, testapp):
    # http://stackoverflow.com/questions/15775601/mutually-exclusive-fixtures
    res = testapp.get('/organisms/')
    items = res.json['items']
    assert len(items)
