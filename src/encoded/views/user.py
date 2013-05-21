from pyramid.view import (
    view_config,
)
from pyramid.security import (
    Allow,
    Authenticated,
    Deny,
    Everyone,
    authenticated_userid,
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

    class Item(Collection.Item):
        links = {
            'labs': [
                {'href': '/labs/{lab_uuid}', 'templated': True,
                 'repeat': 'lab_uuid lab_uuids'}
            ]
        }
        keys = ['email']

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


@view_config(context=Root, name='current-user', request_method='GET',
             effective_principals=[Authenticated])
def current_user(request):
    for principal in effective_principals(request):
        if principal.startswith('userid:'):
            break
    else:
        raise AssertionError('User not found')
    namespace, userid = principal.split(':', 1)
    collection = request.root.by_item_type[User.item_type]
    path = request.resource_path(collection, userid)
    subreq = make_subrequest(request, path)
    subreq.override_renderer = 'null_renderer'
    result = request.invoke_subrequest(subreq)
    login = authenticated_userid(request)
    namespace, userid = login.split(':', 1)
    if namespace == 'mailto':
        result = result.copy()
        result['_persona_email'] = userid
    return result


@view_config(context=Root, name='current-user', request_method='GET')
def current_user_anonymous(request):
    return {}
