import re
from pyramid.view import view_config
from contentbase import (
    Collection,
    TYPES,
)
from contentbase.elasticsearch import ELASTIC_SEARCH
from contentbase.resource_views import collection_view_listing_db
from pyramid.security import effective_principals
from urllib.parse import urlencode
from collections import OrderedDict


def includeme(config):
    config.add_route('search', '/search{slash:/?}')
    config.add_route('matrix', '/matrix{slash:/?}')
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


DEFAULT_DOC_TYPES = [
    'annotation',
    'antibody_lot',
    'biosample',
    'experiment',
    'matched_set',
    'organism_development_series',
    'page',
    'pipeline',
    'project',
    'publication',
    'publication_data',
    'reference',
    'reference_epigenome',
    'replication_timing_series',
    'software',
    'target',
    'treatment_concentration_series',
    'treatment_time_series',
    'ucsc_browser_composite',
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


def prepare_search_term(request):
    search_term = request.params.get('searchTerm', '*')
    if search_term != '*':
        search_term = sanitize_search_string_re.sub(r'\\\g<0>', search_term.strip())
        search_term_array = search_term.split()
        if search_term_array[len(search_term_array) - 1] in ['AND', 'NOT', 'OR']:
            del search_term_array[-1]
            search_term = ' '.join(search_term_array)
    return search_term


def get_sort_order(sort_order=None):
    """
    specifies sort order for elasticsearch results
    """
    if sort_order is not None:
        order = {}
        for field in sort_order:
            # Should always sort on raw field rather than analyzed field
            order['embedded.' + field + '.raw'] = sort_order[field]
        return order
    return {
        'embedded.date_created.raw': {
            'order': 'desc',
            'ignore_unmapped': True,
        },
        'embedded.label.raw': {
            'order': 'asc',
            'missing': '_last',
            'ignore_unmapped': True,
        },
    }


def get_search_fields(request, doc_types):
    """
    Returns set of columns that are being searched and highlights
    """
    fields = {'uuid'}
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
        if field in ['type', 'limit', 'y.limit', 'x.limit' 'mode', 'annotation',
                     'format', 'frame', 'datastore', 'field', 'region', 'genome']:
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

        if field == 'searchTerm':
            continue

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


def format_results(request, es_results, result):
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


def search_result_actions(request, doc_types, es_results):
    actions = {}

    # generate batch hub URL for experiments
    if doc_types == ['experiment'] and any(
            bucket['doc_count'] > 0
            for bucket in es_results['aggregations']['assembly']['assembly']['buckets']):
        search_params = request.query_string.replace('&', ',,')
        hub = request.route_url('batch_hub',
                                search_params=search_params,
                                txt='hub.txt')
        actions['batch_hub'] = hgConnect + hub

    # generate batch download URL for experiments
    if doc_types == ['experiment'] and any(
            bucket['doc_count'] > 0
            for bucket in es_results['aggregations']['files-file_type']['files-file_type']['buckets']):
        actions['batch_download'] = request.route_url(
            'batch_download',
            search_params=request.query_string
        )

    return actions


def load_facets(es_results, facets, result):
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


@view_config(route_name='search', request_method='GET', permission='search')
def search(context, request, search_type=None):
    """
    Search view connects to ElasticSearch and returns the results
    """
    root = request.root
    types = request.registry[TYPES]
    search_base = ('?' + request.query_string if request.query_string else '')
    result = {
        '@context': request.route_path('jsonld_context'),
        '@id': '/search/' + search_base,
        '@type': ['Search'],
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

    search_term = prepare_search_term(request)

    # Handling whitespaces in the search term
    if not search_term:
        result['notification'] = 'Please enter search term'
        return result

    if search_type is None:
        doc_types = request.params.getall('type')
        if '*' in doc_types:
            doc_types = []

        # Check for invalid types including abstract types
        bad_types = [t for t in doc_types if t not in types or not hasattr(types[t], 'item_type')]
        if bad_types:
            result['notification'] = "Invalid type: %s" ', '.join(bad_types)
            return result

        # Normalize to item_type
        doc_types = [types[name].item_type for name in doc_types]
    else:
        doc_types = [search_type]

    # Building query for filters
    if not doc_types:
        if request.params.get('mode') == 'picker':
            doc_types = []
        else:
            doc_types = DEFAULT_DOC_TYPES
    else:
        for item_type in doc_types:
            ti = types[item_type]
            qs = urlencode([
                (k.encode('utf-8'), v.encode('utf-8'))
                for k, v in request.params.items() if not (k == 'type' and types[v] is ti)
            ])
            result['filters'].append({
                'field': 'type',
                'term': ti.item_type,
                'remove': '{}?{}'.format(request.path, qs)
            })
        if len(doc_types) == 1 and hasattr(ti.factory, 'matrix'):
            result['matrix'] = request.route_path('matrix', slash='/') + search_base

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
        query['sort'] = [get_sort_order()]
        if len(doc_types) == 1:
            type_schema = root[doc_types[0]].type_info.schema
            if 'sort_by' in type_schema and len(type_schema['sort_by']):
                query['sort'] = [get_sort_order(type_schema['sort_by'])]
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

    load_facets(es_results, facets, result)

    # Adding total
    result['total'] = es_results['hits']['total']

    # Show any filters that aren't facets as a fake facet with one entry,
    # so that the filter can be viewed and removed
    for field, values in used_filters.items():
        if field not in facets:
            title = field
            for item_type in doc_types:
                if field in types[item_type].schema['properties']:
                    title = types[item_type].schema['properties'][field]['title']
                    break
            result['facets'].append({
                'field': field,
                'title': title,
                'terms': [{'key': v} for v in values],
                'total': result['total'],
                })

    # Add batch actions
    result.update(search_result_actions(request, doc_types, es_results))

    # Format results for JSON-LD
    format_results(request, es_results, result)

    result['notification'] = 'Success' if result['total'] else 'No results found'
    return result


@view_config(context=Collection, permission='list', request_method='GET',
             name='listing')
def collection_view_listing_es(context, request):
    # Switch to change summary page loading options
    if request.datastore != 'elasticsearch':
        return collection_view_listing_db(context, request)

    result = search(context, request, context.type_info.item_type)

    if len(result['@graph']) < result['total']:
        params = [(k, v) for k, v in request.params.items() if k != 'limit']
        params.append(('limit', 'all'))
        result['all'] = '%s?%s' % (request.resource_path(context), urlencode(params))

    return result


@view_config(route_name='matrix', request_method='GET', permission='search')
def matrix(context, request):
    """
    Return search results aggregated by x and y buckets for building a matrix display.
    """
    search_base = ('?' + request.query_string if request.query_string else '')
    result = {
        '@context': request.route_path('jsonld_context'),
        '@id': request.route_path('matrix', slash='/') + search_base,
        '@type': ['Matrix'],
        'facets': [],
        'filters': [],
        'notification': '',
    }

    doc_types = request.params.getall('type')
    if len(doc_types) != 1:
        result['notification'] = 'Search result matrix currently requires specifying a single type.'
        return result
    item_type = doc_types[0]
    types = request.registry[TYPES]
    if item_type not in types:
        result['notification'] = 'Invalid type: {}'.format(item_type)
    type_info = types[item_type]
    if not hasattr(type_info.factory, 'matrix'):
        result['notification'] = 'No matrix configured for type: {}'.format(item_type)
        return result
    schema = type_info.schema
    result['title'] = type_info.name + ' Matrix'

    matrix = result['matrix'] = type_info.factory.matrix.copy()
    matrix['x']['limit'] = request.params.get('x.limit', 20)
    matrix['y']['limit'] = request.params.get('y.limit', 5)
    matrix['search_base'] = request.route_path('search', slash='/') + search_base
    matrix['clear_matrix'] = request.route_path('matrix', slash='/') + '?type=' + item_type

    principals = effective_principals(request)
    es = request.registry[ELASTIC_SEARCH]
    es_index = request.registry.settings['contentbase.elasticsearch.index']

    search_term = prepare_search_term(request)

    # Handling whitespaces in the search term
    if not search_term:
        result['notification'] = 'Please enter search term'
        return result

    search_fields, highlights = get_search_fields(request, doc_types)

    # Builds filtered query which supports multiple facet selection
    query = get_filtered_query(search_term,
                               search_fields,
                               [],
                               principals)

    if search_term == '*':
        query['query']['match_all'] = {}
        del query['query']['query_string']

    # Setting filters
    used_filters = set_filters(request, query, result)
    # We don't actually need filters in the request,
    # since we're only counting and the aggregations have their own filters
    del query['filter']

    # Adding facets to the query
    facets = schema['facets'].items()
    set_facets(facets, used_filters, query, principals)

    # Group results in 2 dimensions
    matrix_terms = []
    for q_field, q_terms in used_filters.items():
        matrix_terms.append({'terms': {'embedded.' + q_field + '.raw': q_terms}})
    matrix_terms.append(
        {'terms': {'principals_allowed.view': principals}}
    )
    x_grouping = matrix['x']['group_by']
    y_groupings = matrix['y']['group_by']
    x_agg = {
        "terms": {
            "field": 'embedded.' + x_grouping + '.raw',
            "size": 0,  # no limit
        },
    }
    aggs = {x_grouping: x_agg}
    for field in reversed(y_groupings):
        aggs = {
            field: {
                "terms": {
                    "field": 'embedded.' + field + '.raw',
                    "size": 0,  # no limit
                },
                "aggs": aggs,
            },
        }
    aggs['x'] = x_agg
    query['aggs']['matrix'] = {
        "filter": {
            "bool": {
                "must": matrix_terms,
            }
        },
        "aggs": aggs,
    }

    # Execute the query
    es_results = es.search(body=query, index=es_index,
                           doc_type=doc_types or None, search_type='count')


    # Format facets for results
    load_facets(es_results, facets, result)

    # Format matrix for results
    aggregations = es_results['aggregations']
    result['matrix']['doc_count'] = aggregations['matrix']['doc_count']
    result['matrix']['max_cell_doc_count'] = 0
    def summarize_buckets(matrix, x_buckets, outer_bucket, grouping_fields):
        group_by = grouping_fields[0]
        grouping_fields = grouping_fields[1:]
        if not grouping_fields:
            counts = {}
            for bucket in outer_bucket[group_by]['buckets']:
                doc_count = bucket['doc_count']
                if doc_count > matrix['max_cell_doc_count']:
                    matrix['max_cell_doc_count'] = doc_count
                counts[bucket['key']] = doc_count
            summary = []
            for bucket in x_buckets:
                summary.append(counts.get(bucket['key'], 0))
            outer_bucket[group_by] = summary
        else:
            for bucket in outer_bucket[group_by]['buckets']:
                summarize_buckets(matrix, x_buckets, bucket, grouping_fields)
    summarize_buckets(result['matrix'], aggregations['matrix']['x']['buckets'], aggregations['matrix'], y_groupings + [x_grouping])
    result['matrix']['y'][y_groupings[0]] = aggregations['matrix'][y_groupings[0]]
    result['matrix']['x'].update(aggregations['matrix']['x'])

    # Add batch actions
    result.update(search_result_actions(request, doc_types, es_results))

    # Format results for JSON-LD
    format_results(request, es_results, result)

    # Adding total
    result['total'] = es_results['hits']['total']
    result['notification'] = 'Success' if result['total'] else 'No results found'
    return result
