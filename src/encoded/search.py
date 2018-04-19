import re
import copy
from urllib.parse import urlencode
from collections import OrderedDict
from pyramid.view import view_config
from pyramid.httpexceptions import HTTPBadRequest
from pyramid.security import effective_principals
from elasticsearch.helpers import scan
from encoded.helpers.helper import (
    format_results,
    search_result_actions
)
from snovault import (
    AbstractCollection,
    TYPES,
)
from snovault.elasticsearch import ELASTIC_SEARCH
from snovault.elasticsearch.create_mapping import TEXT_FIELDS
from snovault.resource_views import collection_view_listing_db
from snovault.helpers.helper import (
    sort_query,
    get_pagination,
    get_filtered_query,
    prepare_search_term,
    set_sort_order,
    get_search_fields,
    list_visible_columns_for_schemas,
    list_result_fields,
    set_filters,
    set_facets,
    format_facets,
    normalize_query,
    iter_long_json
)


CHAR_COUNT = 32


def includeme(config):
    config.add_route('search', '/search{slash:/?}')
    config.add_route('report', '/report{slash:/?}')
    config.add_route('matrix', '/matrix{slash:/?}')
    config.add_route('news', '/news/')
    config.add_route('audit', '/audit/')
    config.add_route('summary', '/summary{slash:/?}')
    config.scan(__name__)


sanitize_search_string_re = re.compile(r'[\\\+\-\&\|\!\(\)\{\}\[\]\^\~\:\/\\\*\?]')

audit_facets = [
    ('audit.ERROR.category', {'title': 'Audit category: ERROR'}),
    ('audit.NOT_COMPLIANT.category', {'title': 'Audit category: NOT COMPLIANT'}),
    ('audit.WARNING.category', {'title': 'Audit category: WARNING'}),
    ('audit.INTERNAL_ACTION.category', {'title': 'Audit category: DCC ACTION'})
]


DEFAULT_DOC_TYPES = [
    'AntibodyLot',
    'Award',
    'Biosample',
    'Dataset',
    'GeneticModification',
    'Page',
    'Pipeline',
    'Publication',
    'Software',
    'Target',
]


