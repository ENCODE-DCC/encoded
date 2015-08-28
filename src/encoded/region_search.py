from pyramid.view import view_config
from contentbase.elasticsearch import ELASTIC_SEARCH
from pyramid.security import effective_principals
from .search import (
    load_columns,
    load_results,
    set_filters,
    set_facets,
    get_filtered_query,
    load_facets
)
from collections import OrderedDict

_ASSEMBLY_MAPPER = {
    'GRCh38': 'hg20',
    'GRCh37': 'hg19',
    'GRCm38': 'mm10',
    'GRCm37': 'mm9',
    'BDGP6': 'dm4',
    'BDGP5': 'dm3',
    'WBcel235': 'WBcel235'
}

_REGION_FIELDS = [
    'embedded.files.uuid',
    'embedded.files.accession',
    'embedded.files.href',
    'embedded.files.file_format',
    'embedded.files.assembly',
    'embedded.files.output_type',
    'embedded.files.derived_from.uuid'
]

_FACETS = [
    ('assay_term_name', {'title': 'Assay'}),
    ('biosample_term_name', {'title': 'Biosample term'}),
    ('target.label', {'title': 'Target'}),
    ('Organism', {'title': 'replicates.library.biosample.donor.organism.scientific_name'})
]


def includeme(config):
    config.add_route('region-search', '/region-search{slash:/?}')
    config.add_route('suggest', '/suggest{slash:/?}')
    config.scan(__name__)


def get_peak_query(start, end):
    """
    return peak query
    """
    return {
        'query': {
            'filtered': {
                'filter': {
                    'nested': {
                        'path': 'positions',
                        'filter': {
                            'bool': {
                                'must': [
                                    {
                                        'range': {
                                            'positions.start': {
                                                'lte': end,
                                            }
                                        }
                                    },
                                    {
                                        'range': {
                                            'positions.end': {
                                                'gte': start,
                                            }
                                        }
                                    }
                                ]
                            }
                        }
                    }
                },
                '_cache': True,
            }
        }
    }


@view_config(route_name='region-search', request_method='GET', permission='search')
def region_search(context, request):
    """
    Search files by region.
    """
    result = {
        '@id': '/region-search/' + ('?' + request.query_string if request.query_string else ''),
        '@type': ['region-search'],
        'title': 'Search by region',
        'facets': [],
        '@graph': [],
        'columns': OrderedDict(),
        'notification': '',
        'filters': []
    }
    principals = effective_principals(request)
    es = request.registry[ELASTIC_SEARCH]
    term = request.params.get('region', '*')
    annotation = request.params.get('annotation', '*')
    assembly = request.params.get('assembly', '*')
    if assembly == '*':
        assembly = 'hg19'
    if term != '*' and assembly != '*':
        terms = term.split(':')
        if len(terms) < 2:
            result['notification'] = 'Please enter valid coordinates'
            return result
        chromosome = terms[0]
        positions = terms[1].split('-')
        if len(positions) > 0 and len(positions) == 1:
            start = end = positions[0]
        elif len(positions) == 2:
            start = positions[0]
            end = positions[1]
        try:
            peak_results = es.search(body=get_peak_query(start, end), index=chromosome,
                                     doc_type=assembly, size=99999)
        except Exception as e:
            result['notification'] = 'Please enter valid coordinates'
            return result
        file_uuids = []
        for hit in peak_results['hits']['hits']:
            if hit['_id']not in file_uuids:
                file_uuids.append(hit['_id'])
        file_uuids = list(set(file_uuids))
        result_fields = load_columns(request, ['experiment'], result)
        result_fields = result_fields.union(_REGION_FIELDS)
        result['notification'] = 'No results found'
        if len(file_uuids):
            query = get_filtered_query('', [], result_fields, principals)
            del query['query']
            query['filter']['and']['filters'].append({
                'terms': {
                    'embedded.files.uuid': file_uuids
                }
            })
            used_filters = set_filters(request, query, result)
            used_filters['files.uuid'] = file_uuids
            set_facets(_FACETS, used_filters, query, principals)
            es_results = es.search(
                body=query,
                index='encoded', doc_type='experiment', size=10
            )
            load_results(request, es_results, result)
            load_facets(es_results, _FACETS, result)
            if len(result['@graph']):
                new_results = []
                for item in result['@graph']:
                    item['highlight'] = []
                    new_files = []
                    for f in item['files']:
                        if 'file_format' in f and f['file_format'] == 'bigBed':
                            new_files.append(f)
                        if 'derived_from' in f:
                            derived_files = []
                            for derived_file in f['derived_from']:
                                if derived_file['uuid'] in file_uuids:
                                    derived_files.append(derived_file)
                                    item['highlight'].append(derived_file['uuid'])
                            if len(derived_files):
                                f['derived_from'] = derived_files
                                new_files.append(f)
                    item['files'] = new_files
                    if len(item['files']) > 0:
                        new_results.append(item)
                if len(new_results) > 0:
                    result['total'] = es_results['hits']['total']
                    result['notification'] = 'Success'
                result['@graph'] = new_results
    elif annotation != '*':
        # got to handle gene names, IDs and other annotations here
        result['notification'] = 'Annotations are not yet handled'
    else:
        result['notification'] = 'Please enter valid coordinates'
    return result


@view_config(route_name='suggest', request_method='GET', permission='search')
def suggest(context, request):
    text = ''
    result = {
        '@id': '/suggest/' + ('?q=' + text),
        '@type': ['suggest'],
        'title': 'Suggest',
        '@graph': [],
    }
    if 'q' in request.params:
        text = request.params.get('q', '')
    else:
        return []
    es = request.registry[ELASTIC_SEARCH]
    query = {
        "suggester": {
            "text": text,
            "completion": {
                "field": "name_suggest",
                "size": 10
            }
        }
    }
    try:
        results = es.suggest(index='annotations', body=query)
    except:
        return {}
    else:
        result['@id'] = '/suggest/' + ('?q=' + text)
        result['@graph'] = results['suggester'][0]['options']
        return result
