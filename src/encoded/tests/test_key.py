import pytest

items = [
    {'name': 'one', 'accession': 'TEST1'},
    {'name': 'two', 'accession': 'TEST2'},
]

bad_items = [
    {'name': 'one', 'accession': 'BAD1'},
    {'name': 'bad', 'accession': 'TEST1'},
]


def test_keys_add(testapp):
    url = '/testing-keys/'
    for item in items:
        testapp.post_json(url, item, status=201)

    for item in bad_items:
        testapp.post_json(url, item, status=409)


def test_keys_update(testapp):
    url = '/testing-keys/'
    item = items[0]
    res = testapp.post_json(url, item, status=201)
    location = res.location
    new_item = {'name': 'new_one', 'accession': 'NEW1'}
    testapp.post_json(location, new_item, status=200)
    testapp.post_json(url, item, status=201)
    testapp.post_json(location, item, status=409)


@pytest.mark.slow
def test_keys_templated(workbook, session):
    from ..storage import Key
    keys = [(key.name, key.value) for key in session.query(Key).all()]
    assert keys
    for name, value in keys:
        assert '{' not in name
        assert '{' not in value