@view_config(route_name='search', request_method='GET', permission='search')
def search(context, request, search_type=None, return_generator=False):
    """
    Search view connects to ElasticSearch and returns the results
    """
    # sets up ES and checks permissions/principles

    # gets schemas for all types
    types = request.registry[TYPES]
    search_base = normalize_query(request)
    result = {
        '@context': request.route_path('jsonld_context'),
        '@id': '/search/' + search_base,
        '@type': ['Search'],
        'title': 'Search',
        'filters': [],
    }
    principals = effective_principals(request)
    es = request.registry[ELASTIC_SEARCH]
    es_index = '_all'
    search_audit = request.has_permission('search_audit')

    # extract from/size from query parameters
    from_, size = get_pagination(request)

    # looks at searchTerm query parameter, sets to '*' if none, and creates antlr/lucene query for fancy stuff
    search_term = prepare_search_term(request)

    # converts type= query parameters to list of doc_types to search, "*" becomes super class Item
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

    # Clear Filters path -- make a path that clears all non-datatype filters.
    # this saves the searchTerm when you click clear filters
    # http://stackoverflow.com/questions/16491988/how-to-convert-a-list-of-strings-to-a-query-string#answer-16492046
    searchterm_specs = request.params.getall('searchTerm')
    searchterm_only = urlencode([("searchTerm", searchterm) for searchterm in searchterm_specs])
    if searchterm_only:
        # Search term in query string; clearing keeps that
        clear_qs = searchterm_only
    else:
        # Possibly type(s) in query string
        clear_qs = urlencode([("type", typ) for typ in doc_types])
    result['clear_filters'] = request.route_path('search', slash='/') + (('?' + clear_qs) if clear_qs else '')

    # Building query for filters
    if not doc_types:
        # For form editing embedded searches
        if request.params.get('mode') == 'picker':
            doc_types = ['Item']
        # For /search/ with no type= use defalts
        else:
            doc_types = DEFAULT_DOC_TYPES
    else:
        # TYPE filters that were set by UI for labeling, only seen with >1 types
        # Probably this is why filtering Items with subclasses doesn't work right
        # i.e., search/?type=Dataset   Type is not a regular filter/facet.
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

        # Add special views like Report and Matrix if search is a single type
        if len(doc_types) == 1:
            result['views'] = views = []
            views.append({
                'href': request.route_path('report', slash='/') + search_base,
                'title': 'View tabular report',
                'icon': 'table',
            })
            # matrix is encoded in schema for type
            if hasattr(ti.factory, 'matrix'):
                views.append({
                    'href': request.route_path('matrix', slash='/') + search_base,
                    'title': 'View summary matrix',
                    'icon': 'th',
                })
            if hasattr(ti.factory, 'summary_data'):
                views.append({
                    'href': request.route_path('summary', slash='/') + search_base,
                    'title': 'View summary report',
                    'icon': 'summary',
                })

    search_fields, highlights = get_search_fields(request, doc_types)

    # Builds filtered query which supports multiple facet selection
    query = get_filtered_query(search_term,
                               search_fields,
                               sorted(list_result_fields(request, doc_types)),
                               principals,
                               doc_types)

    #  Columns is used in report view
    schemas = [types[doc_type].schema for doc_type in doc_types]
    columns = list_visible_columns_for_schemas(request, schemas)
    # and here it is attached to the result for the UI
    if columns:
        result['columns'] = columns

    # If no text search, use match_all query instead of query_string
    if search_term == '*':
        # query['query']['match_all'] = {}
        del query['query']['query_string']
    # If searching for more than one type, don't specify which fields to search
    else:
        # del query['query']['bool']['must']['multi_match']['fields']
        query['query']['query_string']['fields'].extend(['_all', '*.uuid', '*.md5sum', '*.submitted_file_name'])

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

    # Display all audits if logged in, or all but INTERNAL_ACTION if logged out
    for audit_facet in audit_facets:
        if search_audit and 'group.submitter' in principals or 'INTERNAL_ACTION' not in audit_facet[0]:
            facets.append(audit_facet)

    query['aggs'] = set_facets(facets, used_filters, principals, doc_types)

    # Search caching uses JSON as cache key, hence sorting the query
    query = sort_query(query)

    # Decide whether to use scan for results.
    do_scan = size is None or size > 1000

    # When type is known, route search request to relevant index
    if not request.params.get('type') or 'Item' in doc_types:
        es_index = '_all'
    else:
        es_index = [types[type_name].item_type for type_name in doc_types if hasattr(types[type_name], 'item_type')]

    # Execute the query
    if do_scan:
        es_results = es.search(body=query, index=es_index, search_type='query_then_fetch')
    else:
        es_results = es.search(body=query, index=es_index, from_=from_, size=size, request_cache=True)

    result['total'] = total = es_results['hits']['total']

    schemas = (types[item_type].schema for item_type in doc_types)
    result['facets'] = format_facets(
        es_results, facets, used_filters, schemas, total, principals)

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
        return result if not return_generator else []

    result['notification'] = 'Success'
    # Format results for JSON-LD
    if not do_scan:
        graph = format_results(request, es_results['hits']['hits'], result)
        if return_generator:
            return graph
        else:
            result['@graph'] = list(graph)
            return result

    # Scan large result sets.
    del query['aggs']
    if size is None:
        # preserve_order=True has unexpected results in clustered environment
        # https://github.com/elastic/elasticsearch-py/blob/master/elasticsearch/helpers/__init__.py#L257
        hits = scan(es, query=query, index=es_index, preserve_order=False)
    else:
        hits = scan(es, query=query, index=es_index, from_=from_, size=size, preserve_order=False)
    graph = format_results(request, hits, result)

    # Support for request.embed() and `return_generator`
    if request.__parent__ is not None or return_generator:
        if return_generator:
            return graph
        else:
            result['@graph'] = list(graph)
            return result

    # Stream response using chunked encoding.
    # XXX BeforeRender event listeners not called.
    app_iter = iter_long_json('@graph', graph, result)
    request.response.content_type = 'application/json'
    if str is bytes:  # Python 2 vs 3 wsgi differences
        request.response.app_iter = app_iter  # Python 2
    else:
        request.response.app_iter = (s.encode('utf-8') for s in app_iter)
    return request.response


def iter_search_results(context, request):
    return search(context, request, return_generator=True)


@view_config(context=AbstractCollection, permission='list', request_method='GET',
             name='listing')
