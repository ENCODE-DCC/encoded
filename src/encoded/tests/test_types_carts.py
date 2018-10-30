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


def test_add_element_to_cart(testapp, cart):
    testapp.patch_json(
        cart['@id'],
        {'elements': ['abc']}
    )
    res = testapp.get(cart['@id'])
    assert res.json['elements'][0] == 'abc'


def test_owner_can_add_element_to_cart(cart_submitter_testapp, testapp, cart):
    cart_submitter_testapp.patch_json(
        cart['@id'],
        {'elements': ['abc']}
    )
    res = testapp.get(cart['@id'])
    assert res.json['elements'][0] == 'abc'


def test_not_owner_cannot_add_element_to_cart(cart_submitter_testapp, testapp, other_cart):
    cart_submitter_testapp.patch_json(
        other_cart['@id'],
        {'elements': ['bde']},
        status=403
    )


def test_other_can_see_cart(cart_submitter_testapp, other_cart, remc_member):
    res = cart_submitter_testapp.get(other_cart['@id'])
    assert res.json['submitted_by'] == remc_member['@id']
