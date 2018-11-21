from snovault import (
    collection,
    load_schema,
)
from snovault import COLLECTIONS
from snovault.crud_views import create_item
from pyramid.httpexception import HTTPBadRequest
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
        c['@id']
        for c in request.embed('/carts/?datastore=database&limit=all&remove=elements')
        if c['submitted_by'] == '/users/{}/'.format(userid)
    ]


def _create_cart(request, user):
    carts = request.registry[COLLECTIONS]['carts']
    cart = create_item(
        carts.type_info,
        request,
        {
            'submitted_by': user.path,
            'status': 'current',
            'name': '{} cart'.format(user.properties['title'])
        }
    )
    return cart.path


@view_config(context=Cart.Collection, request_method='GET', permission='save-carts')
def get_or_create_cart_by_user(context, request):
    userid = request.authenticated_userid
    if not userid or '.' not in userid:
        raise HTTPBadRequest()
    user = request.registry[COLLECTIONS]['users'][userid.split('.')[0]]
    if not user:
        raise HTTPBadRequest()
    carts = _get_carts_by_user(request, userid)
    if not carts:
        cart = _create_cart(user)
    request.response.status = 200
    return {
        'status': 'success',
        '@type': ['result'],
        '@graph': carts or [cart]
    }