def collection_view_listing_es(context, request):
    # Switch to change summary page loading options
    if request.datastore != 'elasticsearch':
        return collection_view_listing_db(context, request)

    return search(context, request, context.type_info.name)


@view_config(route_name='report', request_method='GET', permission='search')
def report(context, request):
    doc_types = request.params.getall('type')
    if len(doc_types) != 1:
        msg = 'Report view requires specifying a single type.'
        raise HTTPBadRequest(explanation=msg)

    # schemas for all types
    types = request.registry[TYPES]

    # Get the subtypes of the requested type
    try:
        sub_types = types[doc_types[0]].subtypes
    except KeyError:
        # Raise an error for an invalid type
        msg = "Invalid type: " + doc_types[0]
        raise HTTPBadRequest(explanation=msg)

    # Raise an error if the requested type has subtypes.
    if len(sub_types) > 1:
        msg = 'Report view requires a type with no child types.'
        raise HTTPBadRequest(explanation=msg)

    # Ignore large limits, which make `search` return a Response
    # -- UNLESS we're being embedded by the download_report view
    from_, size = get_pagination(request)
    if ('limit' in request.GET and request.__parent__ is None and (size is None or size > 1000)):
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
    res['download_tsv'] = request.route_path('report_download') + search_base
    res['title'] = 'Report'
    res['@type'] = ['Report']
    res['non_sortable'] = TEXT_FIELDS
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
    search_audit = request.has_permission('search_audit')

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
    if type_info.name is 'Annotation':
        result['title'] = 'Encyclopedia'
    else:
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
    if hasattr(type_info.factory, 'summary_data'):
        result['views'].append({
            'href': request.route_path('summary', slash='/') + search_base,
            'title': 'View summary report',
            'icon': 'summary',
        })

    principals = effective_principals(request)
    es = request.registry[ELASTIC_SEARCH]
    es_index = '_all'

    search_term = prepare_search_term(request)

    search_fields, highlights = get_search_fields(request, doc_types)

    # Builds filtered query which supports multiple facet selection
    query = get_filtered_query(search_term,
                               search_fields,
                               [],
                               principals,
                               doc_types)

    if search_term == '*':
        # query['query']['match_all'] = {}
        del query['query']['query_string']
    # If searching for more than one type, don't specify which fields to search
    else:
        # del query['query']['bool']['must']['multi_match']['fields']
        query['query']['query_string']['fields'].extend(['_all', '*.uuid', '*.md5sum', '*.submitted_file_name'])

    # Setting filters.
    # Rather than setting them at the top level of the query
    # we collect them for use in aggregations later.
    query_filters = query['post_filter'].pop('bool')
    filter_collector = {'post_filter': {'bool': query_filters}}
    used_filters = set_filters(request, filter_collector, result)
    filters = filter_collector['post_filter']['bool']['must']
    negative_filters = filter_collector['post_filter']['bool']['must_not']

    # Adding facets to the query
    facets = [(field, facet) for field, facet in schema['facets'].items() if
              field in matrix['x']['facets'] or field in matrix['y']['facets']]

    # Display all audits if logged in, or all but INTERNAL_ACTION if logged out
    for audit_facet in audit_facets:
        if search_audit and 'group.submitter' in principals or 'INTERNAL_ACTION' not in audit_facet[0]:
            facets.append(audit_facet)

    query['aggs'] = set_facets(facets, used_filters, principals, doc_types)

    # Group results in 2 dimensions
    x_grouping = matrix['x']['group_by']
    y_groupings = matrix['y']['group_by']
    x_agg = {
        "terms": {
            "field": 'embedded.' + x_grouping,
            "size": 999999,  # no limit
        },
    }
    aggs = {x_grouping: x_agg}
    for field in reversed(y_groupings):
        aggs = {
            field: {
                "terms": {
                    "field": 'embedded.' + field,
                    "size": 999999,  # no limit
                },
                "aggs": aggs,
            },
        }
    aggs['x'] = x_agg
    query['aggs']['matrix'] = {
        "filter": {
            "bool": {
                "must": filters,
                "must_not": negative_filters
            }
        },
        "aggs": aggs,
    }

    # Execute the query
    es_results = es.search(body=query, index=es_index)

    # Format matrix for results
    aggregations = es_results['aggregations']
    result['matrix']['doc_count'] = total = aggregations['matrix']['doc_count']
    result['matrix']['max_cell_doc_count'] = 0

    # Format facets for results
    result['facets'] = format_facets(
        es_results, facets, used_filters, (schema,), total, principals)

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


