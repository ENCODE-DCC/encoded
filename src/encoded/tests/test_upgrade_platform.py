import pytest


@pytest.fixture
def platform():
    return{
        'term_name': 'ChIP-seq',
        'term_id': 'OBI:0000716'
    }


@pytest.fixture
def platform_1(platform):
    item = platform.copy()
    item.update({
        'schema_version': '1',
        'encode2_dbxrefs': ['AB_SOLiD_3.5'],
        'geo_dbxrefs': ['GPL9442'],
    })
    return item


@pytest.fixture
def platform_2(platform):
    item = platform.copy()
    item.update({
        'schema_version': '2',
        'status': "CURRENT",
    })
    return item


@pytest.fixture
def platform_6(platform):
    item = platform.copy()
    item.update({
        'schema_version': '6',
        'status': "current",
    })
    return item


def test_platform_upgrade(upgrader, platform_1):
    value = upgrader.upgrade('platform', platform_1, target_version='2')
    assert value['schema_version'] == '2'
    assert 'encode2_dbxrefs' not in value
    assert 'geo_dbxrefs' not in value
    assert value['dbxrefs'] == ['UCSC-ENCODE-cv:AB_SOLiD_3.5', 'GEO:GPL9442']


def test_platform_upgrade_status(upgrader, platform_2):
    value = upgrader.upgrade('platform', platform_2, target_version='3')
    assert value['schema_version'] == '3'
    assert value['status'] == 'current'


def test_platform_upgrade_6_7(upgrader, platform_6):
    value = upgrader.upgrade('platform', platform_6, current_version='6', target_version='7')
    assert value['schema_version'] == '7'
    assert value['status'] == 'released'
    platform_6['status'] = 'disabled'
    platform_6['schema_version'] == '6'
    value = upgrader.upgrade('platform', platform_6, current_version='6', target_version='7')
    assert value['schema_version'] == '7'
    assert value['status'] == 'deleted'
