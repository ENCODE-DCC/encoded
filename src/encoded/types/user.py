# -*- coding: utf-8 -*-

from pyramid.httpexceptions import HTTPUnprocessableEntity
from pyramid.view import (
    view_config,
)
from pyramid.security import (
    Allow,
    Deny,
    Everyone,
)
from .base import (
    Item,
)
from snovault import (
    CONNECTION,
    calculated_property,
    collection,
    load_schema,
)
from snovault.calculated import calculate_properties
from snovault.resource_views import item_view_object
from snovault.util import expand_path
from snovault.crud_views import collection_add
from snovault.schema_utils import validate_request
from snovault.storage import User as AuthUser


ONLY_ADMIN_VIEW_DETAILS = [
    (Allow, 'group.admin', ['view', 'view_details', 'edit']),
    (Allow, 'group.read-only-admin', ['view', 'view_details']),
    (Allow, 'remoteuser.INDEXER', ['view']),
    (Allow, 'remoteuser.EMBED', ['view']),
    (Deny, Everyone, ['view', 'view_details', 'edit']),
]

USER_ALLOW_CURRENT = [
    (Allow, Everyone, 'view'),
] + ONLY_ADMIN_VIEW_DETAILS

USER_DELETED = [
    (Deny, Everyone, 'visible_for_edit')
] + ONLY_ADMIN_VIEW_DETAILS


@collection(
    name='users',
    unique_key='user:email',
    properties={
        'title': 'DCC Users',
        'description': 'Listing of current ENCODE DCC users',
    },
    acl=[])
class User(Item):
    item_type = 'user'
    schema = load_schema('encoded:schemas/user.json')
    # Avoid access_keys reverse link so editing access keys does not reindex content.
    embedded = [
        'lab',
    ]
    STATUS_ACL = {
        'current': [(Allow, 'role.owner', ['edit', 'view_details'])] + USER_ALLOW_CURRENT,
        'deleted': USER_DELETED,
        'replaced': USER_DELETED,
        'disabled': ONLY_ADMIN_VIEW_DETAILS,
    }

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
            "linkFrom": "AccessKey.user",
        },
    }, category='page')
    def access_keys(self, request):
        if not request.has_permission('view_details'):
            return
        uuids = self.registry[CONNECTION].get_rev_links(self.model, 'user', 'AccessKey')
        objects = (request.embed('/', str(uuid), '@@object') for uuid in uuids)
        return [obj for obj in objects if obj['status'] not in ('deleted', 'replaced')]


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


@view_config(context=User.Collection, permission='add', request_method='POST',
             physical_path="/users")
def user_add(context,request):
    '''
    if we have a password in our request, create and auth entry
    for the user as well
    '''
    #do we have valid data
    pwd = request.json.get('password', None)
    pwd_less_data = request.json.copy()

    if pwd is not None:
        del pwd_less_data['password']

    validate_request(context.type_info.schema, request, pwd_less_data)

    if request.errors:
        return HTTPUnprocessableEntity(json={'errors':request.errors},
                                     content_type='application/json')

    result = collection_add(context, request)
    if result:
        email = request.json.get('email')
        pwd = request.json.get('password', None)
        name = request.json.get('first_name')
        if pwd is not None:
            auth_user = AuthUser(email, pwd, name)
            db = request.registry['dbsession']
            db.add(auth_user)

            import transaction
            transaction.commit()

    return result

@calculated_property(context=User, category='user_action')
def impersonate(request):
    # This is assuming the user_action calculated properties
    # will only be fetched from the current_user view,
    # which ensures that the user represented by 'context' is also an effective principal
    if request.has_permission('impersonate'):
        return {
            'id': 'impersonate',
            'title': 'Impersonate User…',
            'href': '/#!impersonate-user',
        }


@calculated_property(context=User, category='user_action')
def profile(context, request):
    return {
        'id': 'profile',
        'title': 'Profile',
        'href': request.resource_path(context),
    }


@calculated_property(context=User, category='user_action')
def signout(context, request):
    return {
        'id': 'signout',
        'title': 'Sign out',
        'trigger': 'logout',
    }
