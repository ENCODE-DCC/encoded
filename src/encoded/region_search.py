from pyramid.view import view_config
from encoded.vis_defines import vis_format_url
from snovault import TYPES
from snovault.elasticsearch.interfaces import ELASTIC_SEARCH
from snovault.elasticsearch.indexer import MAX_CLAUSES_FOR_ES
from collections import OrderedDict
import requests
from urllib.parse import urlencode

from encoded.genomic_data_service import GenomicDataService

import logging
import re


log = logging.getLogger(__name__)


_FACETS = [
    ('assay_term_name', {'title': 'Assay'}),
    ('biosample_ontology.term_name', {'title': 'Biosample term'}),
    ('target.label', {'title': 'Target'}),
    ('biosample_ontology.organ_slims', {'title': 'Organ'}),
    ('biosample_ontology.cell_slims', {'title': 'Cell'}),
    ('assembly', {'title': 'Genome assembly'}) # necessary for aggregating data
]

_REMOVE_FACETS = [
    'Genome assembly',
    'assembly',
    'files.uuid'
]

_GENOME_TO_SPECIES = {
    'GRCh37': 'homo_sapiens',
    'GRCh38': 'homo_sapiens',
    'GRCm37': 'mus_musculus',
    'GRCm38': 'mus_musculus',
    'mm10'  : 'mus_musculus'
}

_GENOME_TO_ALIAS = {
    'GRCh37': 'hg19',
    'GRCh38': 'GRCh38',
    'GRCm37': 'mm9',
    'GRCm38': 'mm10',
    'mm10'  : 'mm10'
}

FORMATS_GBROWSER = [
    'bigBed',
    'bigWig'
]

GBROWSER_EMBEDDED_FIELDS = [
    'annotation_subtype',
    'annotation_type',
    'assay_term_name',
    'assembly',
    'biochemical_inputs',
    'biological_replicates',
    'biosample_ontology.term_name',
    'dataset',
    'dataset',
    'file_format',
    'file_format_type',
    'file_type',
    'href',
    'output_type',
    'path',
    'simple_biosample_summary',
    'status',
    'target.label',
    'targets',
    'title'
]


def includeme(config):
    config.add_route('region-search', '/region-search{slash:/?}')
    config.add_route('suggest', '/suggest{slash:/?}')
    config.scan(__name__)


def get_bool_query(start, end):
    must_clause = {
        'bool': {
            'must': [
                {
                    'range': {
                        'positions.start': {
                            'lte': start,
                        }
                    }
                },
                {
                    'range': {
                        'positions.end': {
                            'gte': end,
                        }
                    }
                }
            ]
        }
    }
    return must_clause


def get_peak_query(start, end, with_inner_hits=False, within_peaks=False):
    """
    return peak query
    """
    query = {
        'query': {
            'bool': {
                'filter': {
                    'nested': {
                        'path': 'positions',
                        'query': {
                            'bool': {
                                'should': []
                            }
                        }
                    }
                }
             }
         },
        '_source': False,
    }
    search_ranges = {
        'peaks_inside_range': {
            'start': start,
            'end': end
        },
        'range_inside_peaks': {
            'start': end,
            'end': start
        },
        'peaks_overlap_start_range': {
            'start': start,
            'end': start
        },
        'peaks_overlap_end_range': {
            'start': end,
            'end': end
        }
    }
    for key, value in search_ranges.items():
        query['query']['bool']['filter']['nested']['query']['bool']['should'].append(get_bool_query(value['start'], value['end']))
    if with_inner_hits:
        query['query']['bool']['filter']['nested']['inner_hits'] = {'size': 99999}
    return query


def get_suggested_coordinates(request, query, assembly):
    coordinates, start, end = '', '' , ''

    search_params = '&'.join([
        'type=Gene',
        'field=locations',
        'field=title',
        f'searchTerm={query}',
        f'locations.assembly={assembly}'
    ])

    suggestions = request.embed(f'/search/?{search_params}')

    for suggestion in suggestions['@graph']:
        if suggestion['title'].split(' ')[0].lower() == query.lower():
            for coordinates in suggestion['locations']:
                if coordinates['assembly'] == assembly:
                    return (coordinates['chromosome'], coordinates['start'], coordinates['end'])

    return (coordinates, start, end)


