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
from ..cart_view import (
    get_cart_objects_by_user,
    filter_carts_to_visible,
    CART_USER_MAX,
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
        'current': [(Allow, 'role.owner', ['view', 'edit'])] + ALLOW_CURRENT,
        'deleted': [(Allow, 'role.owner', ['edit'])] + DELETED,
        'disabled': [(Allow, 'role.owner', ['view', 'edit'])] + ONLY_ADMIN_VIEW,
    }

    def __ac_local_roles__(self):
        owner = 'userid.%s' % self.properties['submitted_by']
        return {
            owner: 'role.owner'
        }

    class Collection(Item.Collection):
        pass


def _get_carts_by_user(request, userid, blocked_statuses=[]):
    request.datastore = 'database'
    return [
        request.resource_path(v, '')
        for k, v in request.registry[COLLECTIONS]['cart'].items()
        if v.properties['submitted_by'] == userid and not v.properties['status'] in blocked_statuses
    ]


def _create_cart(request, user, name=None, identifier=None, status=None):
    carts = request.registry[COLLECTIONS]['cart']
    user_props = request.embed(request.resource_path(user), '@@object')
    cart_name = name if name else '{} cart'.format(user_props['title'])
    initial_cart = {
        'submitted_by': str(user.uuid),
        'status': status or 'current',
        'name': cart_name,
        'elements': []
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


@view_config(context=Cart.Collection, request_method='GET', permission='save-carts', name='get-cart')
def get_or_create_cart_by_user(context, request):
    userid = [
        p.replace('userid.', '')
        for p in request.effective_principals
        if p.startswith('userid.')
    ]
    if not userid:
        raise HTTPBadRequest()
    else:
        userid = userid[0]
    user = request.registry[COLLECTIONS]['user'].get(userid)
    if not user:
        raise HTTPBadRequest()
    carts = _get_carts_by_user(request, userid, ['disabled', 'deleted '])
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
    userid = [
        p.replace('userid.', '')
        for p in request.effective_principals
        if p.startswith('userid.')
    ]
    if not userid:
        raise HTTPBadRequest()
    else:
        userid = userid[0]
    user = request.registry[COLLECTIONS]['user'].get(userid)
    if not user:
        raise HTTPBadRequest()
    cart_name = None
    user_carts = get_cart_objects_by_user(request, userid)
    visible_user_carts = filter_carts_to_visible(request, user_carts)
    countable_carts = [
        cart
        for cart in visible_user_carts
        if cart['status'] != 'disabled'
    ]
    cart_atids = [cart['@id'] for cart in visible_user_carts] if visible_user_carts else []
    cart_status = request.json.get('status', None)
    cart_name = request.json.get('name', '').strip()
    # User writing a new cart; check for cart overflow and naming conflicts
    if len(countable_carts) >= CART_USER_MAX:
        msg = 'Users cannot have more than {} carts'.format(CART_USER_MAX)
        raise HTTPBadRequest(explanation=msg)
    elif next((cart for cart in visible_user_carts if (cart['status'] != 'deleted' and
            cart['status'] != 'disabled' and
            cart['name'].strip().upper() == cart_name.upper())), None):
        msg = 'A cart with the name "{}" already exists'.format(cart_name)
        raise HTTPBadRequest(explanation=msg)
    cart_identifier = request.json.get('identifier', None)
    cart = _create_cart(request, user, cart_name, cart_identifier, cart_status)
    request.response.status = 200
    return {
        'status': 'success',
        '@type': ['result'],
        '@graph': [cart] if cart else cart_atids,
    }
