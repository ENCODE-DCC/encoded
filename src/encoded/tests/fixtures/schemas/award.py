import pytest


@pytest.fixture
def ENCODE3_award(testapp):
    item = {
        'name': 'ABC1234',
        'rfa': 'ENCODE3',
        'project': 'ENCODE',
        'title': 'A Generic ENCODE3 Award'
    }
    return testapp.post_json('/award', item, status=201).json['@graph'][0]

@pytest.fixture
def award_a():
    return{
        'name': 'ENCODE2',
    }


@pytest.fixture
def award_1(award_a):
    item = award_a.copy()
    item.update({
        'schema_version': '1',
        'rfa': "ENCODE2"
    })
    return item


@pytest.fixture
def award_2(award_1):
    item = award_1.copy()
    item.update({
        'schema_version': '3',
        'viewing_group': 'ENCODE',
    })
    return item


@pytest.fixture
def award_5(award_2):
    item = award_2.copy()
    item.update({
        'schema_version': '6',
        'viewing_group': 'ENCODE',
    })
    return item


@pytest.fixture
def award(testapp):
    item = {
        'name': 'encode3-award',
        'rfa': 'ENCODE3',
        'project': 'ENCODE',
        'title': 'A Generic ENCODE3 Award',
        'viewing_group': 'ENCODE3',
    }
    return testapp.post_json('/award', item).json['@graph'][0]


@pytest.fixture
def award_modERN(testapp):
    item = {
        'name': 'modERN-award',
        'rfa': 'modERN',
        'project': 'modERN',
        'title': 'A Generic modERN Award',
        'viewing_group': 'ENCODE3',
    }
    return testapp.post_json('/award', item).json['@graph'][0]


@pytest.fixture
def remc_award(testapp):
    item = {
        'name': 'remc-award',
        'rfa': 'GGR',
        'project': 'GGR',
        'title': 'A Generic REMC Award',
        'viewing_group': 'REMC',
    }
    return testapp.post_json('/award', item).json['@graph'][0]


@pytest.fixture
def encode2_award(testapp):
    item = {
        # upgrade/shared.py ENCODE2_AWARDS
        'uuid': '1a4d6443-8e29-4b4a-99dd-f93e72d42418',
        'name': 'encode2-award',
        'rfa': 'ENCODE2',
        'project': 'ENCODE',
        'title': 'A Generic ENCODE2 Award',
        'viewing_group': 'ENCODE3',
    }
    return testapp.post_json('/award', item).json['@graph'][0]


@pytest.fixture
def encode4_award(testapp):
    item = {
        'name': 'encode4-award',
        'rfa': 'ENCODE4',
        'project': 'ENCODE',
        'title': 'A Generic ENCODE4 Award',
        'viewing_group': 'ENCODE4',
        'component': 'mapping',
    }
    return testapp.post_json('/award', item).json['@graph'][0]


@pytest.fixture
def award_encode4(testapp):
    item = {
        'name': 'encode4-award',
        'rfa': 'ENCODE4',
        'project': 'ENCODE',
        'title': 'A Generic ENCODE4 Award',
        'viewing_group': 'ENCODE4',
    }
    return testapp.post_json('/award', item).json['@graph'][0]
