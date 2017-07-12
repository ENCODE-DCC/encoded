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
from .visualization import vis_format_external_url



CHAR_COUNT = 32


def includeme(config):
    config.add_route('search', '/search{slash:/?}')
    config.add_route('report', '/report{slash:/?}')
    config.add_route('matrix', '/matrix{slash:/?}')
    config.add_route('news', '/news/')
    #ADDED START
    config.add_route('audit', '/audit/')
    #ADDED END
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
                # We don't currently traverse to other schemas for embedded
                # objects to find property titles. In this case we'll just
                # show the field's dotted path for now.
                limited_columns[field] = {'title': field}
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

    # Ensure that 'audit' field is requested with _source in the ES query
    if request.__parent__ and '/metadata/' in request.__parent__.url and request.has_permission('search_audit'):
        fields.add('audit.*')

    return fields


def build_terms_filter(field, terms):
    if field.endswith('!'):
        field = field[:-1]
        if not field.startswith('audit'):
            field = 'embedded.' + field + '.raw'
        # Setting not filter instead of terms filter
        if terms == ['*']:
            return {
                'missing': {
                    'field': field,
                }
            }
        else:
            return {
                'not': {
                    'terms': {
                        field: terms,
                    }
                }
            }
    else:
        if not field.startswith('audit'):
            field = 'embedded.' + field + '.raw'
        if terms == ['*']:
            return {
                'exists': {
                    'field': field,
                }
            }
        else:
            return {
                'terms': {
                    field: terms,
                },
            }

def set_filters(request, query, result, static_items=None):
    """
    Sets filters in the query
    """
    query_filters = query['filter']['and']['filters']
    used_filters = {}
    if static_items is None:
        static_items = []

    # Get query string items plus any static items, then extract all the fields
    qs_items = list(request.params.items())
    total_items = qs_items + static_items
    qs_fields = [item[0] for item in qs_items]
    fields = [item[0] for item in total_items]

    # Now make lists of terms indexed by field
    all_terms = {}
    for item in total_items:
        if item[0] in all_terms:
            all_terms[item[0]].append(item[1])
        else:
            all_terms[item[0]] = [item[1]]

    for field in fields:
        if field in used_filters:
            continue

        terms = all_terms[field]
        if field in ['type', 'limit', 'y.limit', 'x.limit', 'mode', 'annotation',
                     'format', 'frame', 'datastore', 'field', 'region', 'genome',
                     'sort', 'from', 'referrer']:
            continue

        # Add filter to result
        if field in qs_fields:
            for term in terms:
                qs = urlencode([
                    (k.encode('utf-8'), v.encode('utf-8'))
                    for k, v in qs_items
                    if '{}={}'.format(k, v) != '{}={}'.format(field, term)
                ])
                result['filters'].append({
                    'field': field,
                    'term': term,
                    'remove': '{}?{}'.format(request.path, qs)
                })

        if field == 'searchTerm':
            continue

        # Add to list of active filters
        used_filters[field] = terms

        # Add filter to query
        query_filters.append(build_terms_filter(field, terms))

    return used_filters


def build_aggregation(facet_name, facet_options, min_doc_count=0):
    """Specify an elasticsearch aggregation from schema facet configuration.
    """
    exclude = []
    if facet_name == 'type':
        field = 'embedded.@type.raw'
        exclude = ['Item']
    elif facet_name.startswith('audit'):
        field = facet_name
    else:
        field = 'embedded.' + facet_name + '.raw'
    agg_name = facet_name.replace('.', '-')

    facet_type = facet_options.get('type', 'terms')
    if facet_type == 'terms':
        agg = {
            'terms': {
                'field': field,
                'min_doc_count': min_doc_count,
                'size': 100,
            },
        }
        if exclude:
            agg['terms']['exclude'] = exclude
    elif facet_type == 'exists':
        agg = {
            'filters': {
                'filters': {
                    'yes': {'exists': {'field': field}},
                    'no': {'missing': {'field': field}},
                },
            },
        }
    else:
        raise ValueError('Unrecognized facet type {} for {} facet'.format(
            facet_type, field))

    return agg_name, agg


