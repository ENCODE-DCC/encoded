
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
    params = request.params
    if 'searchTerm' in params:
        queryTerm = params.get('searchTerm')
        items['results'] = []
        items['count'] = {}
        items['facets'] = {}
        if params.get('type'):
            if 'type' in params:
                index = request.params.get('type')
                s = es.search(queryBuilder(index, queryTerm), index=index, size=1100)
                items['count'][index] = len(s['hits']['hits'])
                facets = s['facets']
                schema = load_schema(schemas[index])
                facet_keys = schema['facets']
                for facet in facets:
                    print facet
                    face = []
                    for term in facets[facet]['terms']:
                        face.append({term['term']: term['count'], 'field': facet_keys[facet]})
                    if len(face):
                        items['facets'][facet] = face

                for data in s['hits']['hits']:
                    items['results'].append(data['_source'])
        else:
            indexes = ['biosamples', 'antibodies', 'experiments', 'targets']
            for index in indexes:
                s = es.search(queryTerm, index=index, size=1100)
                items['count'][index] = len(s['hits']['hits'])
                for data in s['hits']['hits']:
                    items['results'].append(data['_source'])
        result['@graph'] = items
    return result
