import pytest

targets = [
    {'name': 'one', 'uuid': '775795d3-4410-4114-836b-8eeecf1d0c2f'},
    {'name': 'two', 'uuid': 'd6784f5e-48a1-4b40-9b11-c8aefb6e1377'},
]

item = {
    'required': 'required value',
}

simple1 = {
    'required': 'required value',
    'simple1': 'supplied simple1',
}

simple2 = {
    'required': 'required value',
    'simple2': 'supplied simple2',
}

item_with_uuid = [
    {
        'uuid': '0f13ff76-c559-4e70-9497-a6130841df9f',
        'required': 'required value 1',
    },
    {
        'uuid': '6c3e444b-f290-43c4-bfb9-d20135377770',
        'required': 'required value 2',
    },
]

item_with_link = [
    {
        'required': 'required value 1',
        'protected_link': '775795d3-4410-4114-836b-8eeecf1d0c2f',
    },
    {
        'required': 'required value 2',
        'protected_link': 'd6784f5e-48a1-4b40-9b11-c8aefb6e1377',
    },
]


COLLECTION_URL = '/testing-post-put-patch/'


@pytest.fixture
def link_targets(testapp):
    url = '/testing-link-targets/'
    for item in targets:
        testapp.post_json(url, item, status=201)


@pytest.fixture
def content(testapp):
    res = testapp.post_json(COLLECTION_URL, item_with_uuid[0], status=201)
    return {'@id': res.location}


@pytest.fixture
def content_with_child(testapp):
    parent_res = testapp.post_json('/testing-link-targets/', {}, status=201)
    parent_id = parent_res.json['@graph'][0]['@id']
    child_res = testapp.post_json('/testing-link-sources/', {'target': parent_id})
    child_id = child_res.json['@graph'][0]['@id']
    return {'@id': parent_id, 'child': child_id}


def test_admin_post(testapp):
    testapp.post_json(COLLECTION_URL, item, status=201)
    testapp.post_json(COLLECTION_URL, item_with_uuid[0], status=201)


def test_submitter_post(submitter_testapp):
    testapp = submitter_testapp
    testapp.post_json(COLLECTION_URL, item, status=201)
    res = testapp.post_json(COLLECTION_URL, item_with_uuid[0], status=422)
    assert any(error.get('name') == ['uuid'] for error in res.json['errors'])


def test_admin_put_uuid(content, testapp):
    url = content['@id']
    # so long as the same uuid is supplied, PUTing the uuid is fine
    testapp.put_json(url, item_with_uuid[0], status=200)
    # but the uuid may not be changed on PUT;
    testapp.put_json(url, item_with_uuid[1], status=422)


def test_submitter_put_uuid(content, submitter_testapp):
    testapp = submitter_testapp
    url = content['@id']
    # so long as the same uuid is supplied, PUTing the uuid is fine
    testapp.put_json(url, item_with_uuid[0], status=200)
    # but the uuid may not be changed on PUT;
    testapp.put_json(url, item_with_uuid[1], status=422)


def test_defaults_on_put(content, testapp):
    url = content['@id']
    res = testapp.get(url)
    assert res.json['simple1'] == 'simple1 default'
    assert res.json['simple2'] == 'simple2 default'

    res = testapp.put_json(url, simple1, status=200)
    assert res.json['@graph'][0]['simple1'] == 'supplied simple1'
    assert res.json['@graph'][0]['simple2'] == 'simple2 default'

    res = testapp.put_json(url, simple2, status=200)
    assert res.json['@graph'][0]['simple1'] == 'simple1 default'
    assert res.json['@graph'][0]['simple2'] == 'supplied simple2'


def test_patch(content, testapp):
    url = content['@id']
    res = testapp.get(url)
    assert res.json['simple1'] == 'simple1 default'
    assert res.json['simple2'] == 'simple2 default'

    res = testapp.patch_json(url, {}, status=200)
    assert res.json['@graph'][0]['simple1'] == 'simple1 default'
    assert res.json['@graph'][0]['simple2'] == 'simple2 default'

    res = testapp.patch_json(url, {'simple1': 'supplied simple1'}, status=200)
    assert res.json['@graph'][0]['simple1'] == 'supplied simple1'
    assert res.json['@graph'][0]['simple2'] == 'simple2 default'

    res = testapp.patch_json(url, {'simple2': 'supplied simple2'}, status=200)
    assert res.json['@graph'][0]['simple1'] == 'supplied simple1'
    assert res.json['@graph'][0]['simple2'] == 'supplied simple2'