def set_facets(facets, used_filters, principals, doc_types):
    """
    Sets facets in the query using filters
    """
    aggs = {}
    for facet_name, facet_options in facets:
        # Filter facet results to only include
        # objects of the specified type(s) that the user can see
        filters = [
            {'terms': {'principals_allowed.view': principals}},
            {'terms': {'embedded.@type.raw': doc_types}},
        ]
        # Also apply any filters NOT from the same field as the facet
        for field, terms in used_filters.items():
            if field.endswith('!'):
                query_field = field[:-1]
            else:
                query_field = field

            # if an option was selected in this facet,
            # don't filter the facet to only include that option
            if query_field == facet_name:
                continue

            if not query_field.startswith('audit'):
                query_field = 'embedded.' + query_field + '.raw'

            if field.endswith('!'):
                if terms == ['*']:
                    filters.append({'missing': {'field': query_field}})
                else:
                    filters.append({'not': {'terms': {query_field: terms}}})
            else:
                if terms == ['*']:
                    filters.append({'exists': {'field': query_field}})
                else:
                    filters.append({'terms': {query_field: terms}})

        agg_name, agg = build_aggregation(facet_name, facet_options)
        aggs[agg_name] = {
            'aggs': {
                agg_name: agg
            },
            'filter': {
                'bool': {
                    'must': filters,
                },
            },
        }

    return aggs


def format_results(request, hits, result=None):
    """
    Loads results to pass onto UI
    """
    fields_requested = request.params.getall('field')
    if fields_requested:
        frame = 'embedded'
    else:
        frame = request.params.get('frame')

    # Request originating from metadata generation will skip to
    # partion of the code that adds audit  object to result items
    if request.__parent__ and '/metadata/' in request.__parent__.url:
        frame = ''

    any_released = False  # While formatting, figure out if any are released.

    if frame in ['embedded', 'object']:
        for hit in hits:
            if not any_released and hit['_source'][frame].get('status','released') == 'released':
                any_released = True
            yield hit['_source'][frame]
    else:
        # columns
        for hit in hits:
            item = hit['_source']['embedded']
            if not any_released and item.get('status','released') == 'released':
                any_released = True # Not exp? 'released' to do the least harm
            if 'audit' in hit['_source']:
                item['audit'] = hit['_source']['audit']
            if 'highlight' in hit:
                item['highlight'] = {}
                for key in hit['highlight']:
                    item['highlight'][key[9:]] = list(set(hit['highlight'][key]))
            yield item

    # After all are yielded, it may not be too late to change this result setting
    #if not any_released and result is not None and 'batch_hub' in result:
    #    del result['batch_hub']
    if not any_released and result is not None and 'visualize_batch' in result:
        del result['visualize_batch']


def search_result_actions(request, doc_types, es_results, position=None):
    actions = {}
    aggregations = es_results['aggregations']

    # generate batch hub URL for experiments
    # TODO we could enable them for Datasets as well here, but not sure how well it will work
    if doc_types == ['Experiment'] or doc_types == ['Annotation']:
        viz = {}
        for bucket in aggregations['assembly']['assembly']['buckets']:
            if bucket['doc_count'] > 0:
                assembly = bucket['key']
                if assembly in viz:  # mm10 and mm10-minimal resolve to the same thing
                    continue
                search_params = request.query_string.replace('&', ',,')
                if not request.params.getall('assembly') \
                or assembly in request.params.getall('assembly'):
                    # filter  assemblies that are not selected
                    hub_url = request.route_url('batch_hub',search_params=search_params,
                                                txt='hub.txt')
                    browser_urls = {}
                    pos = None
                    if 'region-search' in request.url and position is not None:
                        pos = position
                    ucsc_url = vis_format_external_url("ucsc", hub_url, assembly, pos)
                    if ucsc_url is not None:
                        browser_urls['UCSC'] = ucsc_url
                    ensembl_url = vis_format_external_url("ensembl", hub_url, assembly, pos)
                    if ensembl_url is not None:
                        browser_urls['Ensembl'] = ensembl_url
                    if browser_urls:
                        viz[assembly] = browser_urls
                        #actions.setdefault('visualize_batch', {})[assembly] = browser_urls  # formerly 'batch_hub'
        if viz:
            actions.setdefault('visualize_batch',viz)

    # generate batch download URL for experiments
    # TODO we could enable them for Datasets as well here, but not sure how well it will work
    # batch download disabled for region-search results
    if '/region-search/' not in request.url:
        #if (doc_types == ['Experiment'] or doc_types == ['Annotation']) and any(
        if (doc_types == ['Experiment']) and any(
                bucket['doc_count'] > 0
                for bucket in aggregations['files-file_type']['files-file_type']['buckets']):
            actions['batch_download'] = request.route_url(
                'batch_download',
                search_params=request.query_string
            )

    return actions


