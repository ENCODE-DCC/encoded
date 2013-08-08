
from pyramid.view import view_config
from ..contentbase import (
    Root
)
from pyelasticsearch import ElasticSearch
from ..schema_utils import (
    load_schema,
)

es = ElasticSearch('http://localhost:9200')
schemas = {
    'biosamples': 'biosample.json',
    'experiments': 'experiment.json',
    'antibodies': 'antibody_approval.json',
    'targets': 'target.json'
}


def queryBuilder(index, queryTerm):
    ''' Builds ElasticSearch query weith facets '''

    query = {'query': {'query_string': {'query': queryTerm}}}
    schema = load_schema(schemas[index])
    facets = schema['facets']
    if len(facets.keys()):
        query['facets'] = {}
        for facet in facets:
            query['facets'][facet] = {'terms': {'field': ''}}
            query['facets'][facet]['terms']['field'] = facets[facet]
    return query


@view_config(name='search', context=Root, request_method='GET')
def search(context, request):
    result = context.__json__(request)
    result.update({
        '@id': '/search/',
        '@type': ['search'],
        'title': 'ElasticSearch View',
        '@graph': {}
    })
    items = {}
    queryTerm = request.params.get('searchTerm')
    if queryTerm:
        items['results'] = []
        items['count'] = {}
        items['facets'] = {}
        if len(request.params) == 1:
            indexes = ['biosamples', 'antibodies', 'experiments', 'targets']
            for index in indexes:
                s = es.search(queryTerm, index=index, size=1000)
                items['count'][index] = len(s['hits']['hits'])
                for data in s['hits']['hits']:
                    items['results'].append(data['_source'])
        else:
            index = request.params.get('type')
            s = es.search(queryBuilder(index, queryTerm), index=index, size=1000)
            items['count'][index] = len(s['hits']['hits'])
            facets = s['facets']
            for facet in facets:
                face = []
                for term in facets[facet]['terms']:
                    face.append({term['term']: term['count']})
                if len(face):
                    items['facets'][facet] = face

            for data in s['hits']['hits']:
                items['results'].append(data['_source'])
    result['@graph'] = items
    return result
