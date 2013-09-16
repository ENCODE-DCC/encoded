import os
from pyramid.httpexceptions import HTTPNotFound
from pyramid.view import view_config
from random import randint
from ..contentbase import (
    Root,
    location_root,
)


def includeme(config):
    config.registry['encoded.processid'] = os.getppid()
    config.add_route('schema', '/profiles/{item_type}.json')
    config.add_route('graph', '/profiles/graph.dot')
    config.scan()


@location_root
class EncodedRoot(Root):
    properties = {
        'title': 'Home',
        'portal_title': 'ENCODE 3',
    }


@view_config(context=Root, request_method='GET')
def home(context, request):
    result = context.__json__(request)
    result.update({
        '@id': request.resource_path(context),
        '@type': ['portal'],
        # 'login': {'href': request.resource_path(context, 'login')},
    })
    return result


@view_config(route_name='schema', request_method='GET')
def schema(context, request):
    item_type = request.matchdict['item_type']
    try:
        collection = context.by_item_type[item_type]
    except KeyError:
        raise HTTPNotFound(item_type)
    return collection.schema