def format_facets(es_results, facets, used_filters, schemas, total, principals):
    result = []
    # Loading facets in to the results
    if 'aggregations' not in es_results:
        return result

    aggregations = es_results['aggregations']
    used_facets = set()
    exists_facets = set()
    for field, options in facets:
        used_facets.add(field)
        agg_name = field.replace('.', '-')
        if agg_name not in aggregations:
            continue
        terms = aggregations[agg_name][agg_name]['buckets']
        if len(terms) < 2:
            continue
        # internal_status exception. Only display for admin users
        if field == 'internal_status' and 'group.admin' not in principals:
            continue
        facet_type = options.get('type', 'terms')
        if facet_type == 'exists':
            terms = [
                {'key': 'yes', 'doc_count': terms['yes']['doc_count']},
                {'key': 'no', 'doc_count': terms['no']['doc_count']},
            ]
            exists_facets.add(field)
        result.append({
            'type': facet_type,
            'field': field,
            'title': options.get('title', field),
            'terms': terms,
            'total': aggregations[agg_name]['doc_count']
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


def iter_long_json(name, iterable, other):
    import json

    start = None

    # Note: by yielding @graph (iterable) first, then the contents of result (other) *may* be altered based upon @graph
    it = iter(iterable)
    try:
        first = next(it)
    except StopIteration:
        pass
    else:
        #yield json.dumps(first)
        start = '{' + json.dumps(name) + ':['
        yield start + json.dumps(first)
        for value in it:
            yield ',' + json.dumps(value)

    if start is None: # Nothing has bee yielded yet
        yield json.dumps(other)
    else:
        other_stuff = (',' + json.dumps(other)[1:-1]) if other else ''
        yield ']' + other_stuff + '}'

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
    res['download_tsv'] = request.route_path('report_download') + search_base
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

    principals = effective_principals(request)
    es = request.registry[ELASTIC_SEARCH]
    es_index = request.registry.settings['snovault.elasticsearch.index']

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

    # Setting filters.
    # Rather than setting them at the top level of the query
    # we collect them for use in aggregations later.
    query_filters = query.pop('filter')
    filter_collector = {'filter': query_filters}
    used_filters = set_filters(request, filter_collector, result)
    filters = filter_collector['filter']['and']['filters']

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
                "must": filters,
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
    es_index = request.registry.settings['snovault.elasticsearch.index']
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

    # Set sort order to sort by date_created.
    sort = OrderedDict()
    result_sort = OrderedDict()
    sort['embedded.date_created.raw'] = result_sort['date_created'] = {
        'order': 'desc',
        'ignore_unmapped': True,
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
    es_results = es.search(body=query, index=es_index, from_=0, size=25)
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

    matrix = result['matrix'] = type_info.factory.matrix.copy()
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
    es_index = request.registry.settings['snovault.elasticsearch.index']

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

    # Setting filters.
    # Rather than setting them at the top level of the query
    # we collect them for use in aggregations later.
    query_filters = query.pop('filter')
    filter_collector = {'filter': query_filters}
    used_filters = set_filters(request, filter_collector, result)
    filters = filter_collector['filter']['and']['filters']

    # Adding facets to the query
    facets = [(field, facet) for field, facet in schema['facets'].items() if
              field in matrix['x']['facets'] or field in matrix['y']['facets']]

    # Display all audits if logged in, or all but INTERNAL_ACTION if logged out
    for audit_facet in audit_facets:
        if search_audit and 'group.submitter' in principals or 'INTERNAL_ACTION' not in audit_facet[0]:
            facets.append(audit_facet)

    # To get list of audit categories from facets
    audit_list_label = []
    audit_list_field = []
    for item in facets:
        if item[0].rfind('audit.') > -1:
            audit_list_field.append(item)

    audit_list_label = audit_list_field.copy()

    # Gets just the labels from the tuples and converts it into format usable by summarize buckets
    for item in audit_list_label: # for each audit label
        temp = item[0] # copy string to modify
        audit_list_field[audit_list_field.index(item)] = temp
        index = temp.find('.') # find first index of .
        while index > 0: # if index exists
            temp = temp[:index] + '-' + temp[(index+1):] # replace . with -
            index = temp.find('.') # find repeat index of .
        audit_index = audit_list_label.index(item)
        audit_list_label[audit_index] = temp
        
    query['aggs'] = set_facets(facets, used_filters, principals, doc_types)

    # Group results in 2 dimensions
    # Don't use these groupings for audit matrix
    x_grouping = matrix['x']['group_by']
    y_groupings = audit_list_field
    x_agg = {
        "terms": {
            "field": 'embedded.' + x_grouping + '.raw',
            "size": 0,  # no limit
        },
    }
    aggs = {x_grouping: x_agg}
    
    for field in (y_groupings):
        aggs[field] = {
            "terms": {
                "field": audit_list_field[y_groupings.index(field)],
                "size": 0,  # no limit
            },
        }
    
    aggs = {'audit.ERROR.category': {'aggs': {'assay_title': {'terms': {'size': 0, 'field': 'embedded.assay_title.raw'
                        }
                    }
                },
            'terms': {'field': 'audit.ERROR.category', 'size': 0
        }
    }, 'audit.WARNING.category': {'aggs': {'assay_title': {'terms': {'size': 0, 'field': 'embedded.assay_title.raw'
                        }
                    }
                },
            'terms': {'field': 'audit.WARNING.category', 'size': 0
        }
    }, 'audit.NOT_COMPLIANT.category': {'aggs': {'assay_title': {'terms': {'size': 0, 'field': 'embedded.assay_title.raw'
                        }
                    }
                },
            'terms': {'field': 'audit.NOT_COMPLIANT.category', 'size': 0
        }
    }, 'audit.INTERNAL_ACTION.category': {'aggs': {'assay_title': {'terms': {'size': 0, 'field': 'embedded.assay_title.raw'
                        }
                    }
                },
            'terms': {'field': 'audit.INTERNAL_ACTION.category', 'size': 0
        }
    }
}
    aggs['x'] = x_agg
    query['aggs']['matrix'] = {
        "filter": {
            "bool": {
                "must": filters,
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

    # Create new dictionary that contains all the audit keys from aggregations and use that as 
    # y_bucket below
    temp_dict = {}
    for item in aggregations.items():
        if item[0].rfind('audit') > -1:
            temp_dict.update(item[1])
    
    # Format facets for results
    result['facets'] = format_facets(
        es_results, facets, used_filters, (schema,), total, principals)

    """

    def summarize_buckets(matrix, x_buckets, outer_bucket, grouping_fields):
        group_by = grouping_fields[0]
        #grouping_fields = grouping_fields[1:]
        if grouping_fields:
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

    summarize_buckets(
        result['matrix'],
        aggregations['matrix']['x']['buckets'],
        aggregations['matrix'],
        y_groupings + [x_grouping])

    result['matrix']['y'][y_groupings[0]] = aggregations['matrix'][y_groupings[0]]
    result['matrix']['x'].update(aggregations['matrix']['x'])    
    """
    def summarize_buckets(matrix, x_buckets, outer_bucket, grouping_fields):
        for category in grouping_fields:
            group_by = grouping_fields[0]
            grouping_fields = grouping_fields[1:]
            if grouping_fields:
                counts = {}
                for bucket in outer_bucket[category]['buckets']:
                    for assay in bucket['assay_title']['buckets']:
                        doc_count = assay['doc_count']
                        if doc_count > matrix['max_cell_doc_count']:
                            matrix['max_cell_doc_count'] = doc_count
                        if 'key' in assay:
                            counts[assay['key']] = doc_count
                        else:
                            for col in assay:
                                assay_index = 0
                                counts[bucket[assay_index]['key']] = doc_count
                                assay_index += 1
                    summary = []
                    for xbucket in x_buckets:
                        summary.append(counts.get(xbucket['key'], 0))
                    bucket['assay_title'] = summary
                   #counts[bucket['key']] = doc_count
                    """
                    counts_string = str(bucket['assay_title']['buckets'])
                    temp = counts_string
                    index = counts_string.find('[') # find first index of .
                    temp = temp[:index] + temp[(index+1):] # take out [
                    index = temp.find(']') # find end brace index of
                    temp = temp[:index] + temp[(index+1):]
                    bucket_dict = {}
                    import ast
                    bucket_dict = ast.literal_eval(temp)
                    """
                    #find index of both []
                    #substring out both []
                    #convert string to dict
                    
                 

    summarize_buckets(
        result['matrix'],
        aggregations['matrix']['x']['buckets'],
        aggregations['matrix'],
        y_groupings + [x_grouping])
    #result['matrix']['y'][y_groupings[0]] = aggregations['matrix'][y_groupings[0]]
    # Reformats matrix categories to ones applicable to audits

    #result['matrix']['y']['audit_category'] = temp_dict
    result['matrix']['y']['label'] = "Audit Category"
    result['matrix']['y']['group_by'][0] = "audit_category"
    result['matrix']['y']['group_by'][1] = "audit_label"
    bucket_audit_category_list = []
    for audit in aggregations['matrix']:
        if "audit" in audit:
            audit_category_dict = {}
            audit_category_dict['audit_label'] = aggregations['matrix'][audit]
            audit_category_dict['key'] = audit
            bucket_audit_category_list.append(audit_category_dict)
    """
    audit_category_dict = {}
    audit_category_dict['audit-ERROR-category'] = aggregations['matrix']['audit-ERROR-category']
    audit_category_dict['audit-WARNING-category'] = aggregations['matrix']['audit-WARNING-category']
    audit_category_dict['audit-NOT_COMPLIANT-category'] = aggregations['matrix']['audit-NOT_COMPLIANT-category']
    """
    bucket_audit_category_dict = {}
    bucket_audit_category_dict['buckets'] = bucket_audit_category_list
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