@view_config(route_name='news', request_method='GET', permission='search')
def news(context, request):
    """
    Return search results for news Page items.
    """
    types = request.registry[TYPES]
    es = request.registry[ELASTIC_SEARCH]
    es_index = 'page'
    search_base = normalize_query(request)
    principals = effective_principals(request)

    # Set up initial results metadata; we'll add the search results to them later.
    result = {
        '@context': request.route_path('jsonld_context'),
        '@id': '/news/' + search_base,
        '@type': ['News'],
        'filters': [],
        'notification': '',
    }

    # We have no query string to specify a type, but we know we want 'Page' for news items.
    doc_types = ['Page']

    # Get the fields we want to receive from the search.
    search_fields, highlights = get_search_fields(request, doc_types)

    # Build filtered query for Page items for news.
    query = get_filtered_query('*',
                               search_fields,
                               sorted(list_result_fields(request, doc_types)),
                               principals,
                               doc_types)

    # Keyword search on news items is not implemented yet
    del query['query']['query_string']
    # If searching for more than one type, don't specify which fields to search

    # Set sort order to sort by date_created.
    sort = OrderedDict()
    result_sort = OrderedDict()
    sort['embedded.date_created'] = result_sort['date_created'] = {
        'order': 'desc',
        'unmapped_type': 'keyword',
    }
    query['sort'] = sort
    result['sort'] = result_sort

    # Set filters; has side effect of setting result['filters']. We add some static terms since we
    # have search parameters not specified in the query string.
    used_filters = set_filters(request, query, result, [('type', 'Page'), ('news', 'true'), ('status', 'released')])

    # Build up the facets to search.
    facets = []
    if len(doc_types) == 1 and 'facets' in types[doc_types[0]].schema:
        facets.extend(types[doc_types[0]].schema['facets'].items())

    # Perform the search of news items.
    query['aggs'] = set_facets(facets, used_filters, principals, doc_types)
    es_results = es.search(body=query, index=es_index, doc_type=es_index, from_=0, size=25)
    total = es_results['hits']['total']

    # Return 404 if no results found.
    if not total:
        # http://googlewebmastercentral.blogspot.com/2014/02/faceted-navigation-best-and-5-of-worst.html
        request.response.status_code = 404
        result['notification'] = 'No results found'
        result['@graph'] = []
        return result

    # At this stage, we know we have good results.
    result['notification'] = 'Success'
    result['total'] = total

    # Place the search results into the @graph property.
    graph = format_results(request, es_results['hits']['hits'], result)
    result['@graph'] = list(graph)

    # Insert the facet data into the results.
    types = request.registry[TYPES]
    schemas = [types[doc_type].schema for doc_type in doc_types]
    result['facets'] = format_facets(es_results, facets, used_filters, schemas, total, principals)

    return result


