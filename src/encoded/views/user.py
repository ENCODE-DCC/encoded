from pyramid.view import view_config
from pyramid.security import (
    Allow,
    Deny,
    Everyone,
)
from . import root
from ..schema_utils import (
    load_schema,
)
from ..contentbase import (
    Collection,
    item_view,
)
from ..storage import (
    DBSession,
    UserMap,
)


@root.location('users')
class User(Collection):
    schema = load_schema('colleague.json')
    properties = {
        'title': 'DCC Users',
        'description': 'Listing of current ENCODE DCC users',
    }

    __acl__ = [
        (Allow, 'group:admin', 'list'),
        (Allow, 'group:admin', 'view_details'),
        (Deny, Everyone, 'list'),
        (Deny, Everyone, 'view_details'),
    ]

    def after_add(self, item):
        email = item.model.statement.object.get('email')
        if email is None:
            return
        session = DBSession()
        login = 'mailto:' + email
        user_map = UserMap(login=login, userid=item.model.rid)
        session.add(user_map)

    class Item(Collection.Item):
        links = {
            'labs': [
                {'href': '/labs/{lab_uuid}', 'templated': True,
                 'repeat': 'lab_uuid lab_uuids'}
            ]
        }

        def __acl__(self):
            owner = 'userid:%s' % self.model.rid
            return [
                (Allow, owner, 'edit'),
                (Allow, owner, 'view_details'),
            ]


@view_config(context=User.Item, permission='view', request_method='GET',
             additional_permission='view_details')
def user_details_view(context, request):
    return item_view(context, request)


@view_config(context=User.Item, permission='view', request_method='GET')
def user_basic_view(context, request):
    properties = item_view(context, request)
    filtered = {}
    for key in ['_links', 'first_name', 'last_name']:
        filtered[key] = properties[key]
    return filtered
