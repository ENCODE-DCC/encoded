import pytest


@pytest.fixture
def cart(testapp, submitter):
    item = {
        'name': 'test cart',
        'submitted_by': submitter['uuid'],
    }
    return testapp.post_json('/cart', item).json['@graph'][0]


@pytest.fixture
def other_cart(testapp, remc_member):
    item = {
        'name': 'test cart',
        'submitted_by': remc_member['uuid'],
    }
    return testapp.post_json('/cart', item).json['@graph'][0]


@pytest.fixture
def cart_submitter_testapp(app, submitter):
    '''TestApp with JSON accept header for non-admin user.
    '''
    from webtest import TestApp
    environ = {
        'HTTP_ACCEPT': 'application/json',
        'REMOTE_USER': submitter['uuid'],
    }
    return TestApp(app, environ)


@pytest.fixture
def other_cart_submitter_testapp(app, remc_member):
    '''TestApp with JSON accept header for non-admin user.
    '''
    from webtest import TestApp
    environ = {
        'HTTP_ACCEPT': 'application/json',
        'REMOTE_USER': remc_member['uuid'],
    }
    return TestApp(app, environ)


def test_add_element_to_cart(testapp, cart, experiment):
    testapp.patch_json(
        cart['@id'],
        {'elements': [experiment['@id']]}
    )
    res = testapp.get(cart['@id'])
    assert res.json['elements'][0] == experiment['@id']


def test_owner_can_add_element_to_cart(cart_submitter_testapp, testapp, cart, experiment):
    cart_submitter_testapp.patch_json(
        cart['@id'],
        {'elements': [experiment['@id']]}
    )
    res = testapp.get(cart['@id'])
    assert res.json['elements'][0] == experiment['@id']


def test_not_owner_cannot_add_element_to_cart(cart_submitter_testapp, testapp, other_cart, experiment):
    cart_submitter_testapp.patch_json(
        other_cart['@id'],
        {'elements': [experiment['@id']]},
        status=403
    )


def test_other_can_see_cart(cart_submitter_testapp, other_cart, remc_member):
    res = cart_submitter_testapp.get(other_cart['@id'])
    assert res.json['submitted_by'] == remc_member['@id']


def test_submitter_cannot_add_own_cart(cart_submitter_testapp, submitter):
    item = {
        'name': 'test cart'
    }
    cart_submitter_testapp.post_json('/cart', item, status=403)


def test_submitter_can_not_modify_submitted_by(cart_submitter_testapp, submitter):
    item = {
        'name': 'test cart',
        'submitted_by': submitter['uuid']
    }
    cart_submitter_testapp.post_json('/cart', item, status=422)


def test_get_carts_by_user(cart, submitter, dummy_request, threadlocals):
    from encoded.types.cart import _get_carts_by_user
    userid = submitter['uuid']
    carts = _get_carts_by_user(dummy_request, userid)
    assert carts
    assert carts[0] == cart['@id']


def test_create_cart(dummy_request, threadlocals, submitter):
    from encoded.types.cart import _create_cart
    user = dummy_request.root.get_by_uuid(submitter['uuid'])
    cart = _create_cart(dummy_request, user)
    assert cart and '/carts/' in cart


def test_get_or_create_cart_by_user(cart_submitter_testapp, submitter):
    # Cart doesn't exist
    res = cart_submitter_testapp.get('/carts/@@get-cart')
    carts = res.json['@graph']
    assert carts and '/carts/' in carts[0]
    created_cart = cart_submitter_testapp.get(carts[0])
    assert created_cart.json['submitted_by'] == submitter['@id']
    # Cart should exist
    retrieved_cart = cart_submitter_testapp.get('/carts/@@get-cart').json['@graph'][0]
    assert created_cart.json['@id'] == retrieved_cart


def test_get_or_create_cart_no_user(testapp):
    testapp.get('/carts/@@get-cart', status=400)
