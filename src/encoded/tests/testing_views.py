from pyramid.security import (
    Allow,
)
from pyramid.view import view_config
from ..contentbase import (
    Collection,
    location,
)
from ..views.download import ItemWithAttachment


def includeme(config):
    config.scan(__name__)
    config.include('.testing_auditor')


@view_config(name='testing-user', request_method='GET')
def user(request):
    from pyramid.security import (
        authenticated_userid,
        effective_principals,
    )
    return {
        'authenticated_userid': authenticated_userid(request),
        'effective_principals': effective_principals(request),
    }


@view_config(name='testing-allowed', request_method='GET')
def allowed(context, request):
    from pyramid.security import (
        has_permission,
        principals_allowed_by_permission,
    )
    permission = request.params.get('permission', 'view')
    return {
        'has_permission': bool(has_permission(permission, context, request)),
        'principals_allowed_by_permission': principals_allowed_by_permission(context, permission),
    }


@location('testing-downloads')
class TestingDownload(Collection):
    properties = {
        'title': 'Test download collection',
        'description': 'Testing. Testing. 1, 2, 3.',
    }

    class Item(ItemWithAttachment):
        pass


@location('testing-keys')
class TestingKey(Collection):
    properties = {
        'title': 'Test keys',
        'description': 'Testing. Testing. 1, 2, 3.',
    }
    unique_key = 'testing_accession'

    item_keys = [
        'name',
        {'name': 'testing_accession', 'value': '{accession}', '$templated': True},
    ]


@location('testing-link-sources')
class TestingLinkSource(Collection):
    item_type = 'testing_link_source'
    schema = {
        'type': 'object',
        'properties': {
            'target': {
                'type': 'string',
                'linkTo': 'testing_link_target',
            },
            'status': {
                'type': 'string',
            },
        }
    }
    properties = {
        'title': 'Test links',
        'description': 'Testing. Testing. 1, 2, 3.',
    }


@location('testing-link-targets')
class TestingLinkTarget(Collection):
    item_type = 'testing_link_target'
    schema = {
        'type': 'object',
        'properties': {
            'status': {
                'type': 'string',
            },
        }
    }
    properties = {
        'title': 'Test link targets',
        'description': 'Testing. Testing. 1, 2, 3.',
    }
    item_rev = {
        'reverse': ('testing_link_source', 'target'),
    }
    item_embedded = [
        'reverse',
    ]


@location('testing-post-put-patch')
class TestingPostPutPatch(Collection):
    item_type = 'testing_post_put_patch'
    __acl__ = [
        (Allow, 'group.submitter', ['add', 'edit']),
    ]
    schema = {
        'required': ['required'],
        'type': 'object',
        'properties': {
            "schema_version": {
                "type": "string",
                "pattern": "^\\d+(\\.\\d+)*$",
                "requestMethod": [],
                "default": "1",
            },
            "uuid": {
                "title": "UUID",
                "description": "",
                "type": "string",
                "format": "uuid",
                "permission": "import_items",
                "requestMethod": "POST",
            },
            'required': {
                'type': 'string',
            },
            'simple1': {
                'type': 'string',
                'default': 'simple1 default',
            },
            'simple2': {
                'type': 'string',
                'default': 'simple2 default',
            },
            'protected': {
                # This should be allowed on PUT so long as value is the same
                'type': 'string',
                'default': 'protected default',
                'permission': 'import_items',
            },
            'protected_link': {
                # This should be allowed on PUT so long as the linked uuid is
                # the same
                'type': 'string',
                'linkTo': 'testing_link_target',
                'permission': 'import_items',
            },
        }
    }
    properties = {
        'title': 'Test links',
        'description': 'Testing. Testing. 1, 2, 3.',
    }


@location('testing-server-defaults')
class TestingServerDefault(Collection):
    item_type = 'testing_server_default'
    schema = {
        'type': 'object',
        'properties': {
            'uuid': {
                'serverDefault': 'uuid4',
                'type': 'string',
            },
            'user': {
                'serverDefault': 'userid',
                'linkTo': 'user',
                'type': 'string',
            },
            'now': {
                'serverDefault': 'now',
                'format': 'date-time',
                'type': 'string',
            },
            'accession': {
                'serverDefault': 'accession',
                'accessionType': 'AB',
                'format': 'accession',
                'type': 'string',
            },
        }
    }
    properties = {
        'title': 'Test server defaults',
        'description': 'Testing. Testing. 1, 2, 3.',
    }

@location('testing-dependencies')
class TestingDependencies(Collection):
    item_type = 'testing_dependencies'
    schema = {
        'type': 'object',
        'dependencies': {
            'dep1': ['dep2'],
            'dep2': ['dep1'],
        },
        'properties': {
            'dep1': {
                'type': 'string',
            },
            'dep2': {
                'type': 'string',
                'enum': ['dep2'],
            },
        }
    }
    properties = {
        'title': 'Test dependencies',
        'description': 'Testing. Testing. 1, 2, 3.',
    }


@view_config(name='testing-render-error', request_method='GET')
def testing_render_error(request):
    return {
        '@type': ['testing_render_error', 'item'],
        '@id': request.path,
        'title': 'Item triggering a render error',
    }