def test_admin_put_protected_link(link_targets, testapp):
    res = testapp.post_json(COLLECTION_URL, item_with_link[0], status=201)
    url = res.location

    testapp.put_json(url, item_with_link[0], status=200)
    testapp.put_json(url, item_with_link[1], status=200)


def test_submitter_put_protected_link(link_targets, testapp, submitter_testapp):
    res = testapp.post_json(COLLECTION_URL, item_with_link[0], status=201)
    url = res.location

    submitter_testapp.put_json(url, item_with_link[0], status=200)
    submitter_testapp.put_json(url, item_with_link[1], status=422)


def test_put_object_not_touching_children(content_with_child, testapp):
    url = content_with_child['@id']
    res = testapp.put_json(url, {}, status=200)
    assert content_with_child['child'] in res.json['@graph'][0]['reverse']


def test_put_object_editing_child(content_with_child, testapp):
    edit = {
        'reverse': [{
            '@id': content_with_child['child'],
            'status': 'released',
        }]
    }
    testapp.put_json(content_with_child['@id'], edit, status=200)
    res = testapp.get(content_with_child['child'] + '?frame=embedded')
    assert res.json['status'] == 'released'


def test_put_object_adding_child(content_with_child, testapp):
    edit = {
        'reverse': [
            content_with_child['child'],
            {
                'status': 'released',
            }
        ]
    }
    testapp.put_json(content_with_child['@id'], edit, status=200)
    res = testapp.get(content_with_child['@id'])
    assert len(res.json['reverse']) == 2


def test_submitter_put_object_adding_disallowed_child(
        root, monkeypatch, content_with_child, submitter_testapp):
    from pyramid.security import Allow
    monkeypatch.setattr(root['testing-link-sources'], '__acl__', (), raising=False)
    monkeypatch.setattr(
        root['testing-link-targets'], '__acl__',
        ((Allow, 'group.submitter', 'edit'),), raising=False)
    edit = {
        'reverse': [
            content_with_child['child'],
            {
                'status': 'released',
            }
        ]
    }
    res = submitter_testapp.put_json(content_with_child['@id'], edit, status=422)
    assert res.json['errors'][0]['description'].startswith(
        'add forbidden to /testing-link-sources/')


def test_put_object_removing_child(content_with_child, testapp):
    edit = {
        'reverse': [],
    }
    testapp.put_json(content_with_child['@id'], edit, status=200)
    res = testapp.get(content_with_child['@id'] + '?frame=embedded')
    assert len(res.json['reverse']) == 0
    res = testapp.get(content_with_child['child'])
    assert res.json['status'] == 'deleted'


def test_put_object_child_validation(content_with_child, testapp):
    edit = {
        'reverse': [{
            '@id': content_with_child['child'],
            'target': 'BOGUS',
        }]
    }
    res = testapp.put_json(content_with_child['@id'], edit, status=422)
    assert res.json['errors'][0]['name'] == [u'reverse', 0, u'target']


def test_put_object_validates_child_references(content_with_child, testapp):
    # Try a child that doesn't exist
    edit = {
        'reverse': [
            content_with_child['child'],
            '/asdf',
        ]
    }
    testapp.put_json(content_with_child['@id'], edit, status=422)

    # Try a child that exists but is the wrong type
    edit = {
        'reverse': [
            content_with_child['child'],
            content_with_child['@id'],
        ]
    }
    testapp.put_json(content_with_child['@id'], edit, status=422)


def test_post_object_with_child(testapp):
    edit = {
        'reverse': [{
            'status': 'released',
        }]
    }
    res = testapp.post_json('/testing-link-targets', edit, status=201)
    parent_id = res.json['@graph'][0]['@id']
    source = res.json['@graph'][0]['reverse'][0]
    res = testapp.get(source)
    assert res.json['target'] == parent_id


def test_etag_if_match_tid(testapp, organism):
    res = testapp.get(organism['@id'] + '?frame=edit', status=200)
    etag = res.etag
    testapp.patch_json(organism['@id'], {}, headers={'If-Match': etag}, status=200)
    testapp.patch_json(organism['@id'], {}, headers={'If-Match': etag}, status=412)


def test_retry(testapp):
    res = testapp.post_json('/testing-post-put-patch/', {'required': ''})
    url = res.location
    res = testapp.get(url + '/@@testing-retry?datstore=database')
    assert res.json['attempt'] == 2
    assert not res.json['detached']
