from pyramid.view import (
    view_config,
)
from pyramid.security import (
    Allow,
    Deny,
    Everyone,
    effective_principals,
)
from .base import Item
from ..schema_utils import (
    load_schema,
)
from ..contentbase import (
    Root,
    calculated_property,
    item_view_object,
    collection,
)
from ..embedding import embed


@collection(
    name='users',
    unique_key='user:email',
    properties={
        'title': 'DCC Users',
        'description': 'Listing of current ENCODE DCC users',
    },
    acl=[
        (Allow, 'group.admin', ['list', 'view_details']),
        (Allow, 'group.read-only-admin', ['list', 'view_details']),
        (Allow, 'role.owner', ['edit', 'view_details']),
        (Allow, 'remoteuser.INDEXER', ['list', 'view']),
        (Allow, 'remoteuser.EMBED', ['list', 'view']),
        (Allow, Everyone, ['view']),
        (Deny, Everyone, ['list', 'view_details']),
    ])
class User(Item):
    item_type = 'user'
    schema = load_schema('user.json')

    @calculated_property(schema={
        "title": "Title",
        "type": "string",
    })
    def title(self, first_name, last_name):
        return u'{} {}'.format(first_name, last_name)

    def __ac_local_roles__(self):
        owner = 'userid.%s' % self.uuid
        return {owner: 'role.owner'}


@view_config(context=User, permission='view_details', request_method='GET',
             name='details')
def user_details_view(context, request):
    return item_view_object(context, request)


@view_config(context=User, permission='view', request_method='GET',
             name='object')
def user_basic_view(context, request):
    properties = item_view_object(context, request)
    filtered = {}
    for key in ['@id', '@type', 'uuid', 'lab', 'title']:
        try:
            filtered[key] = properties[key]
        except KeyError:
            pass
    return filtered


@view_config(context=Root, name='current-user', request_method='GET')
def current_user(request):
    request.environ['encoded.canonical_redirect'] = False
    for principal in effective_principals(request):
        if principal.startswith('userid.'):
            break
    else:
        return {}
    namespace, userid = principal.split('.', 1)
    collection = request.root.by_item_type[User.item_type]
    path = request.resource_path(collection, userid, '@@details')
    return embed(request, path, as_user=True)
