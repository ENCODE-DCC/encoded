import pytest


@pytest.fixture
def platform_0_0():
    return{
        'term_name': 'ChIP-seq',
        'term_id': 'OBI:0000716'
    }


@pytest.fixture
def platform_1(platform_0_0):
    item = platform_0_0.copy()
    item.update({
        'schema_version': '1',
        'encode2_dbxrefs': ['AB_SOLiD_3.5'],
        'geo_dbxrefs': ['GPL9442'],
    })
    return item


@pytest.fixture
def platform_2(platform_0_0):
    item = platform_0_0.copy()
    item.update({
        'schema_version': '2',
        'status': "CURRENT",
    })
    return item


@pytest.fixture
def platform_6(platform_0_0):
    item = platform_0_0.copy()
    item.update({
        'schema_version': '6',
        'status': "current",
    })
    return item


@pytest.fixture
def platform1(testapp):
    item = {
        'term_id': 'OBI:0002001',
        'term_name': 'HiSeq2000'
    }
    return testapp.post_json('/platform', item).json['@graph'][0]


@pytest.fixture
def platform2(testapp):
    item = {
        'term_id': 'OBI:0002049',
        'term_name': 'HiSeq4000'
    }
    return testapp.post_json('/platform', item).json['@graph'][0]


@pytest.fixture
def platform3(testapp):
    item = {
        'term_id': 'NTR:0000430',
        'term_name': 'Pacific Biosciences Sequel',
        'uuid': 'ced61406-dcc6-43c4-bddd-4c977cc676e8',
    }
    return testapp.post_json('/platform', item).json['@graph'][0]


@pytest.fixture
def platform4(testapp):
    item = {
        'term_id': 'NTR:0000448',
        'term_name': 'Oxford Nanopore - MinION',
        'uuid': '6c275b37-018d-4bf8-85f6-6e3b830524a9',
    }
    return testapp.post_json('/platform', item).json['@graph'][0]
