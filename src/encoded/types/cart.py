from snovault import (
    collection,
    load_schema,
)
from snovault import COLLECTIONS
from snovault.crud_views import create_item
from pyramid.httpexceptions import HTTPBadRequest
from pyramid.security import (
    Allow,
    Authenticated,
)
from pyramid.view import view_config
from .base import (
    Item,
    DELETED,
    ALLOW_CURRENT,
    ONLY_ADMIN_VIEW,
)
from encoded.cart_view import (
    get_userid,
    get_cart_objects_by_user,
    CART_USER_MAX,
    CART_ADMIN_MAX,
)


@collection(
    name='carts',
    unique_key='cart:identifier',
    properties={
        'title': 'Cart',
        'description': 'Listing of cart contents',
    },
    acl=[
        (Allow, Authenticated, 'save-carts'),
    ]
)
class Cart(Item):
    item_type = 'cart'
    schema = load_schema('encoded:schemas/cart.json')
    name_key = 'identifier'

    STATUS_ACL = {
        'unlisted': [(Allow, 'role.owner', ['view', 'edit'])] + ALLOW_CURRENT,
        'listed': [(Allow, 'role.owner', ['view', 'edit'])] + ALLOW_CURRENT,
        'deleted': [(Allow, 'role.owner', ['edit'])] + DELETED,
        'released': ALLOW_CURRENT,
        'revoked': ALLOW_CURRENT
    }

    embedded = [
        'submitted_by',
        'submitted_by.lab'
    ]

    def __ac_local_roles__(self):
        owner = 'userid.%s' % self.properties['submitted_by']
        return {
            owner: 'role.owner'
        }

    class Collection(Item.Collection):
        pass


def _create_cart(request, user, name=None, identifier=None, status=None):
    carts = request.registry[COLLECTIONS]['cart']
    user_props = request.embed(request.resource_path(user), '@@object')
    cart_name = name or 'Default Cart'
    initial_cart = {
        'submitted_by': str(user.uuid),
        'status': status or 'unlisted',
        'name': cart_name,
        'locked': False,
        'elements': [],
        'file_views': [],
    }
    if identifier:
        initial_cart['identifier'] = identifier
    cart = create_item(
        carts.type_info,
        request,
        initial_cart,
    )
    cart_path = request.resource_path(cart)
    return cart_path


def _get_user(request, userid):
    user = request.registry[COLLECTIONS]['user'].get(userid)
    if not user:
        raise HTTPBadRequest()
    return user


@view_config(context=Cart.Collection, request_method='GET', permission='save-carts', name='get-cart')
def get_or_create_cart_by_user(context, request):
    userid = get_userid(request)
    user = _get_user(request, userid)
    carts = get_cart_objects_by_user(
        request,
        userid,
        blocked_statuses=['deleted']
    )
    carts = [cart['@id'] for cart in carts]
    if not carts:
        cart = _create_cart(request, user)
    request.response.status = 200
    return {
        'status': 'success',
        '@type': ['result'],
        '@graph': carts or [cart]
    }


@view_config(context=Cart.Collection, request_method='PUT', permission='save-carts', name='put-cart')
def create_cart_by_user(context, request):
    userid = get_userid(request)
    user = _get_user(request, userid)
    is_admin = 'group.admin' in request.effective_principals 
    blocked_statuses = ['deleted'] if not is_admin else []
    cart_max_count = CART_ADMIN_MAX if is_admin else CART_USER_MAX
    carts = get_cart_objects_by_user(request, userid, blocked_statuses=blocked_statuses)
    cart_status = request.json.get('status')
    cart_name = request.json.get('name', '').strip()
    # User writing a new cart; check for cart overflow and naming conflicts
    countable_carts = [
        cart
        for cart in carts
        if cart['status'] not in ['deleted']
    ]
    if len(countable_carts) >= cart_max_count:
        msg = 'Users cannot have more than {} carts'.format(cart_max_count)
        raise HTTPBadRequest(explanation=msg)
    conflicting_names = [
        cart
        for cart in carts
        if (cart['status'] not in ['deleted'] and
            cart['name'].strip().upper() == cart_name.upper())
    ]
    if conflicting_names:
        msg = 'A cart with the name "{}" already exists'.format(cart_name)
        raise HTTPBadRequest(explanation=msg)
    cart_identifier = request.json.get('identifier')
    cart = _create_cart(
        request,
        user,
        name=cart_name,
        identifier=cart_identifier,
        status=cart_status
    )
    request.response.status = 200
    return {
        'status': 'success',
        '@type': ['result'],
        '@graph': [cart],
    }
