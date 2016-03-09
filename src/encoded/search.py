import re
from pyramid.view import view_config
from snowfort import (
    AbstractCollection,
    TYPES,
)
from snowfort.elasticsearch import ELASTIC_SEARCH
from snowfort.resource_views import collection_view_listing_db
from elasticsearch.helpers import scan
from pyramid.httpexceptions import HTTPBadRequest
from pyramid.security import effective_principals
from urllib.parse import urlencode
from collections import OrderedDict

_ASSEMBLY_MAPPER = {
    'GRCh38-minimal': 'hg38',
    'GRCh38': 'hg38',
    'GRCh37': 'hg19',
    'GRCm38': 'mm10',
    'GRCm37': 'mm9',
    'BDGP6': 'dm4',
    'BDGP5': 'dm3',
    'WBcel235': 'WBcel235'
}


def includeme(config):
    config.add_route('search', '/search{slash:/?}')
    config.add_route('report', '/report{slash:/?}')
    config.add_route('matrix', '/matrix{slash:/?}')
    config.scan(__name__)


sanitize_search_string_re = re.compile(r'[\\\+\-\&\|\!\(\)\{\}\[\]\^\~\:\/\\\*\?]')

hgConnect = ''.join([
    'http://genome.ucsc.edu/cgi-bin/hgTracks',
    '?hubClear=',
])

audit_facets = [
    ('audit.ERROR.category', {'title': 'Audit category: ERROR'}),
    ('audit.NOT_COMPLIANT.category', {'title': 'Audit category: NOT COMPLIANT'}),
    ('audit.WARNING.category', {'title': 'Audit category: WARNING'}),
    ('audit.DCC_ACTION.category', {'title': 'Audit category: DCC ACTION'})
]


DEFAULT_DOC_TYPES = [
    'AntibodyLot',
    'Biosample',
    'Dataset',
    'Page',
    'Pipeline',
    'Publication',
    'Software',
    'Target',
]


def get_pagination(request):
    from_ = request.params.get('from') or 0
    size = request.params.get('limit', 25)
    if size in ('all', ''):
        size = None
    else:
        try:
            size = int(size)
        except ValueError:
            size = 25
    return from_, size


def get_filtered_query(term, search_fields, result_fields, principals, doc_types):
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
                    },
                    {
                        'terms': {
                            'embedded.@type.raw': doc_types
                        }
                    }
                ]
            }
        },
        '_source': list(result_fields),
    }


def prepare_search_term(request):
    from antlr4 import IllegalStateException
    from lucenequery.prefixfields import prefixfields
    from lucenequery import dialects

    search_term = request.params.get('searchTerm', '').strip() or '*'
    if search_term == '*':
        return search_term

    # elasticsearch uses : as field delimiter, but we use it as namespace designator
    # if you need to search fields you have to use @type:field
    # if you need to search fields where the field contains ":", you will have to escape it
    # yourself
    if search_term.find("@type") < 0:
        search_term = search_term.replace(':', '\:')
    try:
        query = prefixfields('embedded.', search_term, dialects.elasticsearch)
    except (IllegalStateException):
        msg = "Invalid query: {}".format(search_term)
        raise HTTPBadRequest(explanation=msg)
    else:
        return query.getText()


def set_sort_order(request, search_term, types, doc_types, query, result):
    """
    sets sort order for elasticsearch results
    """
    sort = OrderedDict()
    result_sort = OrderedDict()

    # Prefer sort order specified in request, if any
    requested_sort = request.params.get('sort')
    if requested_sort:
        if requested_sort.startswith('-'):
            name = requested_sort[1:]
            order = 'desc'
        else:
            name = requested_sort
            order = 'asc'
        sort['embedded.' + name + '.raw'] = result_sort[name] = {
            'order': order,
            'ignore_unmapped': True,
        }

    # Otherwise we use a default sort only when there's no text search to be ranked
    if not sort and search_term == '*':

        # If searching for a single type, look for sort options in its schema
        if len(doc_types) == 1:
            type_schema = types[doc_types[0]].schema
            if 'sort_by' in type_schema:
                for k, v in type_schema['sort_by'].items():
                    # Should always sort on raw field rather than analyzed field
                    sort['embedded.' + k + '.raw'] = result_sort[k] = v

        # Default is most recent first, then alphabetical by label
        if not sort:
            sort['embedded.date_created.raw'] = result_sort['date_created'] = {
                'order': 'desc',
                'ignore_unmapped': True,
            }
            sort['embedded.label.raw'] = result_sort['label'] = {
                'order': 'asc',
                'missing': '_last',
                'ignore_unmapped': True,
            }

    if sort:
        query['sort'] = sort
        result['sort'] = result_sort


