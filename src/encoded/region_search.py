from pyramid.view import view_config
from snovault import TYPES
from snovault.elasticsearch.interfaces import ELASTIC_SEARCH
from snovault.elasticsearch.indexer import MAX_CLAUSES_FOR_ES
from pyramid.security import effective_principals
from .search import (
    format_results,
    set_filters,
    set_facets,
    get_filtered_query,
    format_facets,
    search_result_actions
)
from .batch_download import get_peak_metadata_links
from .region_indexer import (
    RESIDENT_REGIONSET_KEY,
    FOR_REGION_SEARCH,
    FOR_REGULOME_DB
)
from collections import OrderedDict
import requests
from urllib.parse import urlencode

import logging
import re


log = logging.getLogger(__name__)


_ENSEMBL_URL = 'http://rest.ensembl.org/'
_ENSEMBL_URL_GRCH37 = 'http://grch37.rest.ensembl.org/'

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
    ('assembly', {'title': 'Genome assembly'}),
    ('files.file_type', {'title': 'Available data'})
]

_GENOME_TO_SPECIES = {
    'GRCh37': 'homo_sapiens',
    'GRCh38': 'homo_sapiens',
    'GRCm37': 'mus_musculus',
    'GRCm38': 'mus_musculus'
}

_GENOME_TO_ALIAS = {
    'GRCh37': 'hg19',
    'GRCh38': 'GRCh38',
    'GRCm37': 'mm9',
    'GRCm38': 'mm10'
}


def includeme(config):
    config.add_route('region-search', '/region-search{slash:/?}')
    config.add_route('regulome-search', '/regulome-search{slash:/?}')
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


def region_get_hits(region_es, assembly, chrom, start, end, peaks_too=False, with_inner_hits=False, uses=[]):
    '''Returns a list of file uuids AND dataset paths for chromosome location'''

    all_hits = {}  #{ 'dataset_paths': [], 'file_hits': {}, 'peaks': [], 'message': ''}

    region_query = get_peak_query(start, end, with_inner_hits=with_inner_hits, within_peaks=peaks_too)

    try:
        results = region_es.search(body=region_query,
                                            index=chrom.lower(),
                                            doc_type=_GENOME_TO_ALIAS[assembly],
                                            size=99999)
    except Exception:
        return {'message': 'Error during region search'}

    all_hits['peaks'] = list(results['hits']['hits'])
    all_hits['peak_count'] = len(all_hits['peaks'])
    uuids = [ peak['_id'] for peak in all_hits['peaks'] ]
    uuids = list(set(uuids))
    if not uuids:
        return {'message': 'No uuids found in region'}

    resident_details = {}
    try:
        id_query = {"query": {"ids": {"values": uuids}}}
        res = region_es.search(body=id_query, index=RESIDENT_REGIONSET_KEY, doc_type='default', size=99999)
        hits = res.get("hits", {}).get("hits", [])
        for hit in hits:
            resident_details[hit["_id"]] = hit["_source"]
    except Exception:
        return {'message': 'Error during resident_details search'}

    dataset_ids = set()
    uses_set = set(uses)
    all_hits['file_hits'] = {}
    for uuid in uuids:
        if uuid not in resident_details:
            continue
        if uses and not list(uses_set.intersection(set(resident_details[uuid].get('uses',[])))):
            continue
        dataset_ids.add(resident_details[uuid].get('dataset'))
        all_hits['file_hits'][uuid] = resident_details[uuid]

    all_hits['dataset_paths'] = list(dataset_ids)
    if not peaks_too:
        all_hits['peaks'] = []
        peaks = []  # Don't burden results with too much info

    all_hits['message'] = '%d peaks in %d files belonging to %s experiments in this region' % \
                (all_hits['peak_count'], len(all_hits['file_hits'].keys()), len(all_hits['dataset_paths']))

    return all_hits


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

def sanitize_rsid(rsid):
    return 'rs' + ''.join([a for a in filter(str.isdigit, rsid)])


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
            return (chromosome, start, end)

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
        if 'mappings' not in new_response or len(new_response['mappings']) < 1:
            return('', '', '')
        data = new_response['mappings'][0]['mapped']
        chromosome = 'chr' + data['seq_region_name']
        start = data['start']
        end = data['end']
        return(chromosome, start, end)


