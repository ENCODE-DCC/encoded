from pyramid.view import view_config
from snowfort.elasticsearch.interfaces import (
    ELASTIC_SEARCH,
    SNP_SEARCH_ES,
)
from pyramid.security import effective_principals
from .search import (
    format_results,
    set_filters,
    set_facets,
    get_filtered_query,
    format_facets,
    hgConnect
)
from collections import OrderedDict
import requests
from urllib.parse import urlencode

import logging


log = logging.getLogger(__name__)


_ENSEMBL_URL = 'http://rest.ensembl.org/'

_ASSEMBLY_MAPPER = {
    'GRCh38': 'hg38',
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
    'embedded.files.derived_from'
]

_FACETS = [
    ('assay_term_name', {'title': 'Assay'}),
    ('biosample_term_name', {'title': 'Biosample term'}),
    ('target.label', {'title': 'Target'}),
    ('replicates.library.biosample.donor.organism.scientific_name', {
        'title': 'Organism'
    }),
    ('organ_slims', {'title': 'Organ'}),
    ('assembly', {'title': 'Genome assembly'})
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


def sanitize_coordinates(term):
    ''' Sanitize the input string and return coordinates '''

    if term.count(':') != 1 or term.count('-') > 1:
        return ('', '', '')
    terms = term.split(':')
    chromosome = terms[0]
    positions = terms[1].split('-')
    if len(positions) == 1:
        start = end = positions[0].replace(',', '')
    elif len(positions) == 2:
        start = positions[0].replace(',', '')
        end = positions[1].replace(',', '')
    if start.isdigit() and end.isdigit():
        return (chromosome, start, end)
    return ('', '', '')


def get_annotation_coordinates(es, id, assembly):
    ''' Gets annotation coordinates from annotation index in ES '''

    chromosome, start, end = '', '', ''
    try:
        es_results = es.get(index='annotations', doc_type='default', id=id)
    except:
        return (chromosome, start, end)
    else:
        annotations = es_results['_source']['annotations']
        for annotation in annotations:
            if annotation['assembly_name'] == assembly:
                return ('chr' + annotation['chromosome'],
                        annotation['start'],
                        annotation['end'])
            else:
                location = '{chr}:{start}-{end}'.format(
                    chr=annotation['chromosome'],
                    start=annotation['start'],
                    end=annotation['end']
                )
        return assembly_mapper(location, species,
                               annotations[0]['assembly_name'], assembly)


def assembly_mapper(location, species, input_assembly, output_assembly):
    # All others
    new_url = _ENSEMBL_URL + 'map/' + species + '/' \
        + input_assembly + '/' + location + '/' + output_assembly \
        + '/?content-type=application/json'
    try:
        new_response = requests.get(new_url).json()
    except:
        return('', '', '')
    else:
        if not len(new_response['mappings']):
            return('', '', '')
        data = new_response['mappings'][0]['mapped']
        chromosome = 'chr' + data['seq_region_name']
        start = data['start']
        end = data['end']
        return(chromosome, start, end)


def get_rsid_coordinates(id):
    url = '{ensembl}variation/human/{id}?content-type=application/json'.format(
        ensembl=_ENSEMBL_URL,
        id=id
    )
    try:
        response = requests.get(url).json()
    except:
        return('', '', '')
    else:
        if 'mappings' not in response:
            return('', '', '')
        for mapping in response['mappings']:
            if mapping['assembly_name'] == 'GRCh38':
                location = mapping['location']
        return assembly_mapper(location, 'human', 'GRCh38', 'GRCh37')


def get_ensemblid_coordinates(id):
    url = '{ensembl}lookup/id/{id}?content-type=application/json'.format(
        ensembl=_ENSEMBL_URL,
        id=id
    )
    try:
        response = requests.get(url).json()
    except:
        return('', '', '')
    else:
        if response['assembly_name'] == 'GRCh38':
            location = '{chr}:{start}-{end}'.format(
                chr=response['seq_region_name'],
                start=response['start'],
                end=response['end']
            )
        else:
            return('', '', '')
        return assembly_mapper(location, 'human', 'GRCh38', 'GRCh37')


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
    snp_es = request.registry[SNP_SEARCH_ES]
    region = request.params.get('region', '*')

    # handling limit
    size = request.params.get('limit', 25)
    if size in ('all', ''):
        size = 99999
    else:
        try:
            size = int(size)
        except ValueError:
            size = 25
    if region == '':
        region = '*'

    assembly = request.params.get('genome', '*')
    reference = ''
    for regular_name, ucsc_name in _ASSEMBLY_MAPPER.items():
        if ucsc_name == assembly:
            reference = regular_name
    annotation = request.params.get('annotation', '*')
    if annotation != '*':
        chromosome, start, end = get_annotation_coordinates(es, annotation, reference)
    elif region != '*':
        region = region.lower()
        if region.startswith('rs'):
            chromosome, start, end = get_rsid_coordinates(region)
        elif region.startswith('ens'):
            chromosome, start, end = get_ensemblid_coordinates(region)
        elif region.startswith('chr'):
            chromosome, start, end = sanitize_coordinates(region)
        else:
            result['notification'] = 'Please select valid annotation or enter coordinates'
            return result
    else:
        result['notification'] = 'Please enter valid coordinates'
        return result

    # Check if there are valid coordinates
    if chromosome == '' or start == '' or end == '':
        result['notification'] = 'No annotations found'
        return result
    else:
        result['coordinates'] = '{chr}:{start}-{end}'.format(
            chr=chromosome, start=start, end=end
        )

    # Search for peaks for the coordinates we got
    try:
        peak_results = snp_es.search(body=get_peak_query(start, end),
                                     index=chromosome.lower(),
                                     doc_type=assembly,
                                     size=99999)
    except Exception:
        result['notification'] = 'Please enter valid coordinates'
        return result
    file_uuids = []
    for hit in peak_results['hits']['hits']:
        if hit['_id'] not in file_uuids:
            file_uuids.append(hit['_id'])
    file_uuids = list(set(file_uuids))
    result['notification'] = 'No results found'


    # if more than one peak found return the experiments with those peak files
    if len(file_uuids):
        query = get_filtered_query('', [], set(), principals, ['Item'])
        del query['query']
        query['filter']['and']['filters'].append({
            'terms': {
                'embedded.files.uuid': file_uuids
            }
        })
        used_filters = set_filters(request, query, result)
        used_filters['files.uuid'] = file_uuids
        query['aggs'] = set_facets(_FACETS, used_filters, principals, ['Item'])
        es_results = es.search(
            body=query, index='encoded', doc_type='experiment', size=size
        )

        result['@graph'] = list(format_results(request, es_results['hits']['hits']))
        result['facets'] = format_facets(es_results, _FACETS)
        if len(result['@graph']):
            result['notification'] = 'Success'
            result['total'] = es_results['hits']['total']
            search_params = request.query_string.replace('&', ',,')
            hub = request.route_url('batch_hub',
                                    search_params=search_params,
                                    txt='hub.txt')
            result['batch_hub'] = hgConnect + hub
    return result


@view_config(route_name='suggest', request_method='GET', permission='search')
def suggest(context, request):
    text = ''
    result = {
        '@id': '/suggest/?' + urlencode({'q': text}),
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
        result['@id'] = '/suggest/?' + urlencode({'q': text})
        result['@graph'] = []
        for item in results['suggester'][0]['options']:
            if not any(x in item['text'] for x in ['(C. elegans)','(mus musculus)','(D. melanogaster)']):
                result['@graph'].append(item)


        # result['@graph'] = [x for x in results['suggester'][0]['options'] if x['text'] not in []]
        return result