@view_config(route_name='audit', request_method='GET', permission='search')
def audit(context, request):
    """
    Return search results aggregated by x and y buckets for building a matrix display.
    """
    search_base = normalize_query(request)
    result = {
        '@context': request.route_path('jsonld_context'),
        '@id': request.route_path('audit', slash='/') + search_base,
        '@type': ['AuditMatrix'],
        'filters': [],
        'notification': '',
    }
    search_audit = request.has_permission('search_audit')

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
    if type_info.name is 'Annotation':
        result['title'] = 'Encyclopedia'
    else:
        result['title'] = type_info.name + ' Matrix'

    # Because the formatting of the query edits the sub-objects of the matrix, we need to
    # deepcopy the matrix so the original type_info.factory.matrix is not modified, allowing
    # /matrix to get the correct data and to not be able to access the /audit data.
    temp_matrix = copy.deepcopy(type_info.factory.matrix)
    matrix = result['matrix'] = temp_matrix
    matrix['x']['limit'] = request.params.get('x.limit', 20)
    matrix['y']['limit'] = request.params.get('y.limit', 5)
    matrix['search_base'] = request.route_path('search', slash='/') + search_base
    matrix['clear_matrix'] = request.route_path('audit', slash='/') + '?type=' + item_type

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
    es_index = '_all'

    search_term = prepare_search_term(request)

    search_fields, highlights = get_search_fields(request, doc_types)

    # Builds filtered query which supports multiple facet selection
    query = get_filtered_query(search_term,
                               search_fields,
                               [],
                               principals,
                               doc_types)

    if search_term == '*':
        # query['query']['match_all'] = {}
        del query['query']['query_string']
    # If searching for more than one type, don't specify which fields to search
    else:
        # del query['query']['bool']['must']['multi_match']['fields']
        query['query']['query_string']['fields'].extend(['_all', '*.uuid', '*.md5sum', '*.submitted_file_name'])

    # Setting filters.
    # Rather than setting them at the top level of the query
    # we collect them for use in aggregations later.
    query_filters = query['post_filter'].pop('bool')
    filter_collector = {'post_filter': {'bool': query_filters}}
    used_filters = set_filters(request, filter_collector, result)
    filters = filter_collector['post_filter']['bool']['must']
    negative_filters = filter_collector['post_filter']['bool']['must_not']

    # Adding facets to the query
    facets = [(field, facet) for field, facet in schema['facets'].items() if
              field in matrix['x']['facets'] or field in matrix['y']['facets']]

    # Display all audits if logged in, or all but INTERNAL_ACTION if logged out
    for audit_facet in audit_facets:
        if search_audit and 'group.submitter' in principals or 'INTERNAL_ACTION' not in audit_facet[0]:
            facets.append(audit_facet)

    # To get list of audit categories from facets
    audit_field_list_copy = []
    audit_field_list = []
    for item in facets:
        if item[0].rfind('audit.') > -1:
            audit_field_list.append(item)

    audit_field_list_copy = audit_field_list.copy()

    # Gets just the fields from the tuples from facet data
    for item in audit_field_list_copy:  # for each audit label
        temp = item[0]
        audit_field_list[audit_field_list.index(item)] = temp  # replaces list with just audit field

    query['aggs'] = set_facets(facets, used_filters, principals, doc_types)

    # Group results in 2 dimensions
    x_grouping = matrix['x']['group_by']
    y_groupings = audit_field_list

    # Creates a list of fields used in no audit row
    no_audits_groupings = ['no.audit.error', 'no.audit.not_compliant', 'no.audit.warning']

    x_agg = {
        "terms": {
            "field": 'embedded.' + x_grouping,
            "size": 999999,  # no limit
        },
    }

    # aggs query for audit category rows
    aggs = {
        'audit.ERROR.category': {
            'aggs': {
                x_grouping: x_agg
            },
            'terms': {
                'field': 'audit.ERROR.category', 'size': 999999
            }
        },
        'audit.WARNING.category': {
            'aggs': {
                x_grouping: x_agg
            },
            'terms': {
                'field': 'audit.WARNING.category', 'size': 999999
            }
        },
        'audit.NOT_COMPLIANT.category': {
            'aggs': {
                x_grouping: x_agg
            },
            'terms': {
                'field': 'audit.NOT_COMPLIANT.category', 'size': 999999
            }
        }

    }

    # This is a nested query with error as the top most level and warning as the innermost level.
    # It allows for there to be multiple missing fields in the query.
    # To construct this we go through the no_audits_groupings backwards and construct the query
    # from the inside out.
    temp = {}
    temp_copy = {}
    for group in reversed(no_audits_groupings):
        temp = {
            "missing": {
                "field": audit_field_list[no_audits_groupings.index(group)]
            },
            "aggs": {
                x_grouping: x_agg
            },
        }
        # If not the last element in no_audits_groupings then add the inner query
        # inside the next category query. Therefore, as temp is updated, it sets the old temp,
        # which is now temp_copy, within itself. This creates the nested structure.
        if (no_audits_groupings.index(group) + 1) < len(no_audits_groupings):
            temp["aggs"][no_audits_groupings[(no_audits_groupings.index(group) + 1)]] = temp_copy
        temp_copy = copy.deepcopy(temp)

    # This adds the outermost grouping label to temp.
    update_temp = {}
    update_temp[no_audits_groupings[0]] = temp

    # Aggs query gets updated with no audits queries.
    aggs.update(update_temp)

    # If internal action data is able to be seen in facets (if logged in) then add it to aggs for
    # both: 1) an audit category row for Internal Action and 2) the no audits row as innermost
    # level of nested query to create a no audits at all row within no audits.
    # Additionally, add it to the no_audits_groupings list to be used in summarize_no_audits later.
    if "audit.INTERNAL_ACTION.category" in facets[len(facets) - 1]:
        aggs['audit.INTERNAL_ACTION.category'] = {
            'aggs': {
                x_grouping: x_agg
            },
            'terms': {
                'field': 'audit.INTERNAL_ACTION.category', 'size': 999999
            }
        }
        aggs['no.audit.error']['aggs']['no.audit.not_compliant']['aggs']['no.audit.warning']['aggs']['no.audit.internal_action'] = {
            "missing": {"field": "audit.INTERNAL_ACTION.category"},
            "aggs": {x_grouping: x_agg}
        }
        no_audits_groupings.append("no.audit.internal_action")

    aggs['x'] = x_agg
    query['aggs']['matrix'] = {
        "filter": {
            "bool": {
                "must": filters,
                "must_not": negative_filters
            }
        },
        "aggs": aggs,
    }

    # Execute the query
    es_results = es.search(body=query, index=es_index)

    # Format matrix for results
    aggregations = es_results['aggregations']
    result['matrix']['doc_count'] = total = aggregations['matrix']['doc_count']
    result['matrix']['max_cell_doc_count'] = 0

    # Format facets for results
    result['facets'] = format_facets(
        es_results, facets, used_filters, (schema,), total, principals)

    # For each audit category row.
    # Convert Elasticsearch returned matrix search data to a form usable by the front end matrix
    # code, using only the 'matrix' object within the search data. It contains matrix search
    # results in 'bucket' arrays, with the exact terms being defined in the .py file for the object
    # we're querying in the object's 'matrix' property.
    #
    # matrix (dictionary): 'matrix' object within the Elasticsearch matrix search results,
    #        containing all the data to render the matrix and its headers, but not the facets that
    #        appear along the top and bottom.
    # x_buckets (dictionary): 'x' object within the Elasticsearch matrix search results, containing
    #        the headers that give titles to each column of the chart, as well as summary counts
    #        we don't currently use on the front end.
    # outer_bucket (list): search result bucket containing the term from which to group by.
    # grouping_fields (list): List of audit categories that is hard coded above.

    def summarize_buckets(matrix, x_buckets, outer_bucket, grouping_fields):
        # Loop through each audit category and get proper search result data and format it
        for category in grouping_fields:  # for each audit category
            counts = {}
            # Go through each bucket
            for bucket in outer_bucket[category]['buckets']:
                counts = {}
                # Go through each assay for a key/row and get count and add to counts dictionary
                # that keeps track of counts for each key/row.
                for assay in bucket['assay_title']['buckets']:
                    doc_count = assay['doc_count']
                    if doc_count > matrix['max_cell_doc_count']:
                        matrix['max_cell_doc_count'] = doc_count
                    if 'key' in assay:
                        counts[assay['key']] = doc_count

                # We now have `counts` containing each displayed key and the corresponding count for a
                # row of the matrix. Convert that to a list of counts (cell values for a row of the
                # matrix) to replace the existing bucket for the given grouping_fields term with a
                # simple list of counts without their keys -- the position within the list corresponds
                # to the keys within 'x'.
                summary = []
                for xbucket in x_buckets:
                    summary.append(counts.get(xbucket['key'], 0))
                bucket['assay_title'] = summary

    # For the no audits row.
    # Convert Elasticsearch returned matrix search data to a form usable by the front end matrix
    # code, using only the 'matrix' object within the search data. It contains matrix search
    # results in 'bucket' arrays, with the exact terms being defined in the .py file for the object
    # we're querying in the object's 'matrix' property.
    #
    # matrix (dictionary): 'matrix' object within the Elasticsearch matrix search results,
    #        containing all the data to render the matrix and its headers, but not the facets that
    #        appear along the top and bottom.
    # x_buckets (dictionary): 'x' object within the Elasticsearch matrix search results, containing
    #        the headers that give titles to each column of the chart, as well as summary counts
    #        we don't currently use on the front end.
    # outer_bucket (list): search result bucket containing the term from which to group by.
    # grouping_fields (list): List of no audit labels in order that is hard coded above. Allows
    #        for recursion through the nested query.
    # aggregations (list): same as outer_bucket. Allows for aggregations to be modified so that
    #        the nested query that allows for each level of no audits can become separate rows
    #        under the overall no audits row.

    def summarize_no_audits(matrix, x_buckets, outer_bucket, grouping_fields, aggregations):
        # Loop by recursion through grouping_fields until we get the terminal no audit field. So
        # get the initial no audit field in the list and save the rest for the recursive call.
        group_by = grouping_fields[0]
        grouping_fields = grouping_fields[1:]

        # If there are still items in grouping_fields, then loop by recursion until there is
        # nothing left in grouping_fields.
        if grouping_fields:
            summarize_no_audits(matrix, x_buckets, outer_bucket[group_by], grouping_fields, aggregations)

        counts = {}
        # We have recursed through to the last grouping_field in the array given in the top-
        # level summarize_buckets call. Now we can get down to actually converting the search
        # result data. First loop through each element in the term's 'buckets' which contain
        # displayable key and a count.
        for assay in outer_bucket[group_by]['assay_title']['buckets']:
            # Grab the count for the row, and keep track of the maximum count we find by
            # mutating the max_cell_doc_count property of the matrix for the front end to use
            # to color the cells. Then we add to a counts dictionary that keeps track of each
            # displayed term and the corresponding count.
            doc_count = assay['doc_count']
            if doc_count > matrix['max_cell_doc_count']:
                matrix['max_cell_doc_count'] = doc_count
            if 'key' in assay:
                counts[assay['key']] = doc_count

        # We now have `counts` containing each displayed key and the corresponding count for a
        # row of the matrix. Convert that to a list of counts (cell values for a row of the
        # matrix) to replace the existing bucket for the given grouping_fields term with a
        # simple list of counts without their keys -- the position within the list corresponds
        # to the keys within 'x'.
        summary = []
        for xbucket in x_buckets:
            summary.append(counts.get(xbucket['key'], 0))
        # Set proper results in aggregations. Instead of keeping the nested structure from the
        # query, set each no audit category as a separate item. Delete the other information
        # from the nested queries. *Not really sure if this information is necessary so I just
        # took it out.*
        aggregations[group_by] = outer_bucket[group_by]['assay_title']
        aggregations[group_by]['assay_title'] = summary
        aggregations[group_by].pop("buckets", None)
        aggregations[group_by].pop("sum_other_doc_count", None)
        aggregations[group_by].pop("doc_count_error_upper_bound", None)

    summarize_buckets(
        result['matrix'],
        aggregations['matrix']['x']['buckets'],
        aggregations['matrix'],
        y_groupings)

    summarize_no_audits(
        result['matrix'],
        aggregations['matrix']['x']['buckets'],
        aggregations['matrix'],
        no_audits_groupings,
        aggregations['matrix'])

    # There is no generated key for the no audit categories, so we need to manually add them so
    # that they will be able to be read in the JS file.
    aggregations['matrix']['no.audit.error']['key'] = 'no errors'
    aggregations['matrix']['no.audit.not_compliant']['key'] = 'no errors and compliant'
    aggregations['matrix']['no.audit.warning']['key'] = 'no errors, compliant, and no warnings'
    if "no.audit.internal_action" in no_audits_groupings:
        aggregations['matrix']['no.audit.internal_action']['key'] = "no audits"

    # We need to format the no audits entries as subcategories in an overal 'no_audits' row.
    # To do this, we need to make it the same format as the audit category entries so the JS
    # file will read them and treat them equally.
    aggregations['matrix']['no_audits'] = {}
    aggregations['matrix']['no_audits']['buckets'] = []

    # Add the no audit categories into the overall no_audits entry.
    for category in aggregations['matrix']:
        if "no.audit" in category:
            aggregations['matrix']['no_audits']['buckets'].append(aggregations['matrix'][category])

    # Remove the no audit categories now that they have been added to the overall no_audits row.
    for audit in no_audits_groupings:
        aggregations['matrix'].pop(audit)

    result['matrix']['y']['label'] = "Audit Category"
    result['matrix']['y']['group_by'][0] = "audit_category"
    result['matrix']['y']['group_by'][1] = "audit_label"

    # Formats all audit categories into readable/usable format for auditmatrix.js
    bucket_audit_category_list = []
    for audit in aggregations['matrix']:
        if "audit" in audit:
            audit_category_dict = {}
            audit_category_dict['audit_label'] = aggregations['matrix'][audit]
            audit_category_dict['key'] = audit
            bucket_audit_category_list.append(audit_category_dict)

    bucket_audit_category_dict = {}
    bucket_audit_category_dict['buckets'] = bucket_audit_category_list

    # Add correctly formatted data to results
    result['matrix']['y']['audit_category'] = bucket_audit_category_dict
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