def get_search_fields(request, doc_types):
    """
    Returns set of columns that are being searched and highlights
    """
    fields = {'uuid'}
    highlights = {}
    types = request.registry[TYPES]
    for doc_type in doc_types:
        type_info = types[doc_type]
        for value in type_info.schema.get('boost_values', ()):
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
        fields = {'embedded.@id', 'embedded.@type'}
        if request.has_permission('search_audit'):
            fields.add('audit.*')
        types = request.registry[TYPES]
        for doc_type in doc_types:
            type_info = types[doc_type]
            if 'columns' not in type_info.schema:
                columns = OrderedDict(
                    (name, type_info.schema['properties'][name].get('title', name))
                    for name in ['@id', 'title', 'description', 'name', 'accession', 'aliases']
                    if name in type_info.schema['properties']
                )
            else:
                columns = type_info.schema['columns']
            fields.update('embedded.' + column for column in columns)
            result['columns'].update(columns)
    return fields


def set_filters(request, query, result):
    """
    Sets filters in the query
    """
    query_filters = query['filter']['and']['filters']
    used_filters = {}
    for field, term in request.params.items():
        if field in ['type', 'limit', 'y.limit', 'x.limit', 'mode', 'annotation',
                     'format', 'frame', 'datastore', 'field', 'region', 'genome',
                     'sort', 'from', 'referrer']:
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


