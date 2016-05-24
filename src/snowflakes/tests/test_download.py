from base64 import b64decode
import pytest


RED_DOT = """data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAUA
AAAFCAYAAACNbyblAAAAHElEQVQI12P4//8/w38GIAXDIBKE0DHxgljNBAAO
9TXL0Y4OHwAAAABJRU5ErkJggg=="""

BLUE_DOT = """data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAA
oAAAAKAQMAAAC3/F3+AAAACXBIWXMAAA7DAAAOwwHHb6hkAA
AAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAgY0hSTQ
AAeiYAAICEAAD6AAAAgOgAAHUwAADqYAAAOpgAABdwnLpRPA
AAAANQTFRFALfvPEv6TAAAAAtJREFUCB1jYMAHAAAeAAEBGN
laAAAAAElFTkSuQmCC"""


@pytest.fixture
def testing_download(testapp):
    url = '/testing-downloads/'
    item = {
        'attachment': {
            'download': 'red-dot.png',
            'href': RED_DOT,
        },
        'attachment2': {
            'download': 'blue-dot.png',
            'href': BLUE_DOT,
        },
    }
    res = testapp.post_json(url, item, status=201)
    return res.location


def test_download_create(testapp, testing_download):
    res = testapp.get(testing_download)
    attachment = res.json['attachment']
    attachment2 = res.json['attachment2']

    assert attachment['href'] == '@@download/attachment/red-dot.png'
    assert attachment['type'] == 'image/png'
    assert attachment['width'] == 5
    assert attachment['height'] == 5
    assert attachment['md5sum'] == 'b60ab2708daec7685f3d412a5e05191a'
    url = testing_download + '/' + attachment['href']
    res = testapp.get(url)
    assert res.content_type == 'image/png'
    assert res.body == b64decode(RED_DOT.split(',', 1)[1])

    assert attachment2['href'] == '@@download/attachment2/blue-dot.png'
    assert attachment2['type'] == 'image/png'
    assert attachment2['width'] == 10
    assert attachment2['height'] == 10
    assert attachment2['md5sum'] == '013f03aa088adb19aa226c3439bda179'
    url = testing_download + '/' + attachment2['href']
    res = testapp.get(url)
    assert res.content_type == 'image/png'
    assert res.body == b64decode(BLUE_DOT.split(',', 1)[1])


def test_download_update(testapp, testing_download):
    from base64 import b64decode
    item = {
        'attachment': {
            'download': 'blue-dot.png',
            'href': BLUE_DOT,
        },
        'attachment2': {
            'download': 'red-dot.png',
            'href': RED_DOT,
        },
    }
    testapp.put_json(testing_download, item, status=200)
    res = testapp.get(testing_download)
    attachment = res.json['attachment']
    attachment2 = res.json['attachment2']

    assert attachment['href'] == '@@download/attachment/blue-dot.png'
    url = testing_download + '/' + attachment['href']
    res = testapp.get(url)
    assert res.content_type == 'image/png'
    assert res.body == b64decode(BLUE_DOT.split(',', 1)[1])

    assert attachment2['href'] == '@@download/attachment2/red-dot.png'
    url = testing_download + '/' + attachment2['href']
    res = testapp.get(url)
    assert res.content_type == 'image/png'
    assert res.body == b64decode(RED_DOT.split(',', 1)[1])


def test_download_update_no_change(testapp, testing_download):
    item = {
        'attachment': {
            'download': 'red-dot.png',
            'href': '@@download/attachment/red-dot.png',
        },
        'attachment2': {
            'download': 'blue-dot.png',
            'href': '@@download/attachment2/blue-dot.png',
        },
    }
    testapp.put_json(testing_download, item, status=200)

    res = testapp.get(testing_download)
    attachment = res.json['attachment']
    attachment2 = res.json['attachment2']
    assert attachment['href'] == '@@download/attachment/red-dot.png'
    assert attachment2['href'] == '@@download/attachment2/blue-dot.png'


def test_download_update_one(testapp, testing_download):
    item = {
        'attachment': {
            'download': 'red-dot.png',
            'href': '@@download/attachment/red-dot.png',
        },
        'attachment2': {
            'download': 'red-dot.png',
            'href': RED_DOT,
        },
    }
    testapp.put_json(testing_download, item, status=200)

    res = testapp.get(testing_download)
    attachment = res.json['attachment']
    attachment2 = res.json['attachment2']

    assert attachment['href'] == '@@download/attachment/red-dot.png'
    url = testing_download + '/' + attachment['href']
    res = testapp.get(url)
    assert res.content_type == 'image/png'
    assert res.body == b64decode(RED_DOT.split(',', 1)[1])

    assert attachment2['href'] == '@@download/attachment2/red-dot.png'
    url = testing_download + '/' + attachment2['href']
    res = testapp.get(url)
    assert res.content_type == 'image/png'
    assert res.body == b64decode(RED_DOT.split(',', 1)[1])


def test_download_remove_one(testapp, testing_download):
    item = {
        'attachment': {
            'download': 'red-dot.png',
            'href': '@@download/attachment/red-dot.png',
        },
    }
    testapp.put_json(testing_download, item, status=200)

    res = testapp.get(testing_download)
    assert 'attachment' in res.json
    assert 'attachment2' not in res.json

    url = testing_download + '/@@download/attachment2/red-dot.png'
    res = testapp.get(url, status=404)


@pytest.mark.parametrize(
    'href',
    [
        '@@download/attachment/another.png',
        'http://example.com/another.png',
    ])
def test_download_update_bad_change(testapp, testing_download, href):
    item = {'attachment': {
        'download': 'red-dot.png',
        'href': href,
    }}
    testapp.put_json(testing_download, item, status=422)


@pytest.mark.parametrize(
    'href',
    [
        '@@download/attachment/another.png',
        'http://example.com/another.png',
        'data:image/png;base64,NOT_BASE64',
        'data:image/png;NOT_A_PNG',
        'data:text/plain;asdf',
    ])
def test_download_create_bad_change(testapp, href):
    url = '/testing-downloads/'
    item = {'attachment': {
        'download': 'red-dot.png',
        'href': href,
    }}
    testapp.post_json(url, item, status=422)


def test_download_create_wrong_extension(testapp):
    url = '/testing-downloads/'
    item = {'attachment': {
        'download': 'red-dot.jpg',
        'href': RED_DOT,
    }}
    testapp.post_json(url, item, status=422)


def test_download_create_w_wrong_md5sum(testapp):
    url = '/testing-downloads/'
    item = {'attachment': {
        'download': 'red-dot.jpg',
        'href': RED_DOT,
        'md5sum': 'deadbeef',
    }}
    testapp.post_json(url, item, status=422)
