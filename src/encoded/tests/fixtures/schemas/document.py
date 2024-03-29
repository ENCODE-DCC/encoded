import pytest


@pytest.fixture
def base_document(testapp, lab, award):
    item = {
        'lab': lab['uuid'],
        'award': award['uuid'],
        'document_type': 'growth protocol'
    }
    return testapp.post_json('/document', item, status=201).json['@graph'][0]


@pytest.fixture
def standards_document(testapp, lab, award):
    item = {
        'lab': lab['uuid'],
        'award': award['uuid'],
        'document_type': 'standards document'
    }
    return testapp.post_json('/document', item, status=201).json['@graph'][0]

@pytest.fixture
def document_0(publication):
    return {
        'references': [publication['identifiers'][0]],
    }


@pytest.fixture
def document_base(lab, award):
    return {
        'award': award['uuid'],
        'lab': lab['uuid'],
        'document_type': 'growth protocol',
    }


@pytest.fixture
def document_1(document_base):
    item = document_base.copy()
    item.update({
        'schema_version': '2',
        'status': 'CURRENT',
        'award': '4d462953-2da5-4fcf-a695-7206f2d5cf45'
    })
    return item


@pytest.fixture
def document_3(root, document, publication):
    item = root.get_by_uuid(document['uuid'])
    properties = item.properties.copy()
    properties.update({
        'schema_version': '3',
        'references': [publication['identifiers'][0]],
    })
    return properties


@pytest.fixture
def document(testapp, lab, award):
    item = {
        'award': award['@id'],
        'lab': lab['@id'],
        'document_type': 'growth protocol',
    }
    return testapp.post_json('/document', item).json['@graph'][0]


@pytest.fixture
def intact_protocol(testapp, lab, award):
    item = {
        'award': award['@id'],
        'lab': lab['@id'],
        'uuid': '4dfd0b02-ed3a-4461-b0f5-9ef51570af1f',
        'document_type': 'general protocol'
    }
    return testapp.post_json('/document', item).json['@graph'][0]


@pytest.fixture
def in_situ_protocol(testapp, lab, award):
    item = {
        'award': award['@id'],
        'lab': lab['@id'],
        'uuid': '45e51f3b-d18e-44f9-b126-325918114d37',
        'document_type': 'general protocol'
    }
    return testapp.post_json('/document', item).json['@graph'][0]


@pytest.fixture
def dilution_protocol(testapp, lab, award):
    item = {
        'award': award['@id'],
        'lab': lab['@id'],
        'uuid': '94430c54-3a32-44fa-9e70-6d68b3f51544',
        'document_type': 'general protocol'
    }
    return testapp.post_json('/document', item).json['@graph'][0]