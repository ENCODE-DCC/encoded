import re
from pyramid.view import view_config
from snovault import (
    AbstractCollection,
    TYPES,
)
from snovault.elasticsearch import ELASTIC_SEARCH
from snovault.resource_views import collection_view_listing_db
from elasticsearch.helpers import scan
from pyramid.httpexceptions import HTTPBadRequest
from pyramid.security import effective_principals
from urllib.parse import urlencode
from collections import OrderedDict


'''
This is a generic faceted search interface with a "list object" view and a "csv report view".
It can be customized to your application
'''

CHAR_COUNT = 32


def includeme(config):
    config.add_route('search', '/search{slash:/?}')
    config.add_route('report', '/report{slash:/?}')
    config.scan(__name__)

audit_facets = [
    ('audit.ERROR.category', {'title': 'Audit category: ERROR'}),
    ('audit.NOT_COMPLIANT.category', {'title': 'Audit category: NOT COMPLIANT'}),
    ('audit.WARNING.category', {'title': 'Audit category: WARNING'}),
    ('audit.INTERNAL_ACTION.category', {'title': 'Audit category: DCC ACTION'})
]

sanitize_search_string_re = re.compile(r'[\\\+\-\&\|\!\(\)\{\}\[\]\^\~\:\/\\\*\?]')


DEFAULT_DOC_TYPES = [
    'Page',
    'Lab',
    'Snowset',
    'Snowball',
    'Snowfort',
    'Snowflake',
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

    # avoid interpreting slashes as regular expressions
    search_term = search_term.replace('/', r'\/')
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
        return True

    return False


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


def list_visible_columns_for_schemas(request, schemas):
    """
    Returns mapping of default columns for a set of schemas.
    """
    columns = OrderedDict({'@id': {'title': 'ID'}})
    for schema in schemas:
        if 'columns' in schema:
            columns.update(schema['columns'])
        else:
            # default columns if not explicitly specified
            columns.update(OrderedDict(
                (name, {
                    'title': schema['properties'][name].get('title', name)
                })
                for name in [
                    '@id', 'title', 'description', 'name', 'accession',
                    'aliases'
                ] if name in schema['properties']
            ))

    fields_requested = request.params.getall('field')
    if fields_requested:
        limited_columns = OrderedDict()
        for field in fields_requested:
            if field in columns:
                limited_columns[field] = columns[field]
            else:
                for schema in schemas:
                    if field in schema['properties']:
                        limited_columns[field] = {
                            'title': schema['properties'][field]['title']
                        }
                        break
        columns = limited_columns

    return columns


def list_result_fields(request, doc_types):
    """
    Returns set of fields that are requested by user or default fields
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
        schemas = [types[doc_type].schema for doc_type in doc_types]
        columns = list_visible_columns_for_schemas(request, schemas)
        fields.update('embedded.' + column for column in columns)
    return fields


def set_filters(request, query, result):
    """
    Sets filters in the query
    """
    query_filters = query['filter']['and']['filters']
    used_filters = {}
    for field, term in request.params.items():
        if field in ['type', 'limit', 'mode', 'format', 'frame', 'datastore', 'field',
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

    ''' hook to add ui Actions, encode uses this to generate visualize links based on aggregations'''
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
def search(context, request, search_type=None, return_generator=False):
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
        'filters': [],
    }
    principals = effective_principals(request)
    es = request.registry[ELASTIC_SEARCH]
    es_index = request.registry.settings['snovault.elasticsearch.index']
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

    # Clear Filters path -- make a path that clears all non-datatype filters.
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
                               sorted(list_result_fields(request, doc_types)),
                               principals,
                               doc_types)

    schemas = [types[doc_type].schema for doc_type in doc_types]
    columns = list_visible_columns_for_schemas(request, schemas)
    if columns:
        result['columns'] = columns

    # If no text search, use match_all query instead of query_string
    if search_term == '*':
        query['query']['match_all'] = {}
        del query['query']['query_string']
    # If searching for more than one type, don't specify which fields to search
    elif len(doc_types) != 1:
        del query['query']['query_string']['fields']
        query['query']['query_string']['fields'] = ['_all', '*.uuid', '*.md5sum', '*.submitted_file_name']

    # Set sort order
    has_sort = set_sort_order(request, search_term, types, doc_types, query, result)

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
        return result if not return_generator else []

    result['notification'] = 'Success'

    # Format results for JSON-LD
    if not do_scan:
        graph = format_results(request, es_results['hits']['hits'])
        if return_generator:
            return graph
        else:
            result['@graph'] = list(graph)
            return result

    # Scan large result sets.
    del query['aggs']
    if size is None:
        hits = scan(es, query=query, index=es_index, preserve_order=has_sort)
    else:
        hits = scan(es, query=query, index=es_index, from_=from_, size=size, preserve_order=has_sort)
    graph = format_results(request, hits)

    # Support for request.embed() and `return_generator`
    if request.__parent__ is not None or return_generator:
        if return_generator:
            return graph
        else:
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
    types = request.params.getall('type')
    if len(types) != 1:
        msg = 'Report view requires specifying a single type.'
        raise HTTPBadRequest(explanation=msg)

    # Ignore large limits, which make `search` return a Response
    # -- UNLESS we're being embedded by the download_report view
    from_, size = get_pagination(request)
    if ('limit' in request.GET and request.__parent__ is None
            and (size is None or size > 1000)):
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
    # res['download_tsv'] = request.route_path('report_download') + search_base
    res['title'] = 'Report'
    res['@type'] = ['Report']
    return res
