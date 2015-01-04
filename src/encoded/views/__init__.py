import copy
import os
from collections import OrderedDict
from pyramid.httpexceptions import HTTPNotFound
from pyramid.view import view_config
from pyramid.response import Response
from ..contentbase import (
    Root,
    location_root,
)
from ..embedding import embed
from .visualization import generate_batch_hubs


def includeme(config):
    config.registry['encoded.processid'] = os.getppid()
    config.add_route('search', '/search{slash:/?}')
    config.add_route('schema', '/profiles/{item_type}.json')
    config.add_route('jsonld_context', '/terms/')
    config.add_route('jsonld_context_no_slash', '/terms')
    config.add_route('jsonld_term', '/terms/{term}')
    config.add_route('batch_hub', '/batch_hub/{search_params}/{txt}')
    config.add_route('batch_hub:trackdb', '/batch_hub/{search_params}/{assembly}/{txt}')
    config.add_route('graph_dot', '/profiles/graph.dot')
    config.add_route('graph_svg', '/profiles/graph.svg')
    config.scan()


@location_root
class EncodedRoot(Root):
    properties = {
        'title': 'Home',
        'portal_title': 'ENCODE',
    }


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


@view_config(route_name='schema', request_method='GET')
def schema(context, request):
    item_type = request.matchdict['item_type']
    try:
        collection = context.by_item_type[item_type]
    except KeyError:
        raise HTTPNotFound(item_type)

    schema = copy.deepcopy(collection.Item.schema)
    properties = OrderedDict()
    for k, v in schema['properties'].items():
        if 'permission' in v:
            if not request.has_permission(v['permission'], collection):
                continue
        properties[k] = v
    schema['properties'] = properties
    return schema


@view_config(route_name='batch_hub')
@view_config(route_name='batch_hub:trackdb')
def batch_hub(context, request):
    ''' View for batch track hubs '''
    return Response(generate_batch_hubs(context, request), content_type='text/plain')
