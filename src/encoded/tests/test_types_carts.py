import pytest

from pyramid.exceptions import HTTPBadRequest

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


def test_submitter_cant_see_deleted_cart(cart_submitter_testapp, deleted_cart, submitter):
    cart_submitter_testapp.get(deleted_cart['@id'], status=403)


def test_other_cant_see_autosave_cart(other_cart_submitter_testapp, autosave_cart, remc_member):
    other_cart_submitter_testapp.get(autosave_cart['@id'], status=403)


def test_submitter_can_see_autosave_cart(cart_submitter_testapp, autosave_cart, submitter):
    cart_submitter_testapp.get(autosave_cart['@id'], status=200)


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
    from encoded.cart_view import get_cart_objects_by_user
    userid = submitter['uuid']
    carts = get_cart_objects_by_user(dummy_request, userid)
    assert carts
    assert carts[0]['@id'] == cart['@id']


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


def test_cart_object_init(dummy_request):
    from encoded.cart_view import Cart
    cart = Cart(dummy_request)
    assert isinstance(cart, Cart)
    assert cart.request == dummy_request
    assert cart.uuids == []
    assert cart.max_cart_elements == None


def test_cart_object_get_carts_from_params(dummy_request):
    from encoded.cart_view import Cart
    cart = Cart(dummy_request)
    assert cart._get_carts_from_params() == []
    dummy_request.environ['QUERY_STRING'] = (
        'cart=abc123&cart=def456'
    )
    cart = Cart(dummy_request)
    assert cart._get_carts_from_params() == ['abc123', 'def456']


def test_cart_get_cart_object_or_error(cart, submitter, experiment, dummy_request, threadlocals, testapp):
    testapp.patch_json(
        cart['@id'],
        {'elements': [experiment['@id']]}
    )
    from encoded.cart_view import Cart
    c = Cart(dummy_request, uuids=[cart['uuid']])
    cart_object = c._get_cart_object_or_error(cart['uuid'])
    assert cart_object.get('@id') == cart['@id']
    with pytest.raises(KeyError):
        c._get_cart_object_or_error('abc')

def test_cart_try_to_get_cart_object(cart, submitter, experiment, dummy_request, threadlocals, testapp):
    testapp.patch_json(
        cart['@id'],
        {'elements': [experiment['@id']]}
    )
    from encoded.cart_view import Cart
    c = Cart(dummy_request, uuids=[cart['uuid']])
    cart_object = c._try_to_get_cart_object(cart['uuid'])
    assert cart_object.get('@id') == cart['@id']
    assert c._try_to_get_cart_object('abc') == {}

def test_cart_object_try_to_get_elements_from_cart(cart, submitter, experiment, dummy_request, threadlocals, testapp):
    testapp.patch_json(
        cart['@id'],
        {'elements': [experiment['@id']]}
    )
    from encoded.cart_view import Cart
    c = Cart(dummy_request, uuids=[cart['uuid']])
    assert c.uuids == [cart['uuid']]
    elements = c._try_to_get_elements_from_cart(cart['uuid'])
    assert elements == [experiment['@id']]
    assert c._try_to_get_elements_from_cart('abc') == []


def test_cart_object_get_elements_from_carts(cart, submitter, experiment, dummy_request, threadlocals, testapp):
    testapp.patch_json(
        cart['@id'],
        {'elements': [experiment['@id']]}
    )
    from encoded.cart_view import Cart
    dummy_request.environ['QUERY_STRING'] = (
        f'cart={cart["@id"]}'
    )
    c = Cart(dummy_request)
    elements = list(c._get_elements_from_carts())
    assert elements == [experiment['@id']]
    c = Cart(dummy_request, uuids=[cart['@id']])
    elements = list(c._get_elements_from_carts())
    assert elements == [experiment['@id']]
    c = Cart(dummy_request, uuids=[cart['uuid']])
    elements = list(c._get_elements_from_carts())
    assert elements == [experiment['@id']]
    c = Cart(dummy_request, uuids=['abc'])
    elements = list(c._get_elements_from_carts())
    assert elements == []


def test_cart_object_validate_cart_size(cart, submitter, experiment, dummy_request, threadlocals, testapp):
    from pyramid.exceptions import HTTPBadRequest
    testapp.patch_json(
        cart['@id'],
        {'elements': [experiment['@id']]}
    )
    from encoded.cart_view import Cart
    dummy_request.environ['QUERY_STRING'] = (
        f'cart={cart["@id"]}'
    )
    c = Cart(dummy_request)
    c._elements = [experiment['@id']]
    c._validate_cart_size()
    c = Cart(dummy_request, max_cart_elements=0)
    c._elements = [experiment['@id']]
    with pytest.raises(HTTPBadRequest):
        c._validate_cart_size()


