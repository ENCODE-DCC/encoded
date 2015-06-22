import re
from pyramid.view import view_config
from contentbase import (
    Collection,
    TYPES,
    collection_view_listing_db,
)
from contentbase.elasticsearch import ELASTIC_SEARCH
from pyramid.security import effective_principals
from urllib.parse import urlencode
from collections import OrderedDict


def includeme(config):
    config.add_route('search', '/search{slash:/?}')
    config.scan(__name__)


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


def get_filtered_query(term, search_fields, result_fields, principals):
    return {
        'query': {
            'query_string': {
                'query': term,
                'fields': search_fields,
                'default_operator': 'AND'
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
        'aggs': {},
        '_source': list(result_fields),
    }


def sanitize_search_string(text):
    return sanitize_search_string_re.sub(r'\\\g<0>', text)


def get_sort_order():
    """
    specifies sort order for elasticsearch results
    """
    return {
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


def get_search_fields(request, doc_types):
    """
    Returns set of columns that are being searched and highlights
    """
    fields = set()
    highlights = {}
    for doc_type in (doc_types or request.root.by_item_type.keys()):
        collection = request.root[doc_type]
        for value in collection.type_info.schema.get('boost_values', ()):
            fields.add('embedded.' + value)
            highlights['embedded.' + value] = {}
    return fields, highlights


def load_columns(request, doc_types, result):
    """
    Returns fields that are requested by user or default fields
    """
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
        if request.has_permission('search_audit'):
            fields.add('audit.*')
        for doc_type in (doc_types or request.root.by_item_type.keys()):
            collection = request.root[doc_type]
            if 'columns' not in (collection.type_info.schema or ()):
                fields.add('object.*')
            else:
                columns = collection.type_info.schema['columns']
                fields.update(
                    ('embedded.@id', 'embedded.@type'),
                    ('embedded.' + column for column in columns),
                )
                result['columns'].update(columns)
    return fields


def set_filters(request, query, result):
    """
    Sets filters in the query
    """
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
            query_field = 'embedded.' + field + '.raw'

        if field.endswith('!'):
            if field not in used_filters:
                # Setting not filter instead of terms filter
                query_filters.append({
                    'not': {
                        'terms': {
                            'embedded.' + field[:-1] + '.raw': [term],
                        }
                    }
                })
                query_terms = used_filters[field] = []
            else:
                query_filters.remove({
                    'not': {
                        'terms': {
                            'embedded.' + field[:-1] + '.raw': used_filters[field]
                        }
                    }
                })
                used_filters[field].append(term)
                query_filters.append({
                    'not': {
                        'terms': {
                            'embedded.' + field[:-1] + '.raw': used_filters[field]
                        }
                    }
                })
        else:
            if field not in used_filters:
                query_terms = used_filters[field] = []
                query_filters.append({
                    'terms': {
                        query_field: query_terms,
                    }
                })
            else:
                query_filters.remove({
                    'terms': {
                        query_field: used_filters[field]
                    }
                })
                used_filters[field].append(term)
                query_filters.append({
                    'terms': {
                        query_field: used_filters[field]
                    }
                })
        used_filters[field].append(term)
    return used_filters


def set_facets(facets, used_filters, query, principals):
    """
    Sets facets in the query using filters
    """
    for field, _ in facets:
        if field == 'type':
            query_field = '_type'
        elif field.startswith('audit'):
            query_field = field
        else:
            query_field = 'embedded.' + field + '.raw'
        agg_name = field.replace('.', '-')

        terms = []
        # Adding facets based on filters
        for q_field, q_terms in used_filters.items():
            if q_field != field and q_field.startswith('audit'):
                terms.append({'terms': {q_field: q_terms}})
            elif q_field != field and not q_field.endswith('!'):
                terms.append({'terms': {'embedded.' + q_field + '.raw': q_terms}})
            elif q_field != field and q_field.endswith('!'):
                terms.append({'not': {'terms': {'embedded.' + q_field[:-1] + '.raw': q_terms}}})

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


def load_results(request, es_results, result):
    """
    Loads results to pass onto UI
    """
    hits = es_results['hits']['hits']
    frame = request.params.get('frame')
    fields_requested = request.params.getall('field')
    if frame in ['embedded', 'object'] and not len(fields_requested):
        result['@graph'] = [hit['_source'][frame] for hit in hits]
    elif fields_requested:
        result['@graph'] = [hit['_source']['embedded'] for hit in hits]
    else:  # columns
        for hit in hits:
            item_type = hit['_type']
            if 'columns' in request.registry[TYPES][item_type].schema:
                item = hit['_source']['embedded']
            else:
                item = hit['_source']['object']
            if 'audit' in hit['_source']:
                item['audit'] = hit['_source']['audit']
            if 'highlight' in hit:
                item['highlight'] = {}
                for key in hit['highlight']:
                    item['highlight'][key[9:]] = list(set(hit['highlight'][key]))
            result['@graph'].append(item)


@view_config(route_name='search', request_method='GET', permission='search')
def search(context, request, search_type=None):
    """
    Search view connects to ElasticSearch and returns the results
    """
    root = request.root
    types = request.registry[TYPES]
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
    es_index = request.registry.settings['contentbase.elasticsearch.index']
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
        search_term_array = search_term.split()
        if search_term_array[len(search_term_array) - 1] in ['AND', 'NOT', 'OR']:
            del search_term_array[-1]
            search_term = ' '.join(search_term_array)

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

    search_fields, highlights = get_search_fields(request, doc_types)

    # Builds filtered query which supports multiple facet selection
    query = get_filtered_query(search_term,
                               search_fields,
                               sorted(load_columns(request, doc_types, result)),
                               principals)

    if not result['columns']:
        del result['columns']

    # Sorting the files when search term is not specified
    if search_term == '*':
        query['sort'] = get_sort_order()
        query['query']['match_all'] = {}
        del query['query']['query_string']
    elif len(doc_types) != 1:
        del query['query']['query_string']['fields']

    # Setting filters
    used_filters = set_filters(request, query, result)

    # Adding facets to the query
    facets = [
        ('type', {'title': 'Data Type'}),
    ]
    if len(doc_types) == 1 and 'facets' in types[doc_types[0]].schema:
        facets.extend(types[doc_types[0]].schema['facets'].items())

    if search_audit:
        for audit_facet in audit_facets:
            facets.append(audit_facet)

    set_facets(facets, used_filters, query, principals)

    # Execute the query
    es_results = es.search(body=query, index=es_index,
                           doc_type=doc_types or None, size=size)

    # Loading facets in to the results
    if 'aggregations' in es_results:
        facet_results = es_results['aggregations']
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

    # generate batch hub URL for experiments
    if doc_types == ['experiment'] and any(
            facet['doc_count'] > 0
            for facet in es_results['aggregations']['assembly']['assembly']['buckets']):
        search_params = request.query_string.replace('&', ',,')
        hub = request.route_url('batch_hub',
                                search_params=search_params,
                                txt='hub.txt')
        result['batch_hub'] = hgConnect + hub

    # generate batch download URL for experiments
    if doc_types == ['experiment']:
        result['batch_download'] = request.route_url(
            'batch_download',
            search_params=request.query_string
        )

    # Moved to a seperate method to make code readable
    load_results(request, es_results, result)

    # Adding total
    result['total'] = es_results['hits']['total']
    result['notification'] = 'Success' if result['total'] else 'No results found'
    return result


@view_config(context=Collection, permission='list', request_method='GET',
             name='listing')
def collection_view_listing_es(context, request):
    # Switch to change summary page loading options
    if request.datastore != 'elasticsearch':
        return collection_view_listing_db(context, request)

    result = search(context, request, context.item_type)

    if len(result['@graph']) < result['total']:
        params = [(k, v) for k, v in request.params.items() if k != 'limit']
        params.append(('limit', 'all'))
        result['all'] = '%s?%s' % (request.resource_path(context), urlencode(params))

    return result
