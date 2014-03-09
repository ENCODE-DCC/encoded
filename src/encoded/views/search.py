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
        'query': {
            'query_string': {
                'query': term,
                'default_operator': 'AND',
                'fields': [
                    'encoded_all_ngram',
                    'encoded_all_standard',
                    'encoded_all_untouched'
                    ],
                'analyzer': 'encoded_search_analyzer'
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
        },
        'highlight': {
            'fields': {
                '_all': {}
            }
        },
        'facets': {},
        'fields': fields
    }


def sanitize_search_string(text):
    return sanitize_search_string_re.sub(r'\\\g<0>', text)


@view_config(name='search', context=Root, request_method='GET',
             permission='search')
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
                result['notification'] = "'" + search_type + \
                    "' is not a valid 'item type'"
                return result

    # Handling wildcards
    if search_term == '*' and search_type == '*':
        result['notification'] = 'Please enter search term'
        return result

    # Building query for filters
    if search_type == '*':
        doc_types = ['antibody_approval', 'biosample',
                     'experiment', 'target', 'dataset']
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
        fields = {frame}
    elif len(doc_types) == 1 and not root[doc_types[0]].columns:
        frame = 'object'
        fields = {frame}
    else:
        frame = 'columns'
        fields = {'embedded.@id', 'embedded.@type'}
    for doc_type in doc_types:
        collection = root[doc_type]
        if frame == 'columns':
            fields.update('embedded.' +
                          column for column in collection.columns)
            result['columns'].update(collection.columns)

    if not result['columns']:
        del result['columns']

    # Builds filtered query which supports multiple facet selection
    query = get_filtered_query(search_term, sorted(fields), principals)

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
        # Adding match_all for wildcard search for performance
        query['query']['match_all'] = {}
        del(query['query']['query_string'])

    # Setting filters
    query_filters = query['filter']['and']['filters']
    used_filters = []
    for field, term in request.params.iteritems():
        if field not in ['type', 'searchTerm', 'limit',
                         'format', 'frame', 'datastore']:
            if term == 'other':
                query_filters.append({
                    'missing': {
                        'field': 'embedded.' + field
                        }
                    })
            else:
                if field in used_filters:
                    for f in query_filters:
                        if 'embedded.{}'.format(field) in f['terms'].keys():
                            f['terms']['embedded.{}'
                                       .format(field)].append(term)
                else:
                    query_filters.append({
                        'terms': {
                            'embedded.{}'.format(field): [term]
                        }
                    })
                    used_filters.append(field)
            qs = urlencode([
                (k.encode('utf-8'), v.encode('utf-8'))
                for k, v in request.params.iteritems() if v != term
            ])
            result['filters'].append({
                'field': field,
                'term': term,
                'remove': '{}?{}'.format(request.path, qs)
            })

    # Adding facets to the query
    if len(doc_types) == 1 and 'facets' in root[doc_types[0]].schema:
        facets = [facet.items()[0]
                  for facet in root[doc_types[0]].schema['facets']]
        for facet_title, field in facets:
            query['facets'][field] = {
                'terms': {
                    'field': 'embedded.{}'.format(field),
                }
            }
            for count, used_facet in enumerate(result['filters']):
                if field != used_facet['field']:
                    try:
                        query['facets'][field]['facet_filter']['terms'][
                            'embedded.' + used_facet['field']]\
                            .append(used_facet['term'])
                    except:
                        query['facets'][field]['facet_filter'] = {
                            'terms': {
                                'embedded.' + used_facet['field']:
                                [used_facet['term']]
                            }
                        }
    else:
        facets = [('Data Type', 'type')]
        query['facets']['type'] = {
            'terms': {
                'field': '_type',
            }
        }

    # Execute the query
    results = es.search(query, index='encoded', doc_type=doc_types, size=size)

    # Loading facets in to the results
    if 'facets' in results:
        facet_results = results['facets']
        for facet_title, field in facets:
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
        result['@graph'] = [hit['fields'][frame] for hit in hits]
    else:
        prefix_len = len('embedded.')
        result['@graph'] = [
            {field[prefix_len:]:
                value for field, value in hit['fields'].items()}
            for hit in hits
        ]

    # Adding total
    result['total'] = results['hits']['total']
    if len(result['@graph']):
        result['notification'] = 'Success'
    else:
        result['notification'] = 'No results found'
    return result
