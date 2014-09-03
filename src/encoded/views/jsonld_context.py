from pyramid.httpexceptions import HTTPNotFound
from pyramid.view import view_config

@view_config(route_name='jsonld_context', request_method='GET')
def jsonld_context(context, request):
    item_type = request.matchdict['item_type']
    try:
        collection = context.by_item_type[item_type]
    except KeyError:
        raise HTTPNotFound(item_type)
    return collection.jsonld_context
