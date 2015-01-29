import re
from pyramid.view import view_config
from ..indexing import ELASTIC_SEARCH
from pyramid.security import effective_principals
from urllib.parse import urlencode
from collections import OrderedDict

sanitize_search_string_re = re.compile(r'[\\\+\-\&\|\!\(\)\{\}\[\]\^\~\:\/\\\*\?]')

hgConnect = ''.join([
    'http://genome.ucsc.edu/cgi-bin/hgHubConnect',
    '?hgHub_do_redirect=on',
    '&hgHubConnect.remakeTrackHub=on',
    '&hgHub_do_firstDb=1',
    '&hubUrl=',
])

audit_facets = [
    ('audit.ERROR.category', {'title': 'Audit category: ERROR'}),
    ('audit.NOT_COMPLIANT.category', {'title': 'Audit category: NOT COMPLIANT'}),
    ('audit.WARNING.category', {'title': 'Audit category: WARNING'}),
    ('audit.DCC_ACTION.category', {'title': 'Audit category: DCC ACTION'})
]


def get_filtered_query(term, fields, principals):
    return {
        'query': {
            'query_string': {
                'query': term,
                'default_operator': 'AND',
                'fields': [
                    'encoded_all_ngram',
                    'encoded_all_standard',
                    'encoded_all_untouched'],
                'analyzer': 'encoded_search_analyzer'
            }
        },
        'filter': {
            'and': {
                'filters': [
                    {
                        'terms': {
                            'principals_allowed.view': principals
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
        'aggs': {},
        '_source': list(fields),
    }


def sanitize_search_string(text):
    return sanitize_search_string_re.sub(r'\\\g<0>', text)


@view_config(route_name='search', request_method='GET', permission='search')
def search(context, request, search_type=None):
    ''' Search view connects to ElasticSearch and returns the results'''
    root = request.root
    result = {
        '@id': '/search/' + ('?' + request.query_string if request.query_string else ''),
        '@type': ['search'],
        'title': 'Search',
        'facets': [],
        '@graph': [],
        'columns': OrderedDict(),
        'filters': [],
        'notification': '',
    }

    principals = effective_principals(request)
    es = request.registry[ELASTIC_SEARCH]
    search_audit = request.has_permission('search_audit')

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
        doc_types = request.params.getall('type')
        if '*' in doc_types:
            doc_types = []

        # handling invalid item types
        bad_types = [t for t in doc_types if t not in root.by_item_type]
        if bad_types:
            result['notification'] = "Invalid type: %s" ', '.join(bad_types)
            return result
    else:
        doc_types = [search_type]

    # Building query for filters
    if not doc_types:
        if request.params.get('mode') == 'picker':
            doc_types = []
        else:
            doc_types = ['antibody_lot', 'biosample',
                         'experiment', 'target', 'dataset', 'page', 'publication',
                         'software']
    else:
        for item_type in doc_types:
            qs = urlencode([
                (k.encode('utf-8'), v.encode('utf-8'))
                for k, v in request.params.items() if k != 'type' and v != item_type
            ])
            result['filters'].append({
                'field': 'type',
                'term': item_type,
                'remove': '{}?{}'.format(request.path, qs)
                })

    frame = request.params.get('frame')
    fields_requested = request.params.getall('field')
    if fields_requested:
        fields = {'embedded.@id', 'embedded.@type'}
        fields.update('embedded.' + field for field in fields_requested)
    elif frame in ['embedded', 'object']:
        fields = [frame + '.*']
    else:
        frame = 'columns'
        fields = set()
        if search_audit:
            fields.add('audit.*')
        for doc_type in (doc_types or root.by_item_type.keys()):
            collection = root[doc_type]
            if 'columns' not in (collection.Item.schema or ()):
                fields.add('object.*')
            else:
                columns = collection.Item.schema['columns']
                fields.update(
                    ('embedded.@id', 'embedded.@type'),
                    ('embedded.' + column for column in columns),
                )
                result['columns'].update(columns)

    # Builds filtered query which supports multiple facet selection
    query = get_filtered_query(search_term, sorted(fields), principals)

    if not result['columns']:
        del result['columns']

    # Sorting the files when search term is not specified
    if search_term == '*':
        query['sort'] = {
            'embedded.date_created': {
                'order': 'desc',
                'ignore_unmapped': True,
            },
            'embedded.label': {
                'order': 'asc',
                'missing': '_last',
                'ignore_unmapped': True,
            },
        }
        # Adding match_all for wildcard search for performance
        query['query']['match_all'] = {}
        del query['query']['query_string']

    # Setting filters
    query_filters = query['filter']['and']['filters']
    used_filters = {}
    for field, term in request.params.items():
        if field in ['type', 'limit', 'mode', 'searchTerm',
                     'format', 'frame', 'datastore', 'field']:
            continue

        # Add filter to result
        qs = urlencode([
            (k.encode('utf-8'), v.encode('utf-8'))
            for k, v in request.params.items() if v != term
        ])
        result['filters'].append({
            'field': field,
            'term': term,
            'remove': '{}?{}'.format(request.path, qs)
        })

        # Add filter to query
        if field.startswith('audit'):
            query_field = field
        else:
            query_field = 'embedded.' + field

        if query_field not in used_filters:
            query_terms = used_filters[query_field] = []
            query_filters.append({
                'terms': {
                    query_field: query_terms,
                }
            })
        used_filters[query_field].append(term)

    # Adding facets to the query
    # TODO: Have to simplify this piece of code
    facets = [
        ('type', {'title': 'Data Type'}),
    ]
    if len(doc_types) == 1 and 'facets' in root[doc_types[0]].Item.schema:
        facets.extend(root[doc_types[0]].Item.schema['facets'].items())

    if search_audit:
        for audit_facet in audit_facets:
            facets.append(audit_facet)

    for field, _ in facets:
        if field == 'type':
            query_field = '_type'
        elif field.startswith('audit'):
            query_field = field
        else:
            query_field = 'embedded.' + field
        agg_name = field.replace('.', '-')

        terms = [
            {'terms': {q_field: q_terms}}
            for q_field, q_terms in used_filters.items()
            if q_field != query_field
        ]
        terms.append(
            {'terms': {'principals_allowed.view': principals}}
        )

        query['aggs'][agg_name] = {
            'aggs': {
                agg_name: {
                    'terms': {
                        'field': query_field,
                        'min_doc_count': 0,
                        'size': 100
                    }
                }
            },
            'filter': {
                'bool': {
                    'must': terms,
                },
            },
        }

    # Execute the query
    results = es.search(body=query, index='encoded', doc_type=doc_types or None, size=size)

    # Loading facets in to the results
    if 'aggregations' in results:
        facet_results = results['aggregations']
        for field, facet in facets:
            agg_name = field.replace('.', '-')
            if agg_name not in facet_results:
                continue
            terms = facet_results[agg_name][agg_name]['buckets']
            if len(terms) < 2:
                continue
            result['facets'].append({
                'field': field,
                'title': facet['title'],
                'terms': terms,
                'total': facet_results[agg_name]['doc_count']
            })

    if doc_types == ['experiment'] and any(
            facet['doc_count'] > 0
            for facet in results['aggregations']['assembly']['assembly']['buckets']):
        search_params = request.query_string.replace('&', ',,')
        hub = request.route_url('batch_hub', search_params=search_params, txt='hub.txt')
        result['batch_hub'] = hgConnect + hub

    # Loading result rows
    hits = results['hits']['hits']
    if frame in ['embedded', 'object'] and not len(fields_requested):
        result['@graph'] = [hit['_source'][frame] for hit in hits]
    elif fields_requested:
        result['@graph'] = [hit['_source']['embedded'] for hit in hits]
    else:  # columns
        for hit in hits:
            item_type = hit['_type']
            if 'columns' in root[item_type].Item.schema:
                item = hit['_source']['embedded']
            else:
                item = hit['_source']['object']
            if 'audit' in hit['_source']:
                item['audit'] = hit['_source']['audit']
            result['@graph'].append(item)

    # Adding total
    result['total'] = results['hits']['total']
    result['notification'] = 'Success' if result['total'] else 'No results found'

    return result
