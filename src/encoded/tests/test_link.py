import pytest

targets = [
    {'name': 'one', '_uuid': '775795d3-4410-4114-836b-8eeecf1d0c2f'},
    {'name': 'one', '_uuid': 'd6784f5e-48a1-4b40-9b11-c8aefb6e1377'},
]

sources = [
    {
        'name': 'A',
        'target': '775795d3-4410-4114-836b-8eeecf1d0c2f',
        '_uuid': '16157204-8c8f-4672-a1a4-14f4b8021fcd',
    },
    {
        'name': 'B',
        'target': 'd6784f5e-48a1-4b40-9b11-c8aefb6e1377',
        '_uuid': '1e152917-c5fd-4aec-b74f-b0533d0cc55c',
    },
]


@pytest.fixture
def content(testapp):
    url = '/testing-link-targets/'
    for item in targets:
        testapp.post_json(url, item, status=201)

    url = '/testing-link-sources/'
    for item in sources:
        testapp.post_json(url, item, status=201)


def test_links_add(content, session):
    from ..storage import Link
    links = sorted([
        (str(link.source_rid), link.rel, str(link.target_rid))
        for link in session.query(Link).all()
    ])
    expected = sorted([
        (sources[0]['_uuid'], u'testing_link', targets[0]['_uuid']),
        (sources[1]['_uuid'], u'testing_link', targets[1]['_uuid']),
    ])
    assert links == expected


def test_links_update(content, testapp, session):
    from ..storage import Link

    url = '/testing-link-sources/' + sources[1]['_uuid']
    new_item = {'name': 'B updated', 'target': targets[0]['_uuid']}
    testapp.post_json(url, new_item, status=200)

    links = sorted([
        (str(link.source_rid), link.rel, str(link.target_rid))
        for link in session.query(Link).all()
    ])
    expected = sorted([
        (sources[0]['_uuid'], u'testing_link', targets[0]['_uuid']),
        (sources[1]['_uuid'], u'testing_link', targets[0]['_uuid']),
    ])
    assert links == expected
