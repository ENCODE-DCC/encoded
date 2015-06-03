from pyramid.security import (
    Allow,
)
from pyramid.view import view_config
from contentbase import (
    Item,
    calculated_property,
    collection,
)
from ..types.base import paths_filtered_by_status
from contentbase.attachment import ItemWithAttachment


def includeme(config):
    config.scan(__name__)
    config.include('.testing_auditor')


@view_config(name='testing-user', request_method='GET')
def user(request):
    return {
        'authenticated_userid': request.authenticated_userid,
        'effective_principals': request.effective_principals,
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


@collection(
    'testing-downloads',
    properties={
        'title': 'Test download collection',
        'description': 'Testing. Testing. 1, 2, 3.',
    },
)
class TestingDownload(ItemWithAttachment):
    item_type = 'testing_download'
    schema = {
        'type': 'object',
        'properties': {
            'attachment': {
                'type': 'object',
                'properties': {
                    'type': {
                        'type': 'string',
                        'enum': ['image/png'],
                    }
                }
            }
        }
    }


@collection(
    'testing-keys',
    properties={
        'title': 'Test keys',
        'description': 'Testing. Testing. 1, 2, 3.',
    },
    unique_key='testing_accession',
)
class TestingKey(Item):
    item_type = 'testing_key'
    schema = {
        'type': 'object',
        'properties': {
            'name': {
                'type': 'string',
                'uniqueKey': True,
            },
            'accession': {
                'type': 'string',
                'uniqueKey': 'testing_accession',
            },
        }
    }


@collection('testing-link-sources')
class TestingLinkSource(Item):
    item_type = 'testing_link_source'
    schema = {
        'type': 'object',
        'properties': {
            'name': {
                'type': 'string',
            },
            'uuid': {
                'type': 'string',
            },
            'target': {
                'type': 'string',
                'linkTo': 'testing_link_target',
            },
            'status': {
                'type': 'string',
            },
        },
        'required': ['target'],
        'additionalProperties': False,
    }


@collection('testing-link-targets', unique_key='testing_link_target:name')
class TestingLinkTarget(Item):
    item_type = 'testing_link_target'
    name_key = 'name'
    schema = {
        'type': 'object',
        'properties': {
            'name': {
                'type': 'string',
                'uniqueKey': True,
            },
            'uuid': {
                'type': 'string',
            },
            'status': {
                'type': 'string',
            },
        },
        'additionalProperties': False,
    }
    rev = {
        'reverse': ('testing_link_source', 'target'),
    }
    embedded = [
        'reverse',
    ]

    @calculated_property(schema={
        "title": "Sources",
        "type": "array",
        "items": {
            "type": ['string', 'object'],
            "linkFrom": "testing_link_source.target",
        },
    })
    def reverse(self, request, reverse):
        return paths_filtered_by_status(request, reverse)


@collection(
    'testing-post-put-patch',
    acl=[
        (Allow, 'group.submitter', ['add', 'edit', 'view']),
    ],
)
class TestingPostPutPatch(Item):
    item_type = 'testing_post_put_patch'
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


@collection('testing-server-defaults')
class TestingServerDefault(Item):
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


@collection('testing-dependencies')
class TestingDependencies(Item):
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


@view_config(name='testing-render-error', request_method='GET')
def testing_render_error(request):
    return {
        '@type': ['testing_render_error', 'item'],
        '@id': request.path,
        'title': 'Item triggering a render error',
    }
