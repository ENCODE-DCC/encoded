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
        'disabled': [(Allow, 'role.owner', ['view', 'edit'])],
    }

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
    cart.properties['current'] = cart_path
    return cart_path


@view_config(context=Cart.Collection, request_method=('GET', 'PUT'), permission='save-carts', name='get-cart')
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
    cart_name = None
    all_carts = get_cart_objects_by_user(request, userid)
    countable_carts = [cart for cart in all_carts if cart['status'] != 'deleted' and cart['status'] != 'disabled']
    cart_atids = [cart['@id'] for cart in all_carts] if all_carts else []
    cart_status = None
    cart_name = None
    try:
        cart_status = request.json.get('status')
    except ValueError:
        pass
    try:
        cart_name = request.json.get('name').strip()
    except ValueError:
        pass

    # User writing a new cart; check for cart overflow and naming conflicts
    if request.method == 'PUT' and cart_status != 'disabled':
        # PUT creates new cart even if user already has carts. 'name' required in body.
        # Error if more non-deleted/non-disabled carts than allowed per user.
        if len(countable_carts) >= CART_USER_MAX:
            msg = 'Users cannot have more than {} carts'.format(CART_USER_MAX)
            raise HTTPBadRequest(explanation=msg)
        elif next((cart for cart in all_carts if cart['status'] != 'deleted' and cart['status'] != 'disabled' and cart['name'].strip().upper() == cart_name.upper()), None):
            msg = 'A cart with the name "{}" already exists'.format(cart_name)
            raise HTTPBadRequest(explanation=msg)

    # Create a cart if PUT request, or GET request when none exist
    cart = None
    if not countable_carts or request.method == 'PUT':
        # No carts exist or making an additional cart, the latter requiring a name.
        cart_identifier = None
        try:
            cart_identifier = request.json.get('identifier')
        except ValueError:
            pass
        cart = _create_cart(request, user, cart_name, cart_identifier, cart_status)

    request.response.status = 200
    return {
        'status': 'success',
        '@type': ['result'],
        '@graph': [cart] if cart else cart_atids,
    }
