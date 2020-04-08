import pytest


def test_antibody_lot_upgrade(upgrader, antibody_lot_1):
    value = upgrader.upgrade('antibody_lot', antibody_lot_1, target_version='2')
    assert value['schema_version'] == '2'
    assert 'encode2_dbxrefs' not in value
    assert value['dbxrefs'] == ['UCSC-ENCODE-cv:CEBPZ']


def test_antibody_lot_upgrade_status(upgrader, antibody_lot_2):
    value = upgrader.upgrade('antibody_lot', antibody_lot_2, target_version='3')
    assert value['schema_version'] == '3'
    assert value['status'] == 'released'


def test_antibody_lot_upgrade_status_encode3(upgrader, antibody_lot_2):
    antibody_lot_2['award'] = 'ea1f650d-43d3-41f0-a96a-f8a2463d332f'
    value = upgrader.upgrade('antibody_lot', antibody_lot_2, target_version='3')
    assert value['schema_version'] == '3'
    assert value['status'] == 'in progress'


def test_antibody_lot_upgrade_status_deleted(upgrader, antibody_lot_2):
    antibody_lot_2['status'] = 'DELETED'
    value = upgrader.upgrade('antibody_lot', antibody_lot_2, target_version='3')
    assert value['schema_version'] == '3'
    assert value['status'] == 'deleted'


def test_antibody_lot_unique_array(upgrader, antibody_lot_4):
    value = upgrader.upgrade('antibody_lot', antibody_lot_4, current_version='4', target_version='5')
    assert len(value['purifications']) == len(set(value['purifications']))
    assert len(value['lot_id_alias']) == len(set(value['lot_id_alias']))
