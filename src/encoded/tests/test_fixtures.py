import pytest


@pytest.yield_fixture(scope='session')
def minitestdata(app, conn):
    tx = conn.begin_nested()

    from webtest import TestApp
    environ = {
        'HTTP_ACCEPT': 'application/json',
        'REMOTE_USER': 'TEST',
    }
    testapp = TestApp(app, environ)

    item = {
        'name': 'human',
        'scientific_name': 'Homo sapiens',
        'taxon_id': '9606',
    }
    testapp.post_json('/organism', item, status=201)

    yield
    tx.rollback()


@pytest.yield_fixture(scope='session')
def minitestdata2(app, conn):
    tx = conn.begin_nested()

    from webtest import TestApp
    environ = {
        'HTTP_ACCEPT': 'application/json',
        'REMOTE_USER': 'TEST',
    }
    testapp = TestApp(app, environ)

    item = {
        'name': 'human',
        'scientific_name': 'Homo sapiens',
        'taxon_id': '9606',
    }
    testapp.post_json('/organism', item, status=201)

    yield
    tx.rollback()


@pytest.mark.usefixtures('minitestdata')
def test_fixtures1(testapp):
    """ This test is not really exhaustive.

    Still need to inspect the sql log to verify fixture correctness.
    """
    res = testapp.get('/organism').maybe_follow()
    items = res.json['@graph']
    assert len(items) == 1

    # Trigger an error
    item = {'foo': 'bar'}
    res = testapp.post_json('/organism', item, status=422)
    assert res.json['errors']

    res = testapp.get('/organism').maybe_follow()
    items = res.json['@graph']
    assert len(items) == 1

    item = {
        'name': 'mouse',
        'scientific_name': 'Mus musculus',
        'taxon_id': '10090',
    }
    testapp.post_json('/organism', item, status=201)

    res = testapp.get('/organism').maybe_follow()
    items = res.json['@graph']
    assert len(items) == 2

    # Trigger an error
    item = {'foo': 'bar'}
    res = testapp.post_json('/organism', item, status=422)
    assert res.json['errors']

    res = testapp.get('/organism').maybe_follow()
    items = res.json['@graph']
    assert len(items) == 2


def test_fixtures2(minitestdata2, testapp):
    # http://stackoverflow.com/questions/15775601/mutually-exclusive-fixtures
    res = testapp.get('/organisms/')
    items = res.json['@graph']
    assert len(items) == 1
