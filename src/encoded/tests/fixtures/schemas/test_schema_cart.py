import pytest


def test_cart_released_without_description(testapp, cart_0_0, submitter):
    cart_0_0.update({'status': 'released', 'submitted_by': submitter['uuid']})
    testapp.post_json('/cart', cart_0_0, status=422)
    cart_0_0.update({'description': 'Released carts must have a description.'})
    testapp.post_json('/cart', cart_0_0, status=201)