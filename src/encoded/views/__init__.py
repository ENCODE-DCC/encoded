import os
from pyramid.httpexceptions import HTTPNotFound
from pyramid.view import view_config
from pyramid.response import Response
from ..contentbase import (
    Root,
    item_view,
    location_root,
)
from .visualization import generate_batch_hubs


def includeme(config):
    config.registry['encoded.processid'] = os.getppid()
    config.add_route('schema', '/profiles/{item_type}.json')
    config.add_route('jsonld_context', '/terms')
    config.add_route('graph', '/profiles/graph.dot')
    config.add_route('batch_hub', '/batch_hub/{search_params}/{txt}')
    config.add_route('batch_hub:trackdb', '/batch_hub/{search_params}/{assembly}/{txt}')
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

    homepage = context.get_by_unique_key('page:location', 'homepage')
    if homepage is not None:
        result['default_page'] = item_view(homepage, request)

    return result


@view_config(route_name='schema', request_method='GET')
def schema(context, request):
    item_type = request.matchdict['item_type']
    try:
        collection = context.by_item_type[item_type]
    except KeyError:
        raise HTTPNotFound(item_type)
    return collection.schema


@view_config(route_name='batch_hub')
@view_config(route_name='batch_hub:trackdb')
def batch_hub(context, request):
    ''' View for batch track hubs '''
    return Response(generate_batch_hubs(request), content_type='text/plain')
