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
def deleted_cart(testapp, submitter):
    item = {
        'name': 'test cart',
        'status': 'deleted',
        'locked': False,
        'elements': [],
        'submitted_by': submitter['uuid'],
    }
    return testapp.post_json('/cart', item).json['@graph'][0]


@pytest.fixture
def autosave_cart(testapp, submitter):
    item = {
        'name': 'test cart',
        'status': 'disabled',
        'locked': False,
        'elements': [],
        'submitted_by': submitter['uuid'],
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


@pytest.fixture
def cart_0_0():
    return{
        'name': 'Test Cart',
        'elements': []
    }


@pytest.fixture
def cart_1(cart_0_0):
    item = cart_0_0.copy()
    item.update({
        'schema_version': '1',
    })
    return item
