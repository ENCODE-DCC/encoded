import pytest

targets = [
    {'name': 'one', 'uuid': '775795d3-4410-4114-836b-8eeecf1d0c2f'},
    {'name': 'two', 'uuid': 'd6784f5e-48a1-4b40-9b11-c8aefb6e1377'},
]

sources = [
    {
        'name': 'A',
        'target': '775795d3-4410-4114-836b-8eeecf1d0c2f',
        'uuid': '16157204-8c8f-4672-a1a4-14f4b8021fcd',
        'status': 'CURRENT',
    },
    {
        'name': 'B',
        'target': 'd6784f5e-48a1-4b40-9b11-c8aefb6e1377',
        'uuid': '1e152917-c5fd-4aec-b74f-b0533d0cc55c',
        'status': 'DELETED',
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
        (sources[0]['uuid'], u'target', targets[0]['uuid']),
        (sources[1]['uuid'], u'target', targets[1]['uuid']),
    ])
    assert links == expected


def test_links_update(content, testapp, session):
    from ..storage import Link

    url = '/testing-link-sources/' + sources[1]['uuid']
    new_item = {'name': 'B updated', 'target': targets[0]['uuid']}
    testapp.put_json(url, new_item, status=200)

    links = sorted([
        (str(link.source_rid), link.rel, str(link.target_rid))
        for link in session.query(Link).all()
    ])
    expected = sorted([
        (sources[0]['uuid'], u'target', targets[0]['uuid']),
        (sources[1]['uuid'], u'target', targets[0]['uuid']),
    ])
    assert links == expected


def test_links_reverse(content, testapp, session):
    target = targets[0]
    res = testapp.get('/testing-link-targets/%s/' % target['uuid'])
    assert res.json['reverse'] == ['/testing-link-sources/%s/' % sources[0]['uuid']]

    # DELTED sources are hidden from the list.
    target = targets[1]
    res = testapp.get('/testing-link-targets/%s/' % target['uuid'])
    assert res.json['reverse'] == []
    
