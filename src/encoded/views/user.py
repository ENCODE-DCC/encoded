from pyramid.view import (
    view_config,
)
from pyramid.security import (
    Allow,
    Deny,
    Everyone,
    effective_principals,
)
from ..schema_utils import (
    load_schema,
)
from ..contentbase import (
    Collection,
    Root,
    item_view,
    location,
    make_subrequest,
)


@location('users')
class User(Collection):
    item_type = 'user'
    unique_key = 'user:email'
    schema = load_schema('user.json')
    properties = {
        'title': 'DCC Users',
        'description': 'Listing of current ENCODE DCC users',
    }

    __acl__ = [
        (Allow, 'group.admin', ['list', 'view_details']),
        (Allow, 'group.read-only-admin', ['list', 'view_details']),
        (Allow, 'role.owner', ['edit', 'view_details']),
        (Allow, 'remoteuser.INDEXER', ['list', 'view']),
        (Allow, Everyone, ['view', 'traverse']),
        (Deny, Everyone, ['list', 'view_details']),
    ]

    class Item(Collection.Item):
        keys = ['email']
        unique_key = 'user.email'
        template = {
            'title': '{first_name} {last_name}',
            '$templated': True,
        }

        def __ac_local_roles__(self):
            owner = 'userid.%s' % self.uuid
            return {owner: 'role.owner'}


@view_config(context=User.Item, permission='view', request_method='GET',
             additional_permission='view_details')
def user_details_view(context, request):
    return item_view(context, request)


@view_config(context=User.Item, permission='view', request_method='GET')
def user_basic_view(context, request):
    properties = item_view(context, request)
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
    path = request.resource_path(collection, userid)
    subreq = make_subrequest(request, path)
    subreq.override_renderer = 'null_renderer'
    return request.invoke_subrequest(subreq)
