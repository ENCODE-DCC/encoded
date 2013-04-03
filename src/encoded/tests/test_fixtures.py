import pytest


def test_fixtures1(minitestdata, testapp):
    url = '/organisms/'
    res = testapp.get(url)
    items = res.json['_links']['items']
    count1 = len(items)
    assert len(items)

    # Trigger an error
    item = {'foo': 'bar'}
    res = testapp.post_json(url, item, status=422)
    assert res.json['errors']

    res = testapp.get(url)
    items = res.json['_links']['items']
    assert len(items)

    from .sample_data import URL_COLLECTION
    item = URL_COLLECTION[url][0].copy()
    item['_uuid'] = '91cddd2c-549b-45f4-8937-82a6a11cca1e'
    testapp.post_json(url, item, status=201)

    res = testapp.get(url)
    items = res.json['_links']['items']
    count2 = len(items)
    assert count2 == count1 + 1

    # Trigger an error
    item = {'foo': 'bar'}
    res = testapp.post_json(url, item, status=422)
    assert res.json['errors']

    res = testapp.get(url)
    items = res.json['_links']['items']
    assert len(items) == count2


@pytest.mark.xfail
def test_fixtures2(minitestdata2, testapp):
    # http://stackoverflow.com/questions/15775601/mutually-exclusive-fixtures
    res = testapp.get('/organisms/')
    items = res.json['_links']['items']
    assert len(items)
