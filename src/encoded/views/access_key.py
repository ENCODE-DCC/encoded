from pyramid.security import effective_principals
from pyramid.view import view_config
from pyramid.security import (
    Allow,
    Authenticated,
    Deny,
    Everyone,
)
from ..authentication import (
    generate_password,
    generate_user,
    CRYPT_CONTEXT,
)
from ..schema_utils import (
    load_schema,
    schema_validator,
)
from ..contentbase import (
    Collection,
    Root,
    collection_add,
    item_edit,
    item_view,
    item_view_edit,
    item_view_raw,
    location,
    validate_item_content_post,
    validate_item_content_put,
)
from ..validation import ValidationFailure


@location('access-keys')
class AccessKey(Collection):
    item_type = 'access_key'
    schema = load_schema('access_key.json')
    unique_key = 'access_key:access_key_id'
    properties = {
        'title': 'Access keys',
        'description': 'Programmatic access keys',
    }

    __acl__ = [
        (Allow, Authenticated, 'traverse'),
        (Allow, 'remoteuser.INDEXER', 'traverse'),
        (Allow, 'remoteuser.EMBED', 'traverse'),
        (Deny, Everyone, 'traverse'),
        (Allow, 'role.owner', ['edit', 'view']),
        (Allow, 'group.admin', 'view'),
        (Allow, 'group.read-only-admin', 'view'),
        (Allow, 'remoteuser.INDEXER', 'view'),
        (Allow, 'remoteuser.EMBED', 'view'),
        (Deny, Everyone, 'view'),
    ]

    class Item(Collection.Item):
        keys = ['access_key_id']
        name_key = 'access_key_id'

        def __ac_local_roles__(self):
            owner = 'userid.%s' % self.properties['user']
            return {owner: 'role.owner'}


@view_config(context=AccessKey, permission='add', request_method='POST',
             validators=[validate_item_content_post])
def access_key_add(context, request):
    crypt_context = request.registry[CRYPT_CONTEXT]

    if 'access_key_id' not in request.validated:
        request.validated['access_key_id'] = generate_user()

    if 'user' not in request.validated:
        request.validated['user'], = [
            principal.split('.', 1)[1]
            for principal in effective_principals(request)
            if principal.startswith('userid.')
        ]

    password = None
    if 'secret_access_key_hash' not in request.validated:
        password = generate_password()
        request.validated['secret_access_key_hash'] = crypt_context.encrypt(password)

    result = collection_add(context, request)

    if password is None:
        result['secret_access_key'] = None
    else:
        result['secret_access_key'] = password

    result['access_key_id'] = request.validated['access_key_id']
    result['description'] = request.validated['description']
    return result


@view_config(name='reset-secret', context=AccessKey.Item, permission='edit',
             request_method='POST', subpath_segments=0)
def access_key_reset_secret(context, request):
    request.validated = context.properties.copy()
    crypt_context = request.registry[CRYPT_CONTEXT]
    password = generate_password()
    new_hash = crypt_context.encrypt(password)
    request.validated['secret_access_key_hash'] = new_hash
    # Don't embed the access_key as the subsequent inclusion will fail
    result = item_edit(context, request, render=False)
    result['secret_access_key'] = password
    return result


@view_config(name='disable-secret', context=AccessKey.Item, permission='edit',
             request_method='POST', subpath_segments=0)
def access_key_disable_secret(context, request):
    request.validated = context.properties.copy()
    crypt_context = request.registry[CRYPT_CONTEXT]
    new_hash = crypt_context.encrypt('', scheme='unix_disabled')
    request.validated['secret_access_key_hash'] = new_hash
    result = item_edit(context, request, render=False)
    result['secret_access_key'] = None
    return result


@view_config(context=AccessKey.Item, permission='edit', request_method='PUT',
             validators=[validate_item_content_put])
def access_key_edit(context, request):
    new_properties = context.properties.copy()
    new_properties.update(request.validated)
    request.validated = new_properties
    return item_edit(context, request)


def remove_secret_access_key_hash(properties):
    try:
        del properties['secret_access_key_hash']
    except KeyError:
        pass
    return properties


@view_config(context=AccessKey.Item, permission='view', request_method='GET')
def access_key_view(context, request):
    return remove_secret_access_key_hash(item_view(context, request))


@view_config(context=AccessKey.Item, permission='view_raw', request_method='GET',
             request_param=['frame=raw'])
def access_key_view_raw(context, request):
    return remove_secret_access_key_hash(item_view_raw(context, request))


@view_config(context=AccessKey.Item, permission='view_raw', request_method='GET',
             request_param=['frame=edit'])
def access_key_view_raw(context, request):
    return remove_secret_access_key_hash(item_view_edit(context, request))


@view_config(name='edw_key_create', context=Root, subpath_segments=0,
             request_method='POST', permission='edw_key_create',
             validators=[schema_validator('edw_key.json')])
def edw_key_create(context, request):
    email = request.validated['email']
    username = request.validated['username']
    pwhash = request.validated['pwhash']

    users = request.root['users']
    try:
        user = users[email]
    except KeyError:
        msg = "User not found for %r" % email
        request.errors.add('body', ['email'], msg)

    if not username:
        msg = "username must not be blank"
        request.errors.add('body', ['username'], msg)
    else:
        collection = request.root['access-keys']
        try:
            collection[username]
        except KeyError:
            pass
        else:
            msg = "username already exists"
            request.errors.add('body', ['username'], msg)

    if request.errors:
        raise ValidationFailure()

    request.validated.clear()
    request.validated['schema_version'] = '1'
    request.validated['access_key_id'] = username
    request.validated['secret_access_key_hash'] = pwhash
    request.validated['user'] = str(user.uuid)
    request.validated['description'] = ''

    collection_add(collection, request)
    return {'status': 'success'}


@view_config(name='edw_key_update', context=Root, subpath_segments=0,
             request_method='POST', permission='edw_key_update',
             validators=[schema_validator('edw_key.json')])
def edw_key_update(request):
    email = request.validated['email']
    username = request.validated['username']
    pwhash = request.validated['pwhash']

    users = request.root['users']
    try:
        user = users[email]
    except KeyError:
        msg = "User not found for %r" % email
        request.errors.add('body', ['email'], msg)

    collection = request.root['access-keys']
    try:
        access_key = collection[username]
    except KeyError:
        msg = "username not found"
        request.errors.add('body', ['username'], msg)

    if request.errors:
        raise ValidationFailure()

    request.validated.clear()
    request.validated.update(access_key.properties)
    request.validated['secret_access_key_hash'] = pwhash
    request.validated['user'] = str(user.uuid)

    item_edit(access_key, request)
    return {'status': 'success'}