@view_config(route_name='summary', request_method='GET', permission='search')
def summary(context, request):
    search_base = normalize_query(request)
    result = {
        '@context': request.route_path('jsonld_context'),
        '@id': request.route_path('summary', slash='/') + search_base,
        '@type': ['Summary'],
        'filters': [],
        'notification': '',
    }
    doc_types = request.params.getall('type')
    if len(doc_types) != 1:
        msg = 'Summary currently requires specifying a single type.'
        raise HTTPBadRequest(explanation=msg)
    item_type = doc_types[0]
    types = request.registry[TYPES]
    if item_type not in types:
        msg = 'Invalid type: {}'.format(item_type)
        raise HTTPBadRequest(explanation=msg)
    type_info = types[item_type]
    if not hasattr(type_info.factory, 'summary_data'):
        msg = 'No summary configured for type: {}'.format(item_type)
        raise HTTPBadRequest(explanation=msg)
    schema = type_info.schema
    summary = result['summary'] = type_info.factory.summary_data.copy()
    summary['search_base'] = request.route_path('search', slash='/') + search_base
    summary['clear_summary'] = request.route_path('summary', slash='/') + '?type=' + item_type
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
        },
        {
            'href': request.route_path('matrix', slash='/') + search_base,
            'title': 'View summary matrix',
            'icon': 'th',
        }
    ]
    result['title'] = type_info.name + ' Summary'
    es = request.registry[ELASTIC_SEARCH]
    es_index = '_all'
    principals = effective_principals(request)
    search_term = prepare_search_term(request)
    search_fields, highlights = get_search_fields(request, doc_types)
    clear_qs = urlencode([("type", typ) for typ in doc_types])
    result['clear_filters'] = request.route_path('summary', slash='/') + (('?' + clear_qs) if clear_qs else '')
    query = get_filtered_query(search_term,
                               search_fields,
                               [],
                               principals,
                               doc_types)
    if search_term == '*':
        del query['query']['query_string']
    else:
        query['query']['query_string']['fields'].extend(['_all', '*.uuid', '*.md5sum', '*.submitted_file_name'])
    query_filters = query['post_filter'].pop('bool')
    filter_collector = {'post_filter': {'bool': query_filters}}
    used_filters = set_filters(request, filter_collector, result)
    filters = filter_collector['post_filter']['bool']['must']
    facets = [(field, facet) for field, facet in schema['facets'].items() if
              field in summary['x']['facets'] or field in summary['y']['facets']]
    query['aggs'] = set_facets(facets, used_filters, principals, doc_types)
    x_grouping = summary['x']['group_by']
    y_groupings = summary['y']['group_by']
    summary_groupings = summary['grouping']
    x_agg = {
        "terms": {
            "field": 'embedded.' + x_grouping,
            "size": 999999,
        },
    }
    aggs = {x_grouping: x_agg}
    for field in reversed(y_groupings):
        aggs = {
            field: {
                "terms": {
                    "field": 'embedded.' + field,
                    "size": 999999,
                },
                "aggs": aggs,
            },
        }
    summary_aggs = None
    for field in reversed(summary_groupings):
        sub_summary_aggs = summary_aggs
        summary_aggs = {
            field: {
                "terms": {
                    "field": 'embedded.' + field,
                    "size": 999999,
                },
            },
        }
        if sub_summary_aggs:
            summary_aggs[field]['aggs'] = sub_summary_aggs
    aggs['x'] = x_agg
    query['aggs']['summary'] = {
        "filter": {
            "bool": {
                "must": filters,
            }
        },
        "aggs": summary_aggs,
    }
    query['size'] = 0
    es_results = es.search(body=query, index=es_index)
    aggregations = es_results['aggregations']
    result['summary']['doc_count'] = total = aggregations['summary']['doc_count']
    result['summary']['max_cell_doc_count'] = 0
    result['summary'][summary_groupings[0]] = es_results['aggregations']['summary']
    result['facets'] = format_facets(
        es_results, facets, used_filters, (schema,), total, principals)
    return result
