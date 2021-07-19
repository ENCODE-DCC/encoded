import pytest


def test_cart_upgrade_1_2(upgrader, cart_1):
    value = upgrader.upgrade('cart', cart_1, current_version='1', target_version='2')
    assert value['schema_version'] == '2'
    assert 'file_views' in value
