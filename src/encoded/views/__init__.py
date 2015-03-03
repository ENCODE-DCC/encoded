import os
from collections import OrderedDict
from pyramid.decorator import reify
from pyramid.httpexceptions import HTTPNotFound
from pyramid.view import view_config
from pyramid.response import Response
from ..contentbase import (
    Root,
    root,
)
from ..schema_formats import is_accession
from pyramid.security import (
    ALL_PERMISSIONS,
    Allow,
    Authenticated,
    Deny,
    Everyone,
)
from ..embedding import embed
from .visualization import generate_batch_hubs


def includeme(config):
    config.registry['encoded.processid'] = os.getppid()
    config.add_route('search', '/search{slash:/?}')
    config.add_route('schemas', '/profiles/')
    config.add_route('schema', '/profiles/{item_type}.json')
    config.add_route('jsonld_context', '/terms/')
    config.add_route('jsonld_context_no_slash', '/terms')
    config.add_route('jsonld_term', '/terms/{term}')
    config.add_route('batch_hub', '/batch_hub/{search_params}/{txt}')
    config.add_route('batch_hub:trackdb', '/batch_hub/{search_params}/{assembly}/{txt}')
    config.add_route('graph_dot', '/profiles/graph.dot')
    config.add_route('graph_svg', '/profiles/graph.svg')
    config.add_route('batch_download', '/batch_download/{search_params}')
    config.add_route('metadata', '/metadata/{search_params}/{tsv}')
    config.scan()


def acl_from_settings(settings):
    # XXX Unsure if any of the demo instance still need this
    acl = []
    for k, v in settings.items():
        if k.startswith('allow.'):
            action = Allow
            permission = k[len('allow.'):]
            principals = v.split()
        elif k.startswith('deny.'):
            action = Deny
            permission = k[len('deny.'):]
            principals = v.split()
        else:
            continue
        if permission == 'ALL_PERMISSIONS':
            permission = ALL_PERMISSIONS
        for principal in principals:
            if principal == 'Authenticated':
                principal = Authenticated
            elif principal == 'Everyone':
                principal = Everyone
            acl.append((action, principal, permission))
    return acl


@root
class EncodedRoot(Root):
    properties = {
        'title': 'Home',
        'portal_title': 'ENCODE',
    }

    @reify
    def __acl__(self):
        acl = acl_from_settings(self.registry.settings) + [
            (Allow, Everyone, ['list', 'search']),
            (Allow, 'group.submitter', ['search_audit', 'audit']),
            (Allow, 'group.admin', ALL_PERMISSIONS),
            (Allow, 'group.forms', ('forms',)),
            # Avoid schema validation errors during audit
            (Allow, 'remoteuser.EMBED', 'import_items'),
        ] + Root.__acl__
        return acl

    def get(self, name, default=None):
        resource = super(EncodedRoot, self).get(name, None)
        if resource is not None:
            return resource
        resource = self.connection.get_by_unique_key('page:location', name)
        if resource is not None:
            return resource
        if is_accession(name):
            resource = self.connection.get_by_unique_key('accession', name)
            if resource is not None:
                return resource
        if ':' in name:
            resource = self.connection.get_by_unique_key('alias', name)
            if resource is not None:
                return resource
        return default


@view_config(context=Root, request_method='GET')
def home(context, request):
    result = context.__json__(request)
    result.update({
        '@id': request.resource_path(context),
        '@type': ['portal'],
        # 'login': {'href': request.resource_path(context, 'login')},
    })

    try:
        result['default_page'] = embed(request, '/pages/homepage/@@page', as_user=True)
    except KeyError:
        pass

    return result


def _filtered_schema(collection, request):
    schema = collection.type_info.schema

    properties = OrderedDict()
    for k, v in schema['properties'].items():
        if 'permission' in v:
            if not request.has_permission(v['permission'], collection):
                continue
        properties[k] = v
    schema['properties'] = properties
    return schema


@view_config(route_name='schema', request_method='GET')
def schema(context, request):
    item_type = request.matchdict['item_type']
    try:
        collection = context.by_item_type[item_type]
    except KeyError:
        raise HTTPNotFound(item_type)

    return _filtered_schema(collection, request)


@view_config(route_name='schemas', request_method='GET')
def schemas(context, request):
    schemas = {}
    for typename, collection in context.by_item_type.items():
        schemas[typename] = _filtered_schema(collection, request)
    return schemas


@view_config(route_name='batch_hub')
@view_config(route_name='batch_hub:trackdb')
def batch_hub(context, request):
    ''' View for batch track hubs '''
    return Response(generate_batch_hubs(context, request), content_type='text/plain')
