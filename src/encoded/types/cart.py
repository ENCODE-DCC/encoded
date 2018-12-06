from snovault import (
    collection,
    load_schema,
)
from snovault import COLLECTIONS
from snovault.crud_views import create_item
from pyramid.httpexceptions import HTTPBadRequest
from pyramid.security import (
    Allow,
)
from pyramid.view import view_config
from .base import (
    Item,
    DELETED,
    ALLOW_CURRENT,
    ONLY_ADMIN_VIEW,
)


@collection(
    name='carts',
    properties={
        'title': 'Cart',
        'description': 'Listing of cart contents',
    },
    acl=[
        (Allow, 'group.submitter', 'save-carts'),
    ]
)
class Cart(Item):
    item_type = 'cart'
    schema = load_schema('encoded:schemas/cart.json')

    STATUS_ACL = {
        'current': [(Allow, 'role.owner', ['view', 'edit'])] + ALLOW_CURRENT,
        'deleted': DELETED,
        'disabled': ONLY_ADMIN_VIEW,
    }

    def __ac_local_roles__(self):
        owner = 'userid.%s' % self.properties['submitted_by']
        return {
            owner: 'role.owner'
        }

    class Collection(Item.Collection):
        pass


def _get_carts_by_user(request, userid):
    return [
        request.resource_path(v, '')
        for k, v in request.registry[COLLECTIONS]['cart'].items()
        if v.properties['submitted_by'] == userid
    ]


def _create_cart(request, user):
    carts = request.registry[COLLECTIONS]['cart']
    user_props = request.embed(request.resource_path(user), '@@object')
    cart = create_item(
        carts.type_info,
        request,
        {
            'submitted_by': str(user.uuid),
            'status': 'current',
            'name': '{} cart'.format(user_props['title']),
            'elements': []
        }
    )
    return request.resource_path(cart)


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
    carts = _get_carts_by_user(request, userid)
    if not carts:
        cart = _create_cart(request, user)
    request.response.status = 200
    return {
        'status': 'success',
        '@type': ['result'],
        '@graph': carts or [cart]
    }
