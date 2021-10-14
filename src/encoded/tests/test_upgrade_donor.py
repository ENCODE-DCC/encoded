import pytest


def test_human_donor_upgrade(upgrader, human_donor_1_1):
    value = upgrader.upgrade('human_donor', human_donor_1_1, target_version='2')
    assert value['schema_version'] == '2'
    assert value['status'] == 'in progress'


def test_mouse_donor_upgrade_status_encode2(upgrader, mouse_donor_1):
    value = upgrader.upgrade('mouse_donor', mouse_donor_1, target_version='2')
    assert value['schema_version'] == '2'
    assert value['status'] == 'released'


def test_donor_upgrade_status_deleted(upgrader, human_donor_1_1):
    human_donor_1_1['status'] = 'DELETED'
    value = upgrader.upgrade('human_donor', human_donor_1_1, target_version='2')
    assert value['schema_version'] == '2'
    assert value['status'] == 'deleted'


def test_model_organism_donor_upgrade_(upgrader, mouse_donor_2):
    value = upgrader.upgrade('mouse_donor', mouse_donor_2, target_version='3')
    assert value['schema_version'] == '3'
    assert 'sex' not in value


def test_human_donor_age(upgrader, human_donor_2):
    value = upgrader.upgrade('human_donor', human_donor_2, target_version='3')
    assert value['schema_version'] == '3'
    assert value['age'] == '11'


def test_mouse_donor_upgrade_references(root, upgrader, mouse_donor, mouse_donor_3, publication, threadlocals, dummy_request):
    context = root.get_by_uuid(mouse_donor['uuid'])
    dummy_request.context = context
    value = upgrader.upgrade('mouse_donor', mouse_donor_3, target_version='4', context=context)
    assert value['schema_version'] == '4'
    assert value['references'] == [publication['uuid']]


def test_mouse_donor_documents_upgrade(root, dummy_request, upgrader, mouse_donor, mouse_donor_3):
    context = root.get_by_uuid(mouse_donor['uuid'])
    dummy_request.context = context
    value = upgrader.upgrade('mouse_donor', mouse_donor_3, target_version='6', context=context)
    assert value['schema_version'] == '6'
    assert 'donor_documents' not in value


def test_bad_fly_donor_alias_upgrade_3_4(root, upgrader, fly_donor_3):
    value = upgrader.upgrade('fly_donor', fly_donor_3, current_version='3', target_version='4')
    assert value['schema_version'] == '4'
    assert '||' not in value['aliases']
    assert '!' not in value['aliases']
    for alias in value['aliases']:
        assert len(alias.split(':')) == 2


def test_upgrade_human_donor_9_10(root, upgrader, human_donor_9):
    value = upgrader.upgrade('human_donor', human_donor_9, current_version='9', target_version='10')
    assert value['schema_version'] == '10'
    assert value['life_stage'] == 'newborn'
    assert value['ethnicity'] == 'Caucasian'


def test_upgrade_fly_worm_donor_7_8(root, upgrader, fly_donor_7):
    value = upgrader.upgrade('fly_donor', fly_donor_7, current_version='7', target_version='8')
    assert 'mutated_gene' not in value
    assert 'mutagen' not in value
    assert value['schema_version'] == '8'


def test_upgrade_human_donor_10_11(root, upgrader, human_donor_10):
    value = upgrader.upgrade('human_donor', human_donor_10,
        current_version='10', target_version='11')
    assert 'genetic_modifications' not in value


def test_upgrade_mouse_donor_10_11(root, upgrader, mouse_donor_10):
    value = upgrader.upgrade(
        'mouse_donor', mouse_donor_10, current_version='10', target_version='11')
    assert 'parent_strains' not in value


def test_upgrade_fly_donor_9_10(root, upgrader, fly_donor_9):
    value = upgrader.upgrade('fly_donor', fly_donor_9, current_version='9', target_version='10')
    for dbxref in value['dbxrefs']:
        assert 'Kyoto' not in dbxref
    assert 'kyoto:' not in value['aliases'][0]
    assert 'encode:kyoto_' in value['aliases'][0]
    assert 'DGGR' in value['external_ids'][0]
    assert value['schema_version'] == '10'


def test_upgrade_human_donor_11_12(root, upgrader, human_donor_11a, human_donor_11b):
    value = upgrader.upgrade('human_donor', human_donor_11a, current_version='11', target_version='12')
    assert value['ethnicity'] == ['Caucasian']
    value = upgrader.upgrade('human_donor', human_donor_11b, current_version='11', target_version='12')
    assert 'Arab' in value['ethnicity']
    assert 'Indian' in value['ethnicity']
    assert 'Arab Indian' not in value['ethnicity']


def test_upgrade_human_donor_12_13(root, upgrader, human_donor_12):
    value = upgrader.upgrade('human_donor', human_donor_12, current_version='12', target_version='13')
    assert 'European' in value['ethnicity']
    assert 'Asian' in value['ethnicity']
    assert 'Caucasian' not in value['ethnicity']
    assert value['notes'] == 'The ethnicity of this donor has been updated to European as the term Caucasian is deprecated.'
