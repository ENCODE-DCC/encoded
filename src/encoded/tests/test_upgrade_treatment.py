import pytest


def test_treatment_upgrade(upgrader, treatment_1):
    value = upgrader.upgrade('treatment', treatment_1, target_version='2')
    assert value['schema_version'] == '2'
    assert 'encode2_dbxrefs' not in value
    assert value['dbxrefs'] == ['UCSC-ENCODE-cv:Estradiol_1nM']
    assert 'award' not in value


def test_treatment_upgrade_encode_dbxref(upgrader, treatment_1):
    treatment_1['encode2_dbxrefs'] = ["encode:hESC to endoderm differentiation treatment"]
    value = upgrader.upgrade('treatment', treatment_1, current_version='1', target_version='2')
    assert value['schema_version'] == '2'
    assert 'encode2_dbxrefs' not in value
    assert value['dbxrefs'] == ['UCSC-ENCODE-cv:hESC to endoderm differentiation treatment']
    assert 'award' not in value


def test_treatment_upgrade_status(upgrader, treatment_2):
    value = upgrader.upgrade('treatment', treatment_2, current_version='2', target_version='3')
    assert value['schema_version'] == '3'
    assert value['status'] == 'current'


def test_treatment_upgrade_3_4(upgrader, treatment_3):
    value = upgrader.upgrade('treatment', treatment_3, current_version='3', target_version='4')
    assert value['schema_version'] == '4'
    assert len(value['aliases']) == 1


def test_treatment_upgrade_4_to_5(upgrader, treatment_4):
    value = upgrader.upgrade('treatment', treatment_4, current_version='4', target_version='5')
    assert value['schema_version'] == '5'
    assert 'protocols' not in value
    assert 'documents' in value
    assert 'antibodies' not in value
    assert 'antibodies_used' in value
    assert 'concentation' not in value
    assert 'amount' in value
    assert 'concentation_units' not in value
    assert 'amount_units' in value


def test_treatment_upgrade_8_to_9(upgrader, treatment_8):
    value = upgrader.upgrade('treatment', treatment_8, current_version='8', target_version='9')
    assert value['schema_version'] == '9'
    assert value['treatment_term_id'] == 'UniProtKB:P03823'


def test_treatment_upgrade_9_10(upgrader, treatment_9):
    value = upgrader.upgrade('treatment', treatment_9, current_version='9', target_version='10')
    assert value['schema_version'] == '10'
    assert value['status'] == 'released'
    treatment_9['status'] = 'disabled'
    treatment_9['schema_version'] = '9'
    value = upgrader.upgrade('treatment', treatment_9, current_version='9', target_version='10')
    assert value['schema_version'] == '10'
    assert value['status'] == 'deleted'


def test_treatment_upgrade_10_11(upgrader, treatment_10):
    assert 'lab' in treatment_10
    value = upgrader.upgrade('treatment', treatment_10, current_version='10', target_version='11')
    assert value['schema_version'] == '11'
    assert 'lab' not in value


def test_treatment_upgrade_11_12(upgrader, treatment_11):
    value = upgrader.upgrade('treatment', treatment_11, current_version='11', target_version='12')
    assert value['treatment_type'] == 'chemical'
    assert value['purpose'] == 'stimulation'


def test_treatment_upgrade_12_13(upgrader, treatment_12):
    treatment_12['product_id'] = ''
    value = upgrader.upgrade('treatment', treatment_12, current_version='12', target_version='13')
    assert value['schema_version'] == '13'
    assert 'product_id' not in value


def test_treatment_upgrade_13_14(upgrader, treatment_with_negative_duration_amount_units):
    value = upgrader.upgrade('treatment', treatment_with_negative_duration_amount_units, current_version='13', target_version='14')
    assert value['amount'] == 0
    assert value['duration'] == 0
    assert value['notes'] == (
        'This treatment erroneously had a negative amount of -100 '
        'and was upgraded to 0. This treatment erroneously had a '
        'negative duration of -9 and was upgraded to 0.'
    )