@view_config(route_name='region-search', request_method='GET', permission='search')
def region_search(context, request):
    """
    Search files by region.
    """

    data_service = GenomicDataService(context.registry, request)

    principals = request.effective_principals
    es         = request.registry[ELASTIC_SEARCH]
    snp_es     = request.registry['snp_search']
    types      = request.registry[TYPES]

    region     = request.params.get('region', '')
    annotation = request.params.get('annotation', '')
    assembly   = request.params.get('genome', '')
    size       = request.params.get('limit', 25)
    try:
        size = 99999 if size in ('all', '') else int(size)
    except ValueError:
        size = 25

    result = {
        '@id': '/region-search/' + ('?' + request.query_string.split('&referrer')[0] if request.query_string else ''),
        '@type': ['region-search'],
        'title': 'Search by region',
        'facets': [],
        '@graph': [],
        'columns': OrderedDict(),
        'notification': '',
        'filters': [],
        'assembly': _GENOME_TO_ALIAS.get(assembly,'GRCh38')
    }

    query = annotation or region

    if not query:
        result['notification'] = 'Try for example: chr8:79263597-79294735, or CTCF, or rs75982468, etc.'
        return result

    expand = True
    if region and (re.match('chr\d+:\d+-\d+', region) or re.match('rs\d+', region)):
        expand = False

    try:
        peak_results = data_service.region_search(
            _GENOME_TO_ALIAS[assembly],
            query=query,
            expand_kb=2 if expand else 0
        )
    except Exception:
        result['notification'] = 'Error during search'
        return result

    chromosome = peak_results['chr']
    start      = peak_results['start']
    end        = peak_results['end']
    file_uuids = [f['uuid'] for f in peak_results['regions_per_file']]

    if not chromosome or not start or not end:
        chromosome, start, end = get_suggested_coordinates(request, query, assembly)

        if chromosome and start and end:
            try:
                peak_results = data_service.region_search(
                    _GENOME_TO_ALIAS[assembly],
                    chrom=chromosome,
                    start=start,
                    end=end,
                    expand_kb=2 if expand else 0
                )
            except Exception:
                result['notification'] = 'Error during search'
                return result

            file_uuids = [f['uuid'] for f in peak_results['regions_per_file']]

        if not chromosome or not start or not end:
            result['notification'] = 'No annotations found'
            return result

    if not file_uuids:
        result['notification'] = 'No results found'
        return result

    result['coordinates'] = '{chr}:{start}-{end}'.format(chr=chromosome, start=start, end=end)
    result['coordinates_msg'] = result['coordinates']

    if expand:
        result['coordinates_msg'] = '{label}: ({coords}) +/- 2kb'.format(label=(region or annotation), coords=result['coordinates'])
        result['coordinates'] = '{chr}:{start}-{end}'.format(
            chr=chromosome, start=int(start) - 2000, end=int(end) + 2000
        )

    # if more than one peak found return the experiments with those peak files
    uuid_count = len(file_uuids)
    if uuid_count > MAX_CLAUSES_FOR_ES:
        log.error("REGION_SEARCH WARNING: region with %d file_uuids is being restricted to %d" % \
                                                            (uuid_count, MAX_CLAUSES_FOR_ES))
        file_uuids = file_uuids[:MAX_CLAUSES_FOR_ES]
        uuid_count = len(file_uuids)

    query = get_filtered_query('', [], set(), principals, ['Experiment'])
    del query['query']
    query['post_filter']['bool']['must'].append({
        'terms': {
            'embedded.files.uuid': file_uuids
        }
    })
    used_filters = set_filters(request, query, result)
    used_filters['files.uuid'] = file_uuids
    query['aggs'] = set_facets(_FACETS, used_filters, principals, ['Experiment'])
    schemas = (types[item_type].schema for item_type in ['Experiment'])

    es_results = es.search(body=query, index='experiment', doc_type='experiment', size=size, request_timeout=60)

    result['@graph'] = list(format_results(request, es_results['hits']['hits']))
    result['gbrowser'] = genome_browser_files(es, principals, result['@graph'])
    result['total'] = total = es_results['hits']['total']
    result['facets'] = format_facets(es_results, _FACETS, used_filters, schemas, total, principals)
    if result['total'] > 0:
        result['notification'] = 'Success'

    return result