def get_rsid_coordinates(id, assembly):
    species = _GENOME_TO_SPECIES[assembly]
    ensembl_url = _ENSEMBL_URL
    if assembly == 'GRCh37':
        ensembl_url = _ENSEMBL_URL_GRCH37
    url = '{ensembl}variation/{species}/{id}?content-type=application/json'.format(
        ensembl=ensembl_url,
        species=species,
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
            if 'PATCH' not in mapping['location']:
                #location = mapping['location']
                if mapping['assembly_name'] == assembly:
                    chromosome, start, end = re.split(':|-', mapping['location'])
                    return('chr' + chromosome, start, end)
                elif assembly == 'GRCh37':
                    return assembly_mapper(location, species, 'GRCh38', assembly)
                elif assembly == 'GRCm37':
                    return assembly_mapper(location, species, 'GRCm38', 'NCBIM37')
        return ('', '', '',)


def get_ensemblid_coordinates(id, assembly):
    species = _GENOME_TO_SPECIES[assembly]
    url = '{ensembl}lookup/id/{id}?content-type=application/json'.format(
        ensembl=_ENSEMBL_URL,
        id=id
    )
    try:
        response = requests.get(url).json()
    except:
        return('', '', '')
    else:
        location = '{chr}:{start}-{end}'.format(
            chr=response['seq_region_name'],
            start=response['start'],
            end=response['end']
        )
        if response['assembly_name'] == assembly:
            chromosome, start, end = re.split(':|-', location)
            return('chr' + chromosome, start, end)
        elif assembly == 'GRCh37':
            return assembly_mapper(location, species, 'GRCh38', assembly)
        elif assembly == 'GRCm37':
            return assembly_mapper(location, species, 'GRCm38', 'NCBIM37')
        else:
            return ('', '', '')

def format_position(position, resolution):
    chromosome, start, end = re.split(':|-', position)
    start = int(start) - resolution
    end = int(end) + resolution
    return '{}:{}-{}'.format(chromosome, start, end)

def regulome_score(file_hits):
    '''Calculate RegulomeDB score based upon hits and voodoo'''
    ChIP = False
    DNase = False
    PWM = False
    Footprint = False
    EQTL = False
    targets = { 'ChIP-seq': [], 'PWM': [], 'Footprint': []}
    for file_hit in file_hits.values():
        assay = file_hit['assay_term_name']
        target = file_hit.get('target')
        if target and assay in ['ChIP-seq', 'PWM', 'Footprint']:
            targets[assay].append(target)

        if not ChIP and assay == 'ChIP-seq':
            ChIP = True
        elif not DNase and assay == 'DNase-seq':
            DNase = True
        if not PWM and assay == 'PWM':              # TODO: Figure out how to recognize PWM
            PWM = True
        if not Footprint and assay == 'Footprint':  # TODO: Figure out how to recognize Footptrints
            Footprint = True
        if not EQTL and assay == 'EQTL':            # TODO: Figure out how to recognize EQTLs
            EQTL = True

    # Targets... For each ChIP target, there should be a PWM and/or Footprint to match
    PWM_matched = False
    Footprint_matched = False
    for target in targets['ChIP-seq']:
        if target in targets['PWM']:
            PWM_matched = True
        if target in targets['Footprint']:
            Footprint_matched = True
        if PWM_matched and Footprint_matched:
            break

    # Now the scoring
    if EQTL:
        if ChIP:
            if PWM_matched and Footprint_matched and DNase:
                return '1a'
            if PWM and Footprint and DNase:
                return '1b'
            if PWM_matched and DNase:
                return '1c'
            if PWM and DNase:
                return '1d'
            if PWM_matched:
                return '1e'
        return '1f'
        if DNase:
            return '1f'
    if ChIP:
        if DNase:
            if PWM:
                if Footprint:
                    if PWM_matched and Footprint_matched:
                        return '2a'
                    return '2b'
                if PWM_matched:
                    return '2c'
                return '3a'
        if PWM_matched:
            score = '3b'
        if DNase:
            return '4'
        return '5'
    if DNase:
        return '5'
    if PWM or Footprint or EQTL:
        return '6'

    return None

@view_config(route_name='regulome-search', request_method='GET', permission='search')
@view_config(route_name='region-search', request_method='GET', permission='search')
def region_search(context, request):
    """
    Search files by region.
    """
    types = request.registry[TYPES]
    page = request.path.split('/')[1]
    result = {
        '@id': '/' + page + '/' + ('?' + request.query_string.split('&referrer')[0] if request.query_string else ''),
        '@type': ['region-search'],
        'title': ('Regulome search' if page.startswith('regulome') else 'Region search'),
        'facets': [],
        '@graph': [],
        'columns': OrderedDict(),
        'notification': '',
        'filters': []
    }
    principals = effective_principals(request)
    es = request.registry[ELASTIC_SEARCH]
    snp_es = request.registry['snp_search']
    region = request.params.get('region', '*')
    region_inside_peak_status = False


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
    result['assembly'] = _GENOME_TO_ALIAS.get(assembly,'GRCh38')
    annotation = request.params.get('annotation', '*')
    chromosome, start, end = ('', '', '')

    if annotation != '*':
        if annotation.lower().startswith('ens'):
            chromosome, start, end = get_ensemblid_coordinates(annotation, assembly)
        else:
            chromosome, start, end = get_annotation_coordinates(es, annotation, assembly)
    elif region != '*':
        region = region.lower()
        if region.startswith('rs'):
            sanitized_region = sanitize_rsid(region)
            chromosome, start, end = get_rsid_coordinates(sanitized_region, assembly)
            region_inside_peak_status = True
        elif region.startswith('ens'):
            chromosome, start, end = get_ensemblid_coordinates(region, assembly)
        elif region.startswith('chr'):
            chromosome, start, end = sanitize_coordinates(region)
    else:
        chromosome, start, end = ('', '', '')
    # Check if there are valid coordinates
    if not chromosome or not start or not end:
        result['notification'] = 'No annotations found'
        return result
    else:
        result['coordinates'] = '{chr}:{start}-{end}'.format(
            chr=chromosome, start=start, end=end
        )

    # Search for peaks for the coordinates we got
    peaks_too = ('peak_metadata' in request.query_string)
    if peaks_too:
        region_inside_peak_status = True
    uses = [FOR_REGION_SEARCH]
    if page.startswith('regulome'):
        uses = [FOR_REGULOME_DB]
    all_hits = region_get_hits(snp_es, assembly, chromosome, start, end, peaks_too=peaks_too,
                                        with_inner_hits=region_inside_peak_status, uses=uses)
    result['notification'] = all_hits['message']
    if 'file_hits' not in all_hits or not all_hits['file_hits']:
        return result

    if page.startswith('regulome') and region.startswith('rs'):
        score = regulome_score(all_hits['file_hits'])
        if score:
            result['notification'] += '.  RegulomeDB score: ' + score

    # if more than one peak found return the experiments with those peak files
    dataset_count = len(all_hits['dataset_paths'])
    if dataset_count > MAX_CLAUSES_FOR_ES:
        log.error("REGION_SEARCH WARNING: region covered by %d datasets is being restricted to %d" % \
                                                            (dataset_count, MAX_CLAUSES_FOR_ES))
        all_hits['dataset_paths'] = all_hits['dataset_paths'][:MAX_CLAUSES_FOR_ES]
        dataset_count = len(all_hits['dataset_paths'])

    if dataset_count:

        query = get_filtered_query('Experiment', [], set(), principals, ['Experiment'])
        del query['query']
        query['post_filter']['bool']['must'].extend([
            {'terms': {'embedded.status': ['released']}},
            {'terms': {'embedded.@id':    all_hits['dataset_paths']}}
        ])
        used_filters = set_filters(request, query, result)
        used_filters['@id'] = all_hits['dataset_paths']
        used_filters['status'] = ['released']
        query['aggs'] = set_facets(_FACETS, used_filters, principals, ['Experiment'])
        schemas = (types[item_type].schema for item_type in ['Experiment'])
        es_results = es.search(
            body=query, index='experiment', doc_type='experiment', size=size, request_timeout=60
        )
        result['@graph'] = list(format_results(request, es_results['hits']['hits']))
        result['total'] = total = es_results['hits']['total']
        result['facets'] = format_facets(es_results, _FACETS, used_filters, schemas, total, principals)
        if peaks_too:
            result['peaks'] = all_hits['peaks']
        result['download_elements'] = get_peak_metadata_links(request)
        if result['total'] > 0:
            result['notification'] = 'Success: ' + result['notification']
            position_for_browser = format_position(result['coordinates'], 200)
            result.update(search_result_actions(request, ['Experiment'], es_results, position=position_for_browser))

    return result


@view_config(route_name='suggest', request_method='GET', permission='search')
def suggest(context, request):
    text = ''
    requested_genome = ''
    if 'q' in request.params:
        text = request.params.get('q', '')
        requested_genome = request.params.get('genome', '')
        # print(requested_genome)

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
