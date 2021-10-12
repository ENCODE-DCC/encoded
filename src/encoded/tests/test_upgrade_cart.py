import pytest


def test_cart_upgrade_1_2(upgrader, cart_1):
    value = upgrader.upgrade('cart', cart_1, current_version='1', target_version='2')
    assert value['schema_version'] == '2'
    assert 'file_views' in value


def test_cart_upgrade_2_3(upgrader, autosave_cart, cart_0_0):
    value = upgrader.upgrade('cart', autosave_cart, current_version='2', target_version='3')
    assert value['schema_version'] == '3'
    assert value['status'] == 'unlisted'
    cart_0_0['status'] = 'current'
    value = upgrader.upgrade('cart', cart_0_0, current_version='2', target_version='3')
    assert value['schema_version'] == '3'
    assert value['status'] == 'unlisted'