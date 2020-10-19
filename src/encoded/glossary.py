from pyramid.view import view_config


def includeme(config):
    config.add_route('glossary', '/glossary{slash:/?}')
    config.add_route('series_search', '/series-search{slash:/?}')
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


@view_config(route_name='series_search', request_method='GET', permission='search')
def glossary(context, request):
    result = {
        '@id': '/series-search/',
        '@type': ['SeriesSearch'],
        'title': 'Series search',
        '@graph': [],
        'columns': [],
        'notification': '',
        'filters': []
    }
    return result
