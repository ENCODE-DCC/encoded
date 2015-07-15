# -*- coding: utf-8 -*-

from pyramid.view import (
    view_config,
)
from pyramid.security import (
    Allow,
    Deny,
    Everyone,
    effective_principals,
)
from .base import (
    Item,
    paths_filtered_by_status,
)
from contentbase import (
    Root,
    calculated_property,
    collection,
    load_schema,
)
from contentbase.calculated import calculate_properties
from contentbase.resource_views import item_view_object
from contentbase.util import expand_path
import contentbase


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
    schema = load_schema('encoded:schemas/user.json')
    rev = {
        'access_keys': ('access_key', 'user'),
    }
    embedded = (
        'lab',
        'access_keys',
    )

    @calculated_property(schema={
        "title": "Title",
        "type": "string",
    })
    def title(self, first_name, last_name):
        return u'{} {}'.format(first_name, last_name)

    def __ac_local_roles__(self):
        owner = 'userid.%s' % self.uuid
        return {owner: 'role.owner'}

    @calculated_property(schema={
        "title": "Access Keys",
        "type": "array",
        "items": {
            "type": ['string', 'object'],
            "linkFrom": "access_key.user",
        },
    })
    def access_keys(self, request, access_keys):
        return paths_filtered_by_status(request, access_keys)


@view_config(context=User, permission='view', request_method='GET', name='page')
def user_page_view(context, request):
    if request.has_permission('view_details'):
        properties = item_view_object(context, request)
    else:
        item_path = request.resource_path(context)
        properties = request.embed(item_path, '@@object')
    for path in context.embedded:
        expand_path(request, properties, path)
    calculated = calculate_properties(context, request, properties, category='page')
    properties.update(calculated)
    return properties


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
    path = request.resource_path(collection, userid)
    user = request.embed(path, as_user=True)

    user_actions = calculate_properties(User, request, category='user_action')
    user['user_actions'] = list(user_actions.values()) if user_actions else []

    return user


@contentbase.calculated_property(context=User, category='user_action')
def impersonate(context, request):
    # This is assuming the user_action calculated properties
    # will only be fetched from the current_user view,
    # which ensures that the user represented by 'context' is also an effective principal
    if request.has_permission('impersonate'):
        return {
            'id': 'impersonate',
            'title': 'Impersonate User…',
            'href': '/#!impersonate-user',
        }
