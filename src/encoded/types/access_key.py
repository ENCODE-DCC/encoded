from pyramid.view import view_config
from pyramid.security import (
    Allow,
    Deny,
    Authenticated,
    Everyone,
)
from pyramid.settings import asbool
from .base import (
    Item,
    DELETED,
    ONLY_ADMIN_VIEW,
)
from encoded.authentication import (
    generate_password,
    generate_user,
    CRYPT_CONTEXT,
)
from snovault import (
    collection,
    load_schema,
)
from snovault.crud_views import (
    collection_add,
    item_edit,
)
from snovault.validators import (
    validate_item_content_post,
)


@collection(
    name='access-keys',
    unique_key='access_key:access_key_id',
    properties={
        'title': 'Access keys',
        'description': 'Programmatic access keys',
    },
    acl=[
        (Allow, 'group.verified', 'add'),
        (Allow, 'group.admin', 'list'),
        (Allow, 'group.read-only-admin', 'list'),
        (Allow, 'remoteuser.INDEXER', 'list'),
        (Allow, 'remoteuser.EMBED', 'list'),
        (Deny, Everyone, 'list'),
    ])
class AccessKey(Item):
    item_type = 'access_key'
    schema = load_schema('encoded:schemas/access_key.json')
    name_key = 'access_key_id'

    STATUS_ACL = {
        'current': [(Allow, 'role.owner', ['view', 'edit'])] + ONLY_ADMIN_VIEW,
        'deleted': DELETED,
    }

    def __ac_local_roles__(self):
        owner = 'userid.%s' % self.properties['user']
        return {owner: 'role.owner'}

    def __json__(self, request):
        properties = super(AccessKey, self).__json__(request)
        del properties['secret_access_key_hash']
        return properties

    def update(self, properties, sheets=None):
        # make sure PUTs preserve the secret access key hash
        if 'secret_access_key_hash' not in properties:
            new_properties = self.properties.copy()
            new_properties.update(properties)
            properties = new_properties
        self._update(properties, sheets)

    class Collection(Item.Collection):
        pass


@view_config(context=AccessKey.Collection, permission='add', request_method='POST',
             validators=[validate_item_content_post])
def access_key_add(context, request):
    crypt_context = request.registry[CRYPT_CONTEXT]

    if 'access_key_id' not in request.validated:
        request.validated['access_key_id'] = generate_user()

    if 'user' not in request.validated:
        request.validated['user'], = [
            principal.split('.', 1)[1]
            for principal in request.effective_principals
            if principal.startswith('userid.')
        ]

    password = None
    if 'secret_access_key_hash' not in request.validated:
        password = generate_password()
        request.validated['secret_access_key_hash'] = crypt_context.hash(password)

    result = collection_add(context, request)

    if password is None:
        result['secret_access_key'] = None
    else:
        result['secret_access_key'] = password

    result['access_key_id'] = request.validated['access_key_id']
    result['description'] = request.validated['description']
    return result


@view_config(name='reset-secret', context=AccessKey, permission='edit',
             request_method='POST', subpath_segments=0)
def access_key_reset_secret(context, request):
    request.validated = context.properties.copy()
    crypt_context = request.registry[CRYPT_CONTEXT]
    password = generate_password()
    new_hash = crypt_context.hash(password)
    request.validated['secret_access_key_hash'] = new_hash
    result = item_edit(context, request, render=False)
    result['access_key_id'] = request.validated['access_key_id']
    result['secret_access_key'] = password
    return result


@view_config(context=AccessKey, permission='view_raw', request_method='GET',
             name='raw')
def access_key_view_raw(context, request):
    if asbool(request.params.get('upgrade', True)):
        properties = context.upgrade_properties()
    else:
        properties = context.properties.copy()
    del properties['secret_access_key_hash']
    return properties
