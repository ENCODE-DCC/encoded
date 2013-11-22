
from pyramid.view import view_config
from ..contentbase import (
    Root
)
from pyelasticsearch import ElasticSearch
es = ElasticSearch('http://localhost:9200')


def get_filtered_query(term, fields):
    return {
        'query': {
            'filtered': {
                'query': {
                    'queryString': {
                        'query': term
                    }
                },
                'filter': {
                    'and': {
                        'filters': []
                    }
                }
            }
        },
        'facets': {},
        'fields': fields
    }


def get_query(term, fields):
    return {
        'query': {
            'query_string': {
                'query': term
            }
        },
        'facets': {},
        'fields': fields
    }


@view_config(name='search', context=Root, request_method='GET', permission='search')
def search(context, request):
    ''' Search view connects to ElasticSearch and returns the results'''

    result = context.__json__(request)
    params = request.params
    root = request.root
    result.update({
        '@id': '/search/',
        '@type': ['search'],
        'title': 'Search',
        'facets': [],
        '@graph': [],
        'columns': {},
        'count': {},
        'filters': [],
        'notification': ''
    })

    if 'limit' in params:
        size = 999999
    else:
        size = 100

    try:
        # Wrong way adding wildcards, analyzer should b configured for this functionality
        search_term = params['searchTerm'] + '*'
    except:
        if 'type' in params:
            if params['type'] == '*':
                result['notification'] = 'Please enter search term'
                return result
            else:
                search_term = "*"
        else:
            result['notification'] = 'Please enter search term'
            return result

    try:
        search_type = params['type']
    except:
        if not search_term:
            result['notification'] = 'Please enter search term'
            return result
        
        indices = ['antibody_approval', 'biosample', 'experiment', 'target']
        fields = ['@id', '@type']
        for index in indices:
            collection = root[index]
            result['columns'].update(collection.columns)
            for column in collection.columns:
                fields.append(column)

        query = get_query(search_term, list(set(fields)))
        
        s = es.search(query, index=indices, size=99999)
        result['count']['targets'] = result['count']['antibodies'] = result['count']['experiments'] = result['count']['biosamples'] = 0
        for hit in s['hits']['hits']:
            result_hit = hit['fields']
            if result_hit['@type'][0] == 'antibody_approval':
                result['count']['antibodies'] += 1
            elif result_hit['@type'][0] == 'biosample':
                result['count']['biosamples'] += 1
            elif result_hit['@type'][0] == 'experiment':
                result['count']['experiments'] += 1
            elif result_hit['@type'][0] == 'target':
                result['count']['targets'] += 1

            result_hit['score'] = hit['_score']
            result['@graph'].append(result_hit)
        
        if len(result['@graph']):
            result['notification'] = 'Success'
        else:
            result['notification'] = 'No results found'
        return result
    else:
        search_type = params['type']
        if search_term == '*' and search_type == '*':
            result['notification'] = 'Please enter search terme'
            return result
        
        # Building query for filters
        collections = root.by_item_type
        fields = ['@id', '@type']
        for collection_name in collections:
            if search_type == collection_name:
                collection = root[collection_name]
                index = collection_name
                schema = collection.schema
                result['columns'] = columns = collection.columns
                break
        
        for column in columns:
            fields.append(column)
        
        # Builds filtered query which supports multiple facet selection
        query = get_filtered_query(search_term, fields)
        regular_query = 1
        for key, value in params.iteritems():
            if key not in ['type', 'searchTerm', 'limit', 'format']:
                regular_query = 0
                if value == 'other':
                    query['query']['filtered']['filter']['and']['filters'].append({'missing': {'field': key}})
                else:
                    query['query']['filtered']['filter']['and']['filters'].append({'bool': {'must': {'term': {key + '.untouched': value}}}})
                result['filters'].append({key: value})
        
        if regular_query:
            query = get_query(search_term, fields)

        if search_type == 'biosample' and search_term == '*':
            query['sort'] = {'accession': {'order': 'asc'}}
        elif search_type == 'target' and search_term == '*':
            query['sort'] = {'gene_name.untouched': {'ignore_unmapped': 'true', 'order': 'asc'}}
        elif search_type == 'antibody_approval' and search_term == '*':
            query['sort'] = {'status': {'order': 'asc'}}
        elif search_type == 'experiment' and search_term == '*':
            query['sort'] = {'accession': {'order': 'asc'}}

        if 'facets' in schema:
            for facet in schema['facets']:
                face = {'terms': {'field': '', 'size': 99999}}
                face['terms']['field'] = facet[facet.keys()[0]] + '.untouched'
                query['facets'][facet.keys()[0]] = face
                for f in result['filters']:
                    if facet[facet.keys()[0]] == f.keys()[0]:
                        del(query['facets'][facet.keys()[0]])
        else:
            del(query['facets'])

        # Execute the query
        results = es.search(query, index=index, size=size)
        
        # Loading facets in to the results
        if 'facets' in results:
            facet_results = results['facets']
            for facet in schema['facets']:
                if facet.keys()[0] in facet_results:
                    face = {}
                    face['field'] = facet[facet.keys()[0]]
                    face[facet.keys()[0]] = []
                    for term in facet_results[facet.keys()[0]]['terms']:
                        face[facet.keys()[0]].append({term['term']: term['count']})
                    if facet_results[facet.keys()[0]]['missing'] != 0:
                        face[facet.keys()[0]].append({'other': facet_results[facet.keys()[0]]['missing']})
                    result['facets'].append(face)

        for hit in results['hits']['hits']:
            result_hit = hit['fields']
            result_hit['score'] = hit['_score']
            result['@graph'].append(result_hit)

        result['count'][root.by_item_type[collection_name].__name__] = results['hits']['total']
        if len(result['@graph']):
            result['notification'] = 'Success'
        else:
            result['notification'] = 'No results found'
        return result