def test_cart_object_elements(cart, submitter, experiment, dummy_request, threadlocals, testapp):
    testapp.patch_json(
        cart['@id'],
        {'elements': [experiment['@id'], experiment['@id']]}
    )
    from encoded.cart_view import Cart
    dummy_request.environ['QUERY_STRING'] = (
        f'cart={cart["uuid"]}'
    )
    c = Cart(dummy_request)
    assert list(c.elements) == [experiment['@id']]


def test_cart_object_as_params(cart, submitter, experiment, dummy_request, threadlocals, testapp, mocker):
    mocker.spy(dummy_request, 'embed')
    testapp.patch_json(
        cart['@id'],
        {'elements': [experiment['@id'], experiment['@id']]}
    )
    from encoded.cart_view import Cart
    dummy_request.environ['QUERY_STRING'] = (
        f'cart={cart["uuid"]}'
    )
    c = Cart(dummy_request)
    assert dummy_request.embed.call_count == 0
    assert c.as_params() == [('@id', experiment['@id'])]
    assert dummy_request.embed.call_count == 1
    # Cache value
    assert c.as_params() == [('@id', experiment['@id'])]
    assert dummy_request.embed.call_count == 1


def test_cart_object_no_elements(cart, submitter, experiment, dummy_request, threadlocals, testapp):
    from encoded.cart_view import Cart
    dummy_request.environ['QUERY_STRING'] = (
        f'cart={cart["uuid"]}'
    )
    c = Cart(dummy_request)
    assert list(c.elements) == []
    assert c.as_params() == []


def test_cart_object_no_carts(cart, submitter, experiment, dummy_request, threadlocals, testapp):
    from encoded.cart_view import Cart
    c = Cart(dummy_request)
    assert list(c.elements) == []
    assert c.as_params() == []


def test_cart_object_two_carts(cart, submitter, experiment, dummy_request, threadlocals, testapp, mocker):
    mocker.spy(dummy_request, 'embed')
    testapp.patch_json(
        cart['@id'],
        {'elements': [experiment['@id'], experiment['@id']]}
    )
    from encoded.cart_view import Cart
    dummy_request.environ['QUERY_STRING'] = (
        f'cart={cart["uuid"]}&cart={cart["@id"]}'
    )
    c = Cart(dummy_request)
    assert dummy_request.embed.call_count == 0
    assert c.as_params() == [
        ('@id', experiment['@id'])
    ]
    assert dummy_request.embed.call_count == 2
    # Cache value
    assert c.as_params() == [
        ('@id', experiment['@id'])
    ]
    assert dummy_request.embed.call_count == 2


def test_cart_with_elements_object_init(dummy_request):
    from encoded.cart_view import CartWithElements
    cart = CartWithElements(dummy_request)
    assert isinstance(cart, CartWithElements)
    assert cart.request == dummy_request
    assert cart.uuids == []
    assert cart.max_cart_elements == 8000
    cart = CartWithElements(
        dummy_request,
        max_cart_elements=5
    )
    cart.max_cart_elements == 5


def test_cart_with_elements_object_try_to_get_cart_object(cart, submitter, experiment, dummy_request, threadlocals, testapp):
    testapp.patch_json(
        cart['@id'],
        {'elements': [experiment['@id']]}
    )
    from encoded.cart_view import CartWithElements
    c = CartWithElements(dummy_request, uuids=[cart['uuid']])
    cart_object = c._try_to_get_cart_object(cart['uuid'])
    assert cart_object.get('@id') == cart['@id']
    with pytest.raises(HTTPBadRequest):
        c._try_to_get_cart_object('abc')


def test_cart_with_elements_object_try_to_get_elements_from_cart(cart, submitter, experiment, dummy_request, threadlocals, testapp):
    testapp.patch_json(
        cart['@id'],
        {'elements': [experiment['@id']]}
    )
    from encoded.cart_view import CartWithElements
    c = CartWithElements(dummy_request, uuids=[cart['uuid']])
    assert c.max_cart_elements == 8000
    assert c.uuids == [cart['uuid']]
    elements = c._try_to_get_elements_from_cart(cart['uuid'])
    assert elements == [experiment['@id']]
    testapp.patch_json(
        cart['@id'],
        {'elements': []}
    )
    with pytest.raises(HTTPBadRequest):
        c._try_to_get_elements_from_cart(cart['uuid'])


def test_cart_with_object_validate_cart_size(cart, submitter, experiment, dummy_request, threadlocals, testapp):
    from pyramid.exceptions import HTTPBadRequest
    testapp.patch_json(
        cart['@id'],
        {'elements': [experiment['@id']]}
    )
    from encoded.cart_view import CartWithElements
    dummy_request.environ['QUERY_STRING'] = (
        f'cart={cart["@id"]}'
    )
    c = CartWithElements(dummy_request, max_cart_elements=3)
    c._elements = [experiment['@id']]
    assert c.max_cart_elements == 3
    c._validate_cart_size()
    c._elements = ['a', 'b', 'c', 'd']
    with pytest.raises(HTTPBadRequest):
        c._validate_cart_size()