def set_facets(facets, used_filters, principals, doc_types):
    """
    Sets facets in the query using filters
    """
    aggs = {}
    for field, _ in facets:
        exclude = []
        if field == 'type':
            query_field = 'embedded.@type.raw'
            exclude = ['Item']
        elif field.startswith('audit'):
            query_field = field
        else:
            query_field = 'embedded.' + field + '.raw'
        agg_name = field.replace('.', '-')

        terms = [
            {'terms': {'principals_allowed.view': principals}},
            {'terms': {'embedded.@type.raw': doc_types}},
        ]
        # Adding facets based on filters
        for q_field, q_terms in used_filters.items():
            if q_field != field and q_field.startswith('audit'):
                terms.append({'terms': {q_field: q_terms}})
            elif q_field != field and not q_field.endswith('!'):
                terms.append({'terms': {'embedded.' + q_field + '.raw': q_terms}})
            elif q_field != field and q_field.endswith('!'):
                terms.append({'not': {'terms': {'embedded.' + q_field[:-1] + '.raw': q_terms}}})

        aggs[agg_name] = {
            'aggs': {
                agg_name: {
                    'terms': {
                        'field': query_field,
                        'exclude': exclude,
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

    return aggs


def format_results(request, hits):
    """
    Loads results to pass onto UI
    """
    fields_requested = request.params.getall('field')
    if fields_requested:
        frame = 'embedded'
    else:
        frame = request.params.get('frame')

    if frame in ['embedded', 'object']:
        for hit in hits:
            yield hit['_source'][frame]
        return

    # columns
    for hit in hits:
        item = hit['_source']['embedded']
        if 'audit' in hit['_source']:
            item['audit'] = hit['_source']['audit']
        if 'highlight' in hit:
            item['highlight'] = {}
            for key in hit['highlight']:
                item['highlight'][key[9:]] = list(set(hit['highlight'][key]))
        yield item


def search_result_actions(request, doc_types, es_results, position=None):
    actions = {}
    aggregations = es_results['aggregations']

    # generate batch hub URL for experiments
    # TODO we could enable them for Datasets as well here, but not sure how well it will work
    if doc_types == ['Experiment']:
        for bucket in aggregations['assembly']['assembly']['buckets']:
            if bucket['doc_count'] > 0:
                assembly = bucket['key']
                ucsc_assembly = _ASSEMBLY_MAPPER.get(assembly, assembly)
                search_params = request.query_string.replace('&', ',,')
                if not request.params.getall('assembly') or assembly in request.params.getall('assembly'):
                    # filter  assemblies that are not selected
                    hub = request.route_url('batch_hub',
                                            search_params=search_params,
                                            txt='hub.txt')
                    if 'region-search' in request.url and position is not None:
                        actions.setdefault('batch_hub', {})[assembly] = hgConnect + hub + '&db=' + ucsc_assembly + '&position={}'.format(position)
                    else:
                        actions.setdefault('batch_hub', {})[assembly] = hgConnect + hub + '&db=' + ucsc_assembly 

    # generate batch download URL for experiments
    # TODO we could enable them for Datasets as well here, but not sure how well it will work
    if doc_types == ['Experiment'] and any(
            bucket['doc_count'] > 0
            for bucket in aggregations['files-file_type']['files-file_type']['buckets']):
        actions['batch_download'] = request.route_url(
            'batch_download',
            search_params=request.query_string
        )

    return actions


def format_facets(es_results, facets, used_filters, schemas, total):
    result = []
    # Loading facets in to the results
    if 'aggregations' not in es_results:
        return result

    aggregations = es_results['aggregations']
    used_facets = set()
    for field, facet in facets:
        used_facets.add(field)
        agg_name = field.replace('.', '-')
        if agg_name not in aggregations:
            continue
        terms = aggregations[agg_name][agg_name]['buckets']
        if len(terms) < 2:
            continue
        result.append({
            'field': field,
            'title': facet.get('title', field),
            'terms': terms,
            'total': aggregations[agg_name]['doc_count']
        })

    # Show any filters that aren't facets as a fake facet with one entry,
    # so that the filter can be viewed and removed
    for field, values in used_filters.items():
        if field not in used_facets:
            title = field
            for schema in schemas:
                if field in schema['properties']:
                    title = schema['properties'][field].get('title', field)
                    break
            result.append({
                'field': field,
                'title': title,
                'terms': [{'key': v} for v in values],
                'total': total,
                })

    return result


def normalize_query(request):
    types = request.registry[TYPES]
    fixed_types = (
        (k, types[v].name if k == 'type' and v in types else v)
        for k, v in request.params.items()
    )
    qs = urlencode([
        (k.encode('utf-8'), v.encode('utf-8'))
        for k, v in fixed_types
    ])
    return '?' + qs if qs else ''


def iter_long_json(name, iterable, **other):
    import json

    before = (json.dumps(other)[:-1] + ',') if other else '{'
    yield before + json.dumps(name) + ':['

    it = iter(iterable)
    try:
        first = next(it)
    except StopIteration:
        pass
    else:
        yield json.dumps(first)
        for value in it:
            yield ',' + json.dumps(value)

    yield ']}'


@view_config(route_name='search', request_method='GET', permission='search')
def search(context, request, search_type=None):
    """
    Search view connects to ElasticSearch and returns the results
    """
    types = request.registry[TYPES]
    search_base = normalize_query(request)
    result = {
        '@context': request.route_path('jsonld_context'),
        '@id': '/search/' + search_base,
        '@type': ['Search'],
        'title': 'Search',
        'columns': OrderedDict(),
        'filters': [],
    }

    principals = effective_principals(request)
    es = request.registry[ELASTIC_SEARCH]
    es_index = request.registry.settings['snowfort.elasticsearch.index']
    search_audit = request.has_permission('search_audit')

    from_, size = get_pagination(request)

    search_term = prepare_search_term(request)

    if search_type is None:
        doc_types = request.params.getall('type')
        if '*' in doc_types:
            doc_types = ['Item']

    else:
        doc_types = [search_type]

    # Normalize to item_type
    try:
        doc_types = sorted({types[name].name for name in doc_types})
    except KeyError:
        # Check for invalid types
        bad_types = [t for t in doc_types if t not in types]
        msg = "Invalid type: {}".format(', '.join(bad_types))
        raise HTTPBadRequest(explanation=msg)

    # Building query for filters
    if not doc_types:
        if request.params.get('mode') == 'picker':
            doc_types = ['Item']
        else:
            doc_types = DEFAULT_DOC_TYPES
    else:
        for item_type in doc_types:
            ti = types[item_type]
            qs = urlencode([
                (k.encode('utf-8'), v.encode('utf-8'))
                for k, v in request.params.items() if not (k == 'type' and types['Item' if v == '*' else v] is ti)
            ])
            result['filters'].append({
                'field': 'type',
                'term': ti.name,
                'remove': '{}?{}'.format(request.path, qs)
            })
        if len(doc_types) == 1:
            result['views'] = views = []
            views.append({
                'href': request.route_path('report', slash='/') + search_base,
                'title': 'View tabular report',
                'icon': 'table',
            })
            if hasattr(ti.factory, 'matrix'):
                views.append({
                    'href': request.route_path('matrix', slash='/') + search_base,
                    'title': 'View summary matrix',
                    'icon': 'th',
                })

    search_fields, highlights = get_search_fields(request, doc_types)

    # Builds filtered query which supports multiple facet selection
    query = get_filtered_query(search_term,
                               search_fields,
                               sorted(load_columns(request, doc_types, result)),
                               principals,
                               doc_types)

    if not result['columns']:
        del result['columns']

    # If no text search, use match_all query instead of query_string
    if search_term == '*':
        query['query']['match_all'] = {}
        del query['query']['query_string']
    # If searching for more than one type, don't specify which fields to search
    elif len(doc_types) != 1:
        del query['query']['query_string']['fields']

    # Set sort order
    set_sort_order(request, search_term, types, doc_types, query, result)

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

    query['aggs'] = set_facets(facets, used_filters, principals, doc_types)

    # Decide whether to use scan for results.
    do_scan = size is None or size > 1000

    # Execute the query
    if do_scan:
        es_results = es.search(body=query, index=es_index, search_type='count')
    else:
        es_results = es.search(body=query, index=es_index, from_=from_, size=size)

    result['total'] = total = es_results['hits']['total']

    schemas = (types[item_type].schema for item_type in doc_types)
    result['facets'] = format_facets(
        es_results, facets, used_filters, schemas, total)

    # Add batch actions
    result.update(search_result_actions(request, doc_types, es_results))

    # Add all link for collections
    if size is not None and size < result['total']:
        params = [(k, v) for k, v in request.params.items() if k != 'limit']
        params.append(('limit', 'all'))
        result['all'] = '%s?%s' % (request.resource_path(context), urlencode(params))

    if not result['total']:
        # http://googlewebmastercentral.blogspot.com/2014/02/faceted-navigation-best-and-5-of-worst.html
        request.response.status_code = 404
        result['notification'] = 'No results found'
        result['@graph'] = []
        return result

    result['notification'] = 'Success'

    # Format results for JSON-LD
    if not do_scan:
        result['@graph'] = list(format_results(request, es_results['hits']['hits']))
        return result

    # Scan large result sets.
    del query['aggs']
    if size is None:
        hits = scan(es, query=query, index=es_index)
    else:
        hits = scan(es, query=query, index=es_index, from_=from_, size=size)
    graph = format_results(request, hits)

    # Support for request.embed()
    if request.__parent__ is not None:
        result['@graph'] = list(graph)
        return result

    # Stream response using chunked encoding.
    # XXX BeforeRender event listeners not called.
    app_iter = iter_long_json('@graph', graph, **result)
    request.response.content_type = 'application/json'
    if str is bytes:  # Python 2 vs 3 wsgi differences
        request.response.app_iter = app_iter  # Python 2
    else:
        request.response.app_iter = (s.encode('utf-8') for s in app_iter)
    return request.response


@view_config(context=AbstractCollection, permission='list', request_method='GET',
             name='listing')
def collection_view_listing_es(context, request):
    # Switch to change summary page loading options
    if request.datastore != 'elasticsearch':
        return collection_view_listing_db(context, request)

    return search(context, request, context.type_info.name)


@view_config(route_name='report', request_method='GET', permission='search')
def report(context, request):
    types = request.params.getall('type')
    if len(types) != 1:
        msg = 'Report view requires specifying a single type.'
        raise HTTPBadRequest(explanation=msg)

    # Ignore large limits, which make `search` return a Response
    from_, size = get_pagination(request)
    if 'limit' in request.GET and (size is None or size > 1000):
        del request.GET['limit']
    # Reuse search view
    res = search(context, request)

    # change @id, @type, and views
    res['views'][0] = {
        'href': res['@id'],
        'title': 'View results as list',
        'icon': 'list-alt',
    }
    search_base = normalize_query(request)
    res['@id'] = '/report/' + search_base
    res['title'] = 'Report'
    res['@type'] = ['Report']
    return res


@view_config(route_name='matrix', request_method='GET', permission='search')
def matrix(context, request):
    """
    Return search results aggregated by x and y buckets for building a matrix display.
    """
    search_base = normalize_query(request)
    result = {
        '@context': request.route_path('jsonld_context'),
        '@id': request.route_path('matrix', slash='/') + search_base,
        '@type': ['Matrix'],
        'filters': [],
        'notification': '',
    }

    doc_types = request.params.getall('type')
    if len(doc_types) != 1:
        msg = 'Search result matrix currently requires specifying a single type.'
        raise HTTPBadRequest(explanation=msg)
    item_type = doc_types[0]
    types = request.registry[TYPES]
    if item_type not in types:
        msg = 'Invalid type: {}'.format(item_type)
        raise HTTPBadRequest(explanation=msg)
    type_info = types[item_type]
    if not hasattr(type_info.factory, 'matrix'):
        msg = 'No matrix configured for type: {}'.format(item_type)
        raise HTTPBadRequest(explanation=msg)
    schema = type_info.schema
    result['title'] = type_info.name + ' Matrix'

    matrix = result['matrix'] = type_info.factory.matrix.copy()
    matrix['x']['limit'] = request.params.get('x.limit', 20)
    matrix['y']['limit'] = request.params.get('y.limit', 5)
    matrix['search_base'] = request.route_path('search', slash='/') + search_base
    matrix['clear_matrix'] = request.route_path('matrix', slash='/') + '?type=' + item_type

    result['views'] = [
        {
            'href': request.route_path('search', slash='/') + search_base,
            'title': 'View results as list',
            'icon': 'list-alt',
        },
        {
            'href': request.route_path('report', slash='/') + search_base,
            'title': 'View tabular report',
            'icon': 'table',
        }
    ]

    principals = effective_principals(request)
    es = request.registry[ELASTIC_SEARCH]
    es_index = request.registry.settings['snowfort.elasticsearch.index']

    search_term = prepare_search_term(request)

    search_fields, highlights = get_search_fields(request, doc_types)

    # Builds filtered query which supports multiple facet selection
    query = get_filtered_query(search_term,
                               search_fields,
                               [],
                               principals,
                               doc_types)

    if search_term == '*':
        query['query']['match_all'] = {}
        del query['query']['query_string']

    # Setting filters
    used_filters = set_filters(request, query, result)
    # We don't actually need filters in the request,
    # since we're only counting and the aggregations have their own filters
    del query['filter']

    # Adding facets to the query
    facets = [(field, facet) for field, facet in schema['facets'].items() if
              field in matrix['x']['facets'] or field in matrix['y']['facets']]
    if request.has_permission('search_audit'):
        for audit_facet in audit_facets:
            facets.append(audit_facet)
    query['aggs'] = set_facets(facets, used_filters, principals, doc_types)

    # Group results in 2 dimensions
    matrix_terms = []
    for q_field, q_terms in used_filters.items():
        if q_field.startswith('audit.'):
            matrix_terms.append({'terms': {q_field: q_terms}})
        else:
            matrix_terms.append(
                {'terms': {'embedded.' + q_field + '.raw': q_terms}})
    matrix_terms.extend((
        {'terms': {'principals_allowed.view': principals}},
        {'terms': {'embedded.@type.raw': doc_types}},
    ))
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
    es_results = es.search(body=query, index=es_index, search_type='count')

    # Format matrix for results
    aggregations = es_results['aggregations']
    result['matrix']['doc_count'] = total = aggregations['matrix']['doc_count']
    result['matrix']['max_cell_doc_count'] = 0

    # Format facets for results
    result['facets'] = format_facets(
        es_results, facets, used_filters, (schema,), total)

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

    summarize_buckets(
        result['matrix'],
        aggregations['matrix']['x']['buckets'],
        aggregations['matrix'],
        y_groupings + [x_grouping])

    result['matrix']['y'][y_groupings[0]] = aggregations['matrix'][y_groupings[0]]
    result['matrix']['x'].update(aggregations['matrix']['x'])

    # Add batch actions
    result.update(search_result_actions(request, doc_types, es_results))

    # Adding total
    result['total'] = es_results['hits']['total']
    if result['total']:
        result['notification'] = 'Success'
    else:
        # http://googlewebmastercentral.blogspot.com/2014/02/faceted-navigation-best-and-5-of-worst.html
        request.response.status_code = 404
        result['notification'] = 'No results found'

    return result
