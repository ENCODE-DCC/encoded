
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

data = {
    'biosamples': ['accession', 'biosample_term_id', 'biosample_term_name', 'lab.title'],
    'experiments': ['accession', 'description', 'assay_term_name', 'lab.title'],
    'antibodies': ['antibody.accession', 'target.name', 'target.lab.title'],
    'targets': ['name', 'organism.name', 'lab.title']
}


def queryBuilder(params):
    ''' Builds ElasticSearch query weith facets '''

    schema = load_schema(schemas[params.get('type')])
    facets = schema['facets']

    if len(params) > 2:
        query = {'query': {}}
        query['query']['filtered'] = {}
        query['query']['filtered']['query'] = {'queryString': {"query": params.get('searchTerm')}}
        query['query']['filtered']['filter'] = {'bool': {'must': []}}
        query['fields'] = ['@id', '@type']
        query['fields'].extend(data[params.get('type')])
        for key, value in params.iteritems():
            if key != 'searchTerm' and key != 'type':
                query['query']['filtered']['filter']['bool']['must'].append({'term': {key: value}})
        if len(facets.keys()):
            query['facets'] = {}
            for facet in facets:
                query['facets'][facet] = {'terms': {'field': '', 'size': 1000}}
                query['facets'][facet]['terms']['field'] = facets[facet]
    else:
        query = {'query': {'query_string': {'query': params.get('searchTerm')}}}
        query['fields'] = ['@id', '@type']
        query['fields'].extend(data[params.get('type')])
        if len(facets.keys()):
            query['facets'] = {}
            for facet in facets:
                query['facets'][facet] = {'terms': {'field': '', 'size': 1000}}
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
        if params.get('searchTerm'):
            queryTerm = params.get('searchTerm')
            items['results'] = []
            items['count'] = {}
            items['facets'] = {}
            if params.get('type'):
                if 'type' in params:
                    index = params.get('type')
                    s = es.search(queryBuilder(params), index=index, size=1100)
                    items['count'][index] = len(s['hits']['hits'])
                    facets = s['facets']
                    schema = load_schema(schemas[index])
                    facet_keys = schema['facets']
                    for facet in facets:
                        face = []
                        for term in facets[facet]['terms']:
                            face.append({term['term']: term['count'], 'field': facet_keys[facet]})
                        if len(face):
                            items['facets'][facet] = face

                    for dataS in s['hits']['hits']:
                        items['results'].append(dataS['fields'])
            else:
                indexes = ['biosamples', 'antibodies', 'experiments', 'targets']
                query = {'query': {'query_string': {'query': params.get('searchTerm')}}}
                query['fields'] = ['@id', '@type']
                for index in indexes:
                    query['fields'].extend(data[index])
                    s = es.search(query, index=index, size=1100)
                    items['count'][index] = len(s['hits']['hits'])
                    for dataS in s['hits']['hits']:
                        items['results'].append(dataS['fields'])
        result['@graph'] = items
    else:
        schema = load_schema('biosample.json')
        facets = schema['facets']
        query = {'query': {'match_all': {}}}
        items['results'] = []
        items['count'] = {}
        items['facets'] = {}
        if len(facets.keys()):
            query['facets'] = {}
            for facet in facets:
                query['facets'][facet] = {'terms': {'field': '', 'size': 1000}}
                query['facets'][facet]['terms']['field'] = facets[facet]
        s = es.search(query, index='biosamples', size=1100)
        facet_results = s['facets']
        items['count']['biosamples'] = len(s['hits']['hits'])
        for facet in facet_results:
            face = []
            for term in facet_results[facet]['terms']:
                face.append({term['term']: term['count'], 'field': facets[facet]})
            if len(face):
                items['facets'][facet] = face
        result['@graph'] = items
    return result
