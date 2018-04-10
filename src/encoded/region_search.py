from pyramid.view import view_config
from snovault import TYPES
from snovault.elasticsearch.interfaces import ELASTIC_SEARCH
from snovault.elasticsearch.indexer import MAX_CLAUSES_FOR_ES
from elasticsearch.exceptions import (
    NotFoundError
)
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
    FOR_REGULOME_DB,
    FOR_MULTIPLE_USES,
    ENCODED_ALLOWED_STATUSES,
    REGULOME_ALLOWED_STATUSES
)
from .vis_defines import (
    vis_format_url,
    ASSEMBLY_TO_UCSC_ID
)
from collections import OrderedDict
import requests
from urllib.parse import urlencode

import logging
import re
import json

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

_REGULOME_FACETS = [
    ('assay_term_name', {'title': 'Assay'}),
    ('annotation_type', {'title': 'Annotation type'}),
    ('status', {'title': 'Status'}),
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
    # BUG?  within_peaks is not used.
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
    # get all peaks that overlap requested region peak.start <= requested.end and peak.end >= requested.start
    query['query']['bool']['filter']['nested']['query']['bool']['should'].append(get_bool_query(end, start))
    # BUG?  the for loop below adds all ranges, which should be subsets of above overlap net
    #search_ranges = {
    #    'peaks_inside_range': {
    #        'start': start,
    #        'end': end
    #    },
    #    'range_inside_peaks': {
    #        'start': end,
    #        'end': start
    #    },
    #    'peaks_overlap_start_range': {
    #        'start': start,
    #        'end': start
    #    },
    #    'peaks_overlap_end_range': {
    #        'start': end,
    #        'end': end
    #    }
    #}
    #for key, value in search_ranges.items():
    #    query['query']['bool']['filter']['nested']['query']['bool']['should'].append(get_bool_query(value['start'], value['end']))
    if with_inner_hits:
        query['query']['bool']['filter']['nested']['inner_hits'] = {'size': 99999}
    return query


def region_get_hits(region_es, assembly, chrom, start, end, peaks_too=False, with_inner_hits=False, uses=[]):
    '''Returns a list of file uuids AND dataset paths for chromosome location'''

    all_hits = {}  #{ 'dataset_paths': [], 'file_hits': {}, 'peaks': [], 'message': ''}

    region_query = get_peak_query(start, end, with_inner_hits=with_inner_hits, within_peaks=peaks_too)

    try:
        results = region_es.search(body=region_query, index=chrom.lower(),
                                    doc_type=_GENOME_TO_ALIAS[assembly], size=99999)
    except NotFoundError:
        return {'message': 'No uuids found in this location'}
    except Exception as e:
        return {'message': 'Error during region search: ' + str(e)}

    all_hits['peaks'] = list(results['hits']['hits'])
    all_hits['peak_count'] = len(all_hits['peaks'])
    # NOTE: peak['inner_hits']['positions']['hits']['hits'] may exist with uuids but to same file
    uuids = [ peak['_id'] for peak in all_hits['peaks'] ]
    uuids = list(set(uuids))
    if not uuids:
        return {'message': 'No uuids found in region'}

    resident_details = {}
    use_types = [FOR_MULTIPLE_USES]
    if len(uses) == 1:
        use_types.append(uses[0])
    try:
        id_query = {"query": {"ids": {"values": uuids}}}
        res = region_es.search(body=id_query, index=RESIDENT_REGIONSET_KEY, doc_type=use_types, size=99999)
        hits = res.get("hits", {}).get("hits", [])
        for hit in hits:
            resident_details[hit["_id"]] = hit["_source"]
    except Exception:
        return {'message': 'Error during resident_details search'}

    dataset_ids = set()
    #uses_set = set(uses)
    all_hits['file_hits'] = {}
    for uuid in uuids:
        if uuid not in resident_details:
            continue
        # Don't need to check uses, since query was restricted on use_types
        #if uses and not list(uses_set.intersection(set(resident_details[uuid].get('uses',[])))):
        #    continue
        dataset_ids.add(resident_details[uuid].get('dataset'))
        all_hits['file_hits'][uuid] = resident_details[uuid]

    all_hits['dataset_paths'] = list(dataset_ids)
    if not peaks_too:
        all_hits['peaks'] = []
        peaks = []  # Don't burden results with too much info

    all_hits['message'] = '%d peaks in %d files belonging to %s datasets in this region' % \
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
    species = _GENOME_TO_SPECIES.get(assembly, 'homo_sapiens')
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
    species = _GENOME_TO_SPECIES.get(assembly, 'homo_sapiens')
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

regulome_score_rules = [  # TODO: ways to make more efficient?
    ('1a', {'eQTL','ChIP', 'DNase', 'PWM_matched', 'Footprint_matched'}),
    ('1b', {'eQTL','ChIP', 'DNase', 'PWM', 'Footprint'}),
    ('1c', {'eQTL','ChIP', 'DNase', 'PWM_matched'}),
    ('1d', {'eQTL','ChIP', 'DNase', 'PWM'}),
    ('1e', {'eQTL','ChIP', 'PWM_matched'}),
    ('1f', {'eQTL','ChIP','DNase'}),
    ('1f', {'eQTL','ChIP'}),
    ('1f', {'eQTL','DNase'}),
    ('2a', {'ChIP','DNase', 'PWM_matched', 'Footprint_matched'}),
    ('2b', {'ChIP','DNase', 'PWM', 'Footprint'}),
    ('2c', {'ChIP','DNase', 'PWM_matched'}),
    ('3a', {'ChIP','DNase', 'PWM'}),
    ('3b', {'ChIP','PWM_matched'}),
    ('4',  {'ChIP','DNase'}),
    ('5',  {'ChIP'}),
    ('5',  {'DNase'}),
    ('6',  {'PWM'}),
    ('6',  {'Footprint'}),
    ('6',  {'eQTL'}),
]

def regulome_score(file_hits):
    '''Calculate RegulomeDB score based upon hits and voodoo'''
    characterize = set()
    targets = { 'ChIP-seq': [], 'PWM': [], 'Footprint': []}
    for file_hit in file_hits.values():
        data_type = file_hit.get('assay_term_name',file_hit.get('annotation_type'))
        if data_type is None:
            continue
        target = file_hit.get('target')
        if target and data_type in ['ChIP-seq', 'PWM', 'Footprint']:
            targets[data_type].append(target)

        if data_type == 'ChIP-seq':
            characterize.add('ChIP')
        elif data_type in ['DNase-seq', 'FAIRE-seq']:  # TODO: confirm FAIRE is lumped in
            characterize.add('DNase')                  #       aka Chromatin_Structure
        if data_type == 'PWM':                         # TODO: Figure out Position Weight Matrix
            characterize.add('PWM')                    #       From motifs
        if data_type == 'Footprint':                   # TODO: Figure out how to recognize Footptrints
            characterize.add('Footprint')              #       Also in Motifs?
        if data_type in ['eQTLs','dsQTLs']:
            characterize.add('eQTL')

    # Targets... For each ChIP target, there should be a PWM and/or Footprint to match
    to_match = {'PWM_matched', 'Footprint_matched'}
    for target in targets['ChIP-seq']:
        if not to_match:
            break
        if target in targets['PWM']:
            characterize.add('PWM_matched')
            characterize.discard('PWM')  # match implies PWM
            to_match.discard('PWM_matched')
        if target in targets['Footprint']:
            characterize.add('Footprint_matched')
            characterize.discard('Footprint')
            to_match.discard('Footprint_matched')

    # Now the scoring
    for (score, rule) in regulome_score_rules:
        if characterize == rule:
            return score
    return "Found: " + str(characterize)

def update_viusalize(result, assembly, dataset_paths, regulome=False):
    '''Restrict visualize to assembly and add Quick View if possible.'''
    vis = result.get('visualize_batch')
    if vis is None:
        return None
    assembly = _GENOME_TO_ALIAS[assembly]
    vis_assembly = vis.pop(assembly, None)
    if vis_assembly is None:
        return None
    if regulome:
        datasets = ''
        count = 0
        for path in dataset_paths:
            if not path.startswith('/annotations/'):
                datasets += '&dataset=' + path
                count += 1
                if count > 25:
                    break
        if count >= 1 and count <= 25:
            datasets = datasets[9:]  # first dataset= would be redundant
            pos = result.get('coordinates')
            quickview_url = vis_format_url("quickview", datasets, assembly, pos)
            if quickview_url is not None:
                vis_assembly['Quick View'] = quickview_url
    return { assembly: vis_assembly }


@view_config(route_name='regulome-search', request_method='GET', permission='search')
@view_config(route_name='region-search', request_method='GET', permission='search')
def region_search(context, request):
    """
    Search files by region.
    """
    types = request.registry[TYPES]
    page = request.path.split('/')[1]
    regulome = page.startswith('regulome')
    result = {
        '@id': '/' + page + '/' + ('?' + request.query_string.split('&referrer')[0] if request.query_string else ''),
        '@type': ['region-search'],
        'title': ('Regulome search' if regulome else 'Region search'),
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
    if regulome:
        uses = [FOR_REGULOME_DB]
    all_hits = region_get_hits(snp_es, assembly, chromosome, start, end, peaks_too=peaks_too,
                                        with_inner_hits=region_inside_peak_status, uses=uses)
    result['notification'] = all_hits['message']
    if 'file_hits' not in all_hits or not all_hits['file_hits']:
        return result

    # score regulome SNPs or point locations
    if regulome:
        if (region.startswith('rs') or (int(end) - int(start)) <= 5):
            # NOTE: This is on all file hits rather than 'released' or set reduced by facet selection
            regdb_score = regulome_score(all_hits['file_hits'])
            if regdb_score:
                result['regulome_score'] = regdb_score
    else:  # not regulome then clean up message
        if result['notification'].startswith('Success'):
            result['notification']= 'Success'

    # if more than one peak found return the experiments with those peak files
    dataset_count = len(all_hits['dataset_paths'])
    if dataset_count > MAX_CLAUSES_FOR_ES:
        log.error("REGION_SEARCH WARNING: region covered by %d datasets is being restricted to %d" % \
                                                            (dataset_count, MAX_CLAUSES_FOR_ES))
        all_hits['dataset_paths'] = all_hits['dataset_paths'][:MAX_CLAUSES_FOR_ES]
        dataset_count = len(all_hits['dataset_paths'])

    if dataset_count:

        set_type = ['Experiment']
        set_indices = 'experiment'
        allowed_status = ['released']  # ENCODED_ALLOWED_STATUSES
        facets = _FACETS
        if regulome:
            set_type = ['Dataset']
            set_indices = ['experiment','annotation']  # TODO: REGULOME_PRIORITIZED_TYPES ? lowercase
            allowed_status = REGULOME_ALLOWED_STATUSES
            facets = _REGULOME_FACETS

        query = get_filtered_query('Dataset', [], set(), principals, set_type)
        del query['query']
        query['post_filter']['bool']['must'].append({'terms': {'embedded.@id': all_hits['dataset_paths']}})
        query['post_filter']['bool']['must'].append({'terms': {'embedded.status': allowed_status}})

        used_filters = set_filters(request, query, result)
        used_filters['@id'] = all_hits['dataset_paths']
        used_filters['status'] = allowed_status  # TODO: force regulome to show this facet
        query['aggs'] = set_facets(facets, used_filters, principals, ['Dataset'])
        schemas = (types[item_type].schema for item_type in ['Experiment'])
        es_results = es.search(
            body=query, index=set_indices, doc_type=set_indices, size=size, request_timeout=60
        )
        result['@graph'] = list(format_results(request, es_results['hits']['hits']))
        result['total'] = total = es_results['hits']['total']
        result['facets'] = format_facets(es_results, facets, used_filters, schemas, total, principals)

        if peaks_too:
            result['peaks'] = all_hits['peaks']
        result['download_elements'] = get_peak_metadata_links(request)
        if result['total'] > 0:
            result['notification'] = 'Success: ' + result['notification']
            position_for_browser = format_position(result['coordinates'], 200)
            result.update(search_result_actions(request, ['Experiment'], es_results, position=position_for_browser))
        result.pop('batch_download', None)  # not desired for region OR regulome

        vis = update_viusalize(result, assembly, all_hits['dataset_paths'], regulome)
        if vis is not None:
            result['visualize_batch'] = vis

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
            if _GENOME_TO_SPECIES.get(requested_genome,'homo_sapiens').replace('_', ' ') == item['_source']['payload']['species']:
                result['@graph'].append(item)
        result['@graph'] = result['@graph'][:10]
        return result
