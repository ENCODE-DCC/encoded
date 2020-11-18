import pytest


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
    platform_6['schema_version'] = '6'
    value = upgrader.upgrade('platform', platform_6, current_version='6', target_version='7')
    assert value['schema_version'] == '7'
    assert value['status'] == 'deleted'