@view_config(route_name='suggest', request_method='GET', permission='search')
def suggest(context, request):
    text = ''
    requested_genome = ''
    if 'q' in request.params:
        text = request.params.get('q', '')
        requested_genome = request.params.get('genome', '')

    result = {
        '@id': '/suggest/?' + urlencode({'genome': requested_genome, 'q': text}, ['q', 'genome']),
        '@type': ['suggest'],
        'title': 'Suggest',
        '@graph': [],
    }
    es = request.registry[ELASTIC_SEARCH]

    query = {
        "suggest": {
            "default-suggest": {
                "text": text,
                "completion": {
                    "field": "suggest",
                    "size": 100
                }
            }
        }
    }
    try:
        results = es.search(index='annotations', body=query)
    except:
        return result
    else:
        result['@id'] = '/suggest/?' + urlencode({'genome': requested_genome, 'q': text}, ['q','genome'])
        result['@graph'] = []
        for item in results['suggest']['default-suggest'][0]['options']:
            if _GENOME_TO_SPECIES[requested_genome].replace('_', ' ') == item['_source']['payload']['species']:
                result['@graph'].append(item)
        result['@graph'] = result['@graph'][:10]
        return result


def genome_browser_files(es, principals, graph):
    uuids = []

    for experiment in graph:
        for f in experiment['files']:
            if 'preferred_default' in f and f['file_format'] in FORMATS_GBROWSER:
                uuids.append(f['uuid'])

    query = get_filtered_query('', [], set(), principals, ['File'])
    del query['query']

    query['_source'] = [f"embedded.{field}" for field in GBROWSER_EMBEDDED_FIELDS]
    query['post_filter']['bool']['must'].append({
        'terms': {
            'uuid': list(set(uuids))
        }
    })

    es_results = es.search(body=query, index='file', size=9999, request_timeout=60)

    return [result['_source']['embedded'] for result in es_results['hits']['hits']]


def format_facets(
        es_results,
        facets,
        used_filters,
        schemas,
        total,
        principals
):
    result = []
    if 'aggregations' not in es_results:
        return result
    aggregations = es_results['aggregations']
    used_facets = set()
    exists_facets = set()
    for field, options in facets:
        if options.get('title', field) in _REMOVE_FACETS:
            continue

        used_facets.add(field)
        agg_name = field.replace('.', '-')
        if agg_name not in aggregations:
            continue
        all_buckets_total = aggregations[agg_name]['doc_count']
        if not all_buckets_total > 0:
            continue
        # internal_status exception. Only display for admin users
        if field == 'internal_status' and 'group.admin' not in principals:
            continue
        facet_type = options.get('type', 'terms')
        terms = aggregations[agg_name][agg_name]['buckets']
        if facet_type == 'exists':
            terms = [
                {'key': 'yes', 'doc_count': terms['yes']['doc_count']},
                {'key': 'no', 'doc_count': terms['no']['doc_count']},
            ]
            exists_facets.add(field)
        result.append(
            {
                'type': facet_type,
                'field': field,
                'title': options.get('title', field),
                'terms': terms,
                'appended': False,
                'total': all_buckets_total
            }
        )
    for field, values in used_filters.items():
        field_without_bang = field.rstrip('!')
        if field_without_bang not in used_facets and field_without_bang not in exists_facets:
            title = field_without_bang

            if title in _REMOVE_FACETS:
                continue

            for schema in schemas:
                if field in schema['properties']:
                    title = schema['properties'][field].get('title', field)
                    break
            item = [r for r in result if r['field'] == field_without_bang]
            terms = [{'key': v, 'isEqual': True if field[-1] != '!' else False} for v in values]
            if item:
                item[0]['terms'].extend(terms)
            else:
                result.append({
                    'field': field_without_bang,
                    'title': title,
                    'terms': terms,
                    'appended': True,
                    'total': total,
                })
    return result


def get_filtered_query(term, search_fields, result_fields, principals, doc_types):
    return {
        'query': {
            'query_string': {
                'query': term,
                'fields': search_fields,
                'default_operator': 'AND'
            }
        },
        'post_filter': {
            'bool': {
                'must': [
                    {
                        'terms': {
                            'principals_allowed.view': principals
                        }
                    },
                    {
                        'terms': {
                            'embedded.@type': doc_types
                        }
                    }
                ],
                'must_not': []
            }
        },
        '_source': list(result_fields),
    }


def build_terms_filter(query_filters, field, terms):
    if field.endswith('!'):
        field = field[:-1]
        if not field.startswith('audit'):
            field = 'embedded.' + field
        # Setting not filter instead of terms filter
        if terms == ['*']:
            negative_filter_condition = {
                'exists': {
                    'field': field,
                }
            }
        else:
            negative_filter_condition = {
                'terms': {
                    field: terms
                }
            }
        query_filters['must_not'].append(negative_filter_condition)
    else:
        if not field.startswith('audit'):
            field = 'embedded.' + field
        if terms == ['*']:
            filter_condition = {
                'exists': {
                    'field': field,
                }
            }
        else:
            filter_condition = {
                'terms': {
                    field: terms,
                },
            }
        query_filters['must'].append(filter_condition)


