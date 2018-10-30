from snovault import (
    collection,
    load_schema,
)
from pyramid.security import (
    Allow,
)
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
    })
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
