import re
from pyramid.view import view_config
from ..contentbase import (
    Root
)
from ..indexing import ELASTIC_SEARCH

sanitize_search_string_re = re.compile(r'[\\\+\-\&\|\!\(\)\{\}\[\]\^\~\:\/\\\*\?]')


def get_filtered_query(term, fields, search_fields):
    return {
        'explain': True,
        'query': {
            'filtered': {
                'query': {
                    'queryString': {
                        'query': term,
                        'analyze_wildcard': True,
                        'analyzer': 'encoded_search_analyzer',
                        'default_operator': 'AND',
                        'fields': search_fields
                    }
                },
                'filter': {
                    'and': {
                        'filters': []
                    }
                }
            }
        },
        'highlight': {
            'fields': {
                '_all': {}
            }
        },
        'facets': {},
        'fields': fields
    }


def get_query(term, fields, search_fields):
    return {
        'explain': True,
        'query': {
            'query_string': {
                'query': term,
                'analyze_wildcard': True,
                'analyzer': 'encoded_search_analyzer',
                'default_operator': 'AND',
                'fields': search_fields
            }
        },
        'highlight': {
            'fields': {
                '_all': {}
            }
        },
        'facets': {},
        'fields': fields,
    }


def sanitize_search_string(text):
    return sanitize_search_string_re.sub(r'\\\g<0>', text)


@view_config(name='search', context=Root, request_method='GET', permission='view')
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
        'count': 0,
        'filters': [],
        'notification': ''
    })

    qs = request.environ.get('QUERY_STRING')
    if qs:
        result['@id'] = '/search/?%s' % qs

    es = request.registry[ELASTIC_SEARCH]
    if 'limit' in params:
        if params['limit'] == 'all':
            size = 99999
        else:
            if params['limit'].isdigit():
                size = params['limit']
            else:
                size = 100
    else:
        size = 100

    try:
        search_term = params['searchTerm'].strip()
        search_term = sanitize_search_string(search_term)
        # Handling whitespaces in the search term
        if not search_term:
            result['notification'] = 'Please enter search term'
            return result
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
        search_type = root.collections[params['type']].item_type
        collections = root.by_item_type.keys()
        # handling invalid item types
        if search_type not in collections:
            result['notification'] = '\'' + search_type + '\' is not a valid \'item type\''
            return result
    except:
        if not search_term:
            result['notification'] = 'Please enter search term'
            return result
        
        doc_types = ['antibody_approval', 'biosample', 'experiment', 'target', 'dataset']
        fields = ['object.@id', 'object.@type']
        search_fields = []

        for doc_type in doc_types:
            collection = root[doc_type]
            result['columns'].update(collection.columns)
            for column in collection.columns:
                fields.append('object.' + column)
            for value in collection.schema.get('boost_values', ()):
                search_fields.append('object.' + value)
                search_fields.append('object.' + value + '.standard^2')
                search_fields.append('object.' + value + '.untouched^3')
        
        query = get_query(search_term, list(set(fields)), search_fields)

        common_facets = [{'Data Type': 'object.@type.untouched'}]
        for facet in common_facets:
            face = {'terms': {'field': '', 'size': 99999}}
            face['terms']['field'] = facet[facet.keys()[0]]
            query['facets'][facet.keys()[0]] = face

        s = es.search(query, index='encoded', doc_type=doc_types, size=size)
        for hit in s['hits']['hits']:
            new_hit = {}
            for field in hit['fields']:
                new_hit[field[7:]] = hit['fields'][field]
            result['@graph'].append(new_hit)
        
        facet_results = s['facets']
        for facet in common_facets:
            if facet.keys()[0] in facet_results:
                face = {}
                face['field'] = 'type'
                face[facet.keys()[0]] = []
                for term in facet_results[facet.keys()[0]]['terms']:
                    if term['term'] in doc_types:
                        face[facet.keys()[0]].append({root.by_item_type[term['term']].__name__: term['count']})
                result['facets'].append(face)

        result['count'] = s['hits']['total']
        if len(result['@graph']):
            result['notification'] = 'Success'
        else:
            if len(search_term) < 3:
                result['notification'] = 'No results found. Search term should be at least 3 characters long.'
            else:
                result['notification'] = 'No results found'
        return result
    else:
        if search_term == '*' and search_type == '*':
            result['notification'] = 'Please enter search terme'
            return result

        # Building query for filters
        fields = ['object.@id', 'object.@type']
        search_fields = []
        collections = root.by_item_type
        for collection_name in collections:
            if search_type == collection_name:
                collection = root[collection_name]
                for value in collection.schema.get('boost_values', ()):
                    search_fields.append('object.' + value)
                    search_fields.append('object.' + value + '.standard^2')
                    search_fields.append('object.' + value + '.untouched^3')
                index = collection_name
                schema = collection.schema
                columns = result['columns'] = collection.columns
                break
        for column in columns:
            fields.append('object.' + column)

        # Builds filtered query which supports multiple facet selection
        query = get_filtered_query(search_term, fields, search_fields)
        regular_query = 1
        for key, value in params.iteritems():
            if key not in ['type', 'searchTerm', 'limit', 'format']:
                regular_query = 0
                if value == 'other':
                    query['query']['filtered']['filter']['and']['filters'].append({'missing': {'field': 'object.' + key}})
                else:
                    query['query']['filtered']['filter']['and']['filters'].append({'bool': {'must': {'term': {'object.' + key + '.untouched': value}}}})
                result['filters'].append({key: value})
        if regular_query:
            query = get_query(search_term, fields, search_fields)

        if 'facets' in schema:
            for facet in schema['facets']:
                face = {'terms': {'field': '', 'size': 99999}}
                face['terms']['field'] = 'object.' + facet[facet.keys()[0]] + '.untouched'
                query['facets'][facet.keys()[0]] = face
                for f in result['filters']:
                    if facet[facet.keys()[0]] == f.keys()[0]:
                        del(query['facets'][facet.keys()[0]])
        else:
            del(query['facets'])

        # Execute the query
        results = es.search(query, index='encoded', doc_type=index, size=size)

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
                    if len(face[facet.keys()[0]]) > 1:
                        result['facets'].append(face)

        for hit in results['hits']['hits']:
            result_hit = hit['fields']
            result_hit_new = {}
            for c in result_hit:
                result_hit_new[c[7:]] = result_hit[c]
            result['@graph'].append(result_hit_new)

        result['count'] = results['hits']['total']
        if len(result['@graph']):
            result['notification'] = 'Success'
        else:
            if len(search_term) < 3:
                result['notification'] = 'No results found. Search term should be at least 3 characters long.'
            else:
                result['notification'] = 'No results found'
        return result