def set_filters(request, query, result, static_items=None, filter_exclusion=None):
    """
    Sets filters in the query
    """
    default_filter_exclusion = [
        'type', 'limit', 'mode', 'annotation', 'format', 'frame', 'datastore',
        'field', 'region', 'genome', 'sort', 'from', 'referrer', 'filterresponse',
        'remove', 'cart',
    ]
    query_filters = query['post_filter']['bool']
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
        if field in (filter_exclusion or default_filter_exclusion):
            continue

        # Add filter to result
        filterresponse = request.params.get('filterresponse', 'on')
        if field in qs_fields and filterresponse == 'on':
            for term in terms:
                query_string = urlencode([
                    (k.encode('utf-8'), v.encode('utf-8'))
                    for k, v in qs_items
                    if '{}={}'.format(k, v) != '{}={}'.format(field, term)
                ])
                result['filters'].append({
                    'field': field,
                    'term': term,
                    'remove': '{}?{}'.format(request.path, query_string)
                })

        if field in ('searchTerm', 'advancedQuery'):
            continue

        # Add to list of active filters
        used_filters[field] = terms

        # Add filter to query
        build_terms_filter(query_filters, field, terms)

    return used_filters


def build_aggregation(facet_name, facet_options, min_doc_count=0):
    """Specify an elasticsearch aggregation from schema facet configuration.
    """
    exclude = []
    if facet_name == 'type':
        field = 'embedded.@type'
        exclude = ['Item']
    elif facet_name.startswith('audit'):
        field = facet_name
    else:
        field = 'embedded.' + facet_name
    agg_name = facet_name.replace('.', '-')

    facet_type = facet_options.get('type', 'terms')
    facet_length = 200
    if facet_options.get('length') == 'long':
        facet_length = 3000
    if facet_type in ['terms', 'typeahead']:
        agg = {
            'terms': {
                'field': field,
                'min_doc_count': min_doc_count,
                'size': facet_length,
            },
        }
        if exclude:
            agg['terms']['exclude'] = exclude
    elif facet_type == 'exists':
        agg = {
            'filters': {
                'filters': {
                    'yes': {
                        'bool': {
                            'must': {
                                'exists': {'field': field}
                            }
                        }
                    },
                    'no': {
                        'bool': {
                            'must_not': {
                                'exists': {'field': field}
                            }
                        }
                    },
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
            {'terms': {'embedded.@type': doc_types}},
        ]
        negative_filters = []
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
                query_field = 'embedded.' + query_field

            if field.endswith('!'):
                if terms == ['*']:
                    negative_filters.append({'exists': {'field': query_field}})
                else:
                    negative_filters.append({'terms': {query_field: terms}})
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
                    'must_not': negative_filters
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
            if not any_released and hit['_source'][frame].get('status', 'released') == 'released':
                any_released = True
            yield hit['_source'][frame]
    else:
        # columns
        for hit in hits:
            item = hit['_source']['embedded']
            if not any_released and item.get('status', 'released') == 'released':
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
    BATCH_DOWNLOAD_DOC_TYPES = [
        ['Experiment'],
        ['Annotation'],
    ]
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
                    hub_url = request.route_url('batch_hub', search_params=search_params,
                                                txt='hub.txt')
                    browser_urls = {}
                    pos = None
                    if 'region-search' in request.url and position is not None:
                        pos = position
                    ucsc_url = vis_format_url("ucsc", hub_url, assembly, pos)
                    if ucsc_url is not None:
                        browser_urls['UCSC'] = ucsc_url
                    ensembl_url = vis_format_url("ensembl", hub_url, assembly, pos)
                    if ensembl_url is not None:
                        browser_urls['Ensembl'] = ensembl_url
                    if browser_urls:
                        viz[assembly] = browser_urls
                        #actions.setdefault('visualize_batch', {})[assembly] =\
                                #browser_urls  # formerly 'batch_hub'
        if viz:
            actions.setdefault('visualize_batch', viz)

    # generate batch download URL for experiments and annotation
    # batch download disabled for region-search results
    # TODO: Can potentially be enabled for dataset...
    bucket_has_doc = any(
        bucket['doc_count'] > 0
        for bucket in aggregations.get('files-file_type', {}).get('files-file_type', {}).get('buckets', {})
    )
    if ('/region-search/' not in request.url and
            doc_types in BATCH_DOWNLOAD_DOC_TYPES and
            bucket_has_doc):
        actions['batch_download'] = request.route_url(
            'batch_download',
            search_params='?' + request.query_string
        )
    return actions
