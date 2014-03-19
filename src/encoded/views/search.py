import re
from pyramid.view import view_config
from ..contentbase import (
    Root
)
from ..indexing import ELASTIC_SEARCH
from pyramid.security import effective_principals
from urllib import urlencode

sanitize_search_string_re = re.compile(r'[\\\+\-\&\|\!\(\)\{\}\[\]\^\~\:\/\\\*\?]')


def get_filtered_query(term, fields, principals):
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
                        'fields': [
                            'encoded_all_ngram',
                            'encoded_all_standard',
                            'encoded_all_untouched'
                        ]
                    }
                },
                'filter': {
                    'and': {
                        'filters': [
                            {
                                'terms': {
                                    'principals_allowed_view': principals
                                }
                            }
                        ]
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
        'fields': ['embedded.' + field for field in fields],
    }


def sanitize_search_string(text):
    return sanitize_search_string_re.sub(r'\\\g<0>', text)


@view_config(name='search', context=Root, request_method='GET', permission='search')
def search(context, request, search_type=None):
    ''' Search view connects to ElasticSearch and returns the results'''

    uri = request.resource_path(context, request.view_name, '')
    if request.query_string:
        uri += '?' + request.query_string

    root = request.root
    result = {
        '@id': uri,
        '@type': ['search'],
        'title': 'Search',
        'facets': [],
        '@graph': [],
        'columns': {},
        'filters': [],
        'notification': ''
    }

    principals = effective_principals(request)
    es = request.registry[ELASTIC_SEARCH]

    # handling limit
    size = request.params.get('limit', 25)
    if size in ('all', ''):
        size = 99999
    else:
        try:
            size = int(size)
        except ValueError:
            size = 25

    search_term = request.params.get('searchTerm', '*')
    if search_term != '*':
        search_term = sanitize_search_string(search_term.strip())
    # Handling whitespaces in the search term
    if not search_term:
        result['notification'] = 'Please enter search term'
        return result

    if search_type is None:
        search_type = request.params.get('type', '*')

        # handling invalid item types
        if search_type != '*':
            if search_type not in root.by_item_type:
                result['notification'] = "'" + search_type + "' is not a valid 'item type'"
                return result

    # Handling wildcards
    if search_term == '*' and search_type == '*':
        result['notification'] = 'Please enter search term'
        return result

    # Building query for filters
    if search_type == '*':
        doc_types = ['antibody_approval', 'biosample', 'experiment', 'target', 'dataset']
    else:
        doc_types = [search_type]
        if search_term != '*':
            field = 'type'
            term = root.by_item_type[search_type].__name__
            qs = urlencode([
                (k.encode('utf-8'), v.encode('utf-8'))
                for k, v in request.params.iteritems() if k != field
            ])
            result['filters'].append({
                'field': field,
                'term': term,
                'remove': '{}?{}'.format(request.path, qs)
            })

    frame = request.params.get('frame')
    if frame in ['embedded', 'object']:
        fields = []
    elif len(doc_types) == 1 and 'columns' not in (root[doc_types[0]].schema or ()):
        frame = 'object'
        fields = []
    else:
        frame = 'columns'
        fields = {'@id', '@type'}
        for doc_type in doc_types:
            collection = root[doc_type]
            if frame == 'columns':
                if collection.schema is None:
                    continue
                fields.update(collection.schema.get('columns', ()))
                result['columns'].update(collection.schema['columns'])

    # Builds filtered query which supports multiple facet selection
    query = get_filtered_query(search_term, sorted(fields), principals)
    
    # Handling object fields return for ES 1.0.+
    if not len(fields):
        del(query['fields'])
        query['_source'] = [frame]

    if not result['columns']:
        del result['columns']

    # Sorting the files when search term is not specified
    if search_term == '*':
        query['sort'] = {
            'date_created': {
                'order': 'desc',
                'ignore_unmapped': True,
            },
            'label': {
                'order': 'asc',
                'missing': '_last',
                'ignore_unmapped': True,
            },
        }

    # Setting filters
    query_filters = query['query']['filtered']['filter']['and']['filters']
    for field, term in request.params.iteritems():
        if field not in ['type', 'searchTerm', 'limit', 'format', 'frame', 'datastore']:
            if term == 'other':
                query_filters.append({'missing': {'field': 'embedded.' + field}})
            else:
                query_filters.append({'term': {'embedded.{}'.format(field): term}})

            qs = urlencode([
                (k.encode('utf-8'), v.encode('utf-8'))
                for k, v in request.params.iteritems() if k != field
            ])
            result['filters'].append({
                'field': field,
                'term': term,
                'remove': '{}?{}'.format(request.path, qs)
            })

    used_facets = {f['field'] for f in result['filters']}
    # Adding facets to the query
    if len(doc_types) == 1 and 'facets' in root[doc_types[0]].schema:
        facets = root[doc_types[0]].schema['facets']
        for facet_title in facets:
            field = facets[facet_title]
            if field in used_facets:
                continue
            query['facets'][field] = {
                'terms': {
                    'field': 'embedded.{}'.format(field),
                    'size': 99999,
                },
            }
    else:
        facets = {'Data Type': 'type'}
        query['facets']['type'] = {'terms': {'field': '_type', 'size': 99999}}

    # Execute the query
    results = es.search(query, index='encoded', doc_type=doc_types, size=size)

    # Loading facets in to the results
    if 'facets' in results:
        facet_results = results['facets']
        for facet_title in facets:
            field = facets[facet_title]
            if field not in facet_results:
                continue
            terms = facet_results[field]['terms']
            if len(terms) < 2:
                continue
            result['facets'].append({
                'field': field,
                'title': facet_title,
                'terms': terms,
            })

    # Loading result rows
    hits = results['hits']['hits']
    if frame in ['embedded', 'object']:
        result['@graph'] = [hit['_source'][frame] for hit in hits]
    else:
        prefix_len = len('embedded.')
        for hit in hits:
            item = {}
            for field, value in hit['fields'].items():
                if field[prefix_len:] == '@id':
                    item[field[prefix_len:]] = value[0]
                elif field[prefix_len:] == '@type':
                    item[field[prefix_len:]] = value
                elif result['columns'][field[prefix_len:]]['type'] != 'array':
                    item[field[prefix_len:]] = value[0]
                else:
                    item[field[prefix_len:]] = value
            result['@graph'].append(item)

    # Adding total
    result['total'] = results['hits']['total']
    if len(result['@graph']):
        result['notification'] = 'Success'
    else:
        result['notification'] = 'No results found'
    return result
