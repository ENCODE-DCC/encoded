from pyramid.view import view_config
from contentbase.elasticsearch import ELASTIC_SEARCH


def includeme(config):
    config.add_route('region-search', '/region-search{slash:/?}')
    config.add_route('suggest', '/suggest{slash:/?}')
    config.scan(__name__)


@view_config(route_name='region-search', request_method='GET', permission='search')
def region_search(context, request):

    result = {
        '@id': '/region-search/',
        '@type': ['region-search'],
        'title': 'Region Search'
    }
    return result


@view_config(route_name='suggest', request_method='GET', permission='search')
def suggest(context, request):
    text = ''
    result = {
        '@id': '/suggest/' + ('?q=' + text),
        '@type': ['suggest'],
        'title': 'Suggest',
        '@graph': [],
    }
    if 'q' in request.params:
        text = request.params.get('q', '')
    else:
        return []
    es = request.registry[ELASTIC_SEARCH]
    query = {
        "suggester": {
            "text": text,
            "completion": {
                "field": "name_suggest",
                "size": 10
            }
        }
    }
    results = es.suggest(index='annotations', body=query)
    result['@id'] = '/suggest/' + ('?q=' + text)
    result['@graph'] = results['suggester'][0]['options']
    return result
