from pyramid.view import view_config
from pyramid.httpexceptions import HTTPBadRequest
from urllib.parse import (
    parse_qs,
    urlencode,
)

def includeme(config):
    config.add_route('glossary', '/glossary{slash:/?}')
    config.scan(__name__)

@view_config(route_name='glossary', request_method='GET', permission='search')
def glossary(context, request):
    result = {
        '@id': '/glossary/',
        '@type': ['Glossary'],
        'title': 'Glossary',
        '@graph': [],
        'columns': [],
        'notification': '',
        'filters': []
    }
    return result
