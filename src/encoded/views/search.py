
from pyramid.view import view_config
from ..contentbase import (
    Root
)
from pyelasticsearch import ElasticSearch

es = ElasticSearch('http://localhost:9200')


@view_config(name='search', context=Root, request_method='GET')
def search(context, request):
    result = context.__json__(request)
    result.update({
        '@id': '/search/',
        '@type': ['search'],
        'title': 'ElasticSearch View',
        'items': {}
    })
    items = {}
    items['results'] = []
    items['count'] = {}
    queryTerm = request.params.get('searchTerm')
    if len(request.params) == 1:
        if queryTerm:
            indexes = ['biosamples', 'antibodies', 'experiments', 'targets']
            for index in indexes:
                s = es.search(queryTerm, index=index, size=1000)
                items['count'][index] = len(s['hits']['hits'])
                for data in s['hits']['hits']:
                    items['results'].append(data['_source'])
    elif len(request.params) > 1:
        index = request.params.get('index')
        s = es.search(queryTerm, index=index, size=1000)
        items['count'][index] = len(s['hits']['hits'])
        for data in s['hits']['hits']:
            items['results'].append(data['_source'])

    result['items'] = items
    return result
