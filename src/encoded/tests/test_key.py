import pytest

items = [
    {'name': 'one', 'alias': 'TEST1'},
    {'name': 'two', 'alias': 'TEST2'},
]

bad_items = [
    {'name': 'one', 'alias': 'BAD1'},
    {'name': 'bad', 'alias': 'TEST1'},
]


@pytest.fixture
def content(testapp):
    url = '/testing-keys/'
    for item in items:
        testapp.post_json(url, item, status=201)


@pytest.mark.parametrize('item', items)
def test_unique_key(testapp, content, item):
    url = '/testing-keys/' + item['alias']
    res = testapp.get(url).maybe_follow()
    assert res.json['name'] == item['name']


def test_keys_bad_items(testapp, content):
    url = '/testing-keys/'
    for item in bad_items:
        testapp.post_json(url, item, status=409)


def test_keys_update(testapp):
    url = '/testing-keys/'
    item = items[0]
    res = testapp.post_json(url, item, status=201)
    location = res.location
    new_item = {'name': 'new_one', 'alias': 'NEW1'}
    testapp.put_json(location, new_item, status=200)
    testapp.post_json(url, item, status=201)
    testapp.put_json(location, item, status=409)


def test_keys_conflict(testapp):
    url = '/testing-keys/'
    item = items[1]
    initial = testapp.get(url).json['@graph']
    testapp.post_json(url, item, status=201)
    posted = testapp.get(url).json['@graph']
    assert(len(initial)+1 == len(posted))
    conflict = testapp.post_json(url, item, status=409)
    assert(conflict.status_code == 409)
    conflicted = testapp.get(url).json['@graph']
    assert(len(posted) == len(conflicted))


@pytest.mark.slow
def test_keys_templated(workbook, session):
    from snovault.storage import Key
    keys = [(key.name, key.value) for key in session.query(Key).all()]
    assert keys
    for name, value in keys:
        assert '{' not in name
        assert '{' not in value
