from pyramid.view import view_config
from snovault import TYPES
from snovault.elasticsearch.interfaces import (
    ELASTIC_SEARCH,
    SNP_SEARCH_ES
)
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
from .region_atlas import (
    RegionAtlas,
    RegulomeAtlas
)
from .vis_defines import (
    vis_format_url
)
from collections import OrderedDict
import requests
from urllib.parse import urlencode

import logging
import re
import time

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
    config.add_route('jbrest', '/jbrest/snp141/{assembly}/{cmd}/{chrom}{slash:/?}')
    config.scan(__name__)


def region_get_hits(atlas, assembly, chrom, start, end, peaks_too=False):
    '''Returns a list of file uuids AND dataset paths for chromosome location'''

    all_hits = {}  # { 'dataset_paths': [], 'files': {}, 'datasets': {}, 'peaks': [], 'message': ''}

    (peaks, peak_details) = atlas.find_peaks_filtered(_GENOME_TO_ALIAS[assembly], chrom, start, end,
                                                      peaks_too)
    if not peaks:
        return {'message': 'No hits found in this location'}
    if peak_details is None:
        return {'message': 'Error during peak filtering'}
    if not peak_details:
        return {'message': 'No %s sources found' % atlas.type()}

    all_hits['peak_count'] = len(peaks)
    if peaks_too:
        all_hits['peaks'] = peaks  # For "download_elements", contains 'inner_hits' with positions
    # NOTE: peak['inner_hits']['positions']['hits']['hits'] may exist with uuids but to same file

    (all_hits['datasets'], all_hits['files']) = atlas.details_breakdown(peak_details)
    all_hits['dataset_paths'] = list(all_hits['datasets'].keys())
    all_hits['file_count'] = len(all_hits['files'])
    all_hits['dataset_count'] = len(all_hits['datasets'])

    all_hits['message'] = ('%d peaks in %d files belonging to %s datasets in this region' %
                           (all_hits['peak_count'], all_hits['file_count'],
                            all_hits['dataset_count']))

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


def get_annotation_coordinates(es, aid, assembly):
    ''' Gets annotation coordinates from annotation index in ES '''
    chromosome, start, end = '', '', ''
    try:
        es_results = es.get(index='annotations', doc_type='default', id=aid)
    except Exception:
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
    # maps location on GRCh38 to hg19 for example
    new_url = (_ENSEMBL_URL + 'map/' + species + '/'
               + input_assembly + '/' + location + '/' + output_assembly
               + '/?content-type=application/json')
    try:
        new_response = requests.get(new_url).json()
    except Exception:
        return('', '', '')
    else:
        if 'mappings' not in new_response or len(new_response['mappings']) < 1:
            return('', '', '')
        data = new_response['mappings'][0]['mapped']
        chromosome = 'chr' + data['seq_region_name']
        start = data['start']
        end = data['end']
        return(chromosome, start, end)


def get_rsid_coordinates(rsid, assembly, atlas=None):
    if atlas and assembly in ['GRCh38', 'hg19', 'GRCh37']:
        snp = atlas.snp(_GENOME_TO_ALIAS[assembly], rsid)
        if snp:
            return (snp['chrom'], snp.get('start', ''), snp.get('end', ''))

    species = _GENOME_TO_SPECIES.get(assembly, 'homo_sapiens')
    ensembl_url = _ENSEMBL_URL
    if assembly == 'GRCh37':
        ensembl_url = _ENSEMBL_URL_GRCH37
    url = '{ensembl}variation/{species}/{id}?content-type=application/json'.format(
        ensembl=ensembl_url,
        species=species,
        id=rsid
    )
    try:
        response = requests.get(url).json()
    except Exception:
        return('', '', '')
    else:
        if 'mappings' not in response:
            return('', '', '')
        for mapping in response['mappings']:
            if 'PATCH' not in mapping['location']:
                if mapping['assembly_name'] == assembly:
                    chromosome, start, end = re.split(':|-', mapping['location'])
                    return('chr' + chromosome, start, end)
                elif assembly == 'GRCh37':
                    return assembly_mapper(mapping['location'], species, 'GRCh38', assembly)
                elif assembly == 'GRCm37':
                    return assembly_mapper(mapping['location'], species, 'GRCm38', 'NCBIM37')
        return ('', '', '',)


def get_ensemblid_coordinates(eid, assembly):
    species = _GENOME_TO_SPECIES.get(assembly, 'homo_sapiens')
    url = '{ensembl}lookup/id/{id}?content-type=application/json'.format(
        ensembl=_ENSEMBL_URL,
        id=eid
    )
    try:
        response = requests.get(url).json()
    except Exception:
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


def update_viusalize(result, assembly, dataset_paths, file_statuses):
    '''Restrict visualize to assembly and add Quick View if possible.'''
    vis = result.get('visualize_batch')
    if vis is None:
        vis = {}
    assembly = _GENOME_TO_ALIAS[assembly]
    vis_assembly = vis.pop(assembly, None)
    if vis_assembly is None:
        vis_assembly = {}
    datasets = ''
    count = 0
    for path in dataset_paths:
        datasets += '&dataset=' + path
        count += 1
        # WARNING: Quick View of 100 datasets is probably of little benefit, but who are we to judge
        # if count > 25:    # NOTE: only first 25 datasets
        #    break
    if count >= 1:
        datasets = datasets[9:]  # first '&dataset=' will be redundant in vis_format_url
        pos = result.get('coordinates')
        quickview_url = vis_format_url("quickview", datasets, assembly, position=pos,
                                       file_statuses=file_statuses)
        if quickview_url is not None:
            vis_assembly['Quick View'] = quickview_url
    if not vis_assembly:
        return None
    return {assembly: vis_assembly}


@view_config(route_name='regulome-search', request_method='GET', permission='search')
@view_config(route_name='region-search', request_method='GET', permission='search')
def region_search(context, request):
    """
    Search files by region.
    """
    begin = time.time()  # DEBUG: timing
    types = request.registry[TYPES]
    page = request.path.split('/')[1]
    regulome = page.startswith('regulome')
    result = {
        '@id': '/' + page + '/' + ('?' + request.query_string.split('&referrer')[0]
                                   if request.query_string else ''),
        '@type': ['region-search'],
        'title': ('Regulome search' if regulome else 'Region search'),
        'facets': [],
        '@graph': [],
        'columns': OrderedDict(),
        'notification': '',
        'filters': [],
        'timing': []  # DEBUG: timing
    }
    principals = effective_principals(request)
    es = request.registry[ELASTIC_SEARCH]
    if regulome:
        atlas = RegulomeAtlas(request.registry[SNP_SEARCH_ES])
    else:
        atlas = RegionAtlas(request.registry[SNP_SEARCH_ES])
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
    result['assembly'] = _GENOME_TO_ALIAS.get(assembly, 'GRCh38')
    annotation = request.params.get('annotation', '*')
    chromosome, start, end = ('', '', '')

    result['timing'].append({'preamble': (time.time() - begin)})    # DEBUG: timing
    begin = time.time()                                             # DEBUG: timing
    rsid = None
    if annotation != '*':
        if annotation.lower().startswith('ens'):
            chromosome, start, end = get_ensemblid_coordinates(annotation, assembly)
        else:
            chromosome, start, end = get_annotation_coordinates(es, annotation, assembly)
    elif region != '*':
        region = region.lower()
        if region.startswith('rs'):
            sanitized_region = sanitize_rsid(region)
            chromosome, start, end = get_rsid_coordinates(sanitized_region, assembly, atlas)
            rsid = sanitized_region
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
    result['timing'].append({'get_coords': (time.time() - begin)})  # DEBUG: timing
    begin = time.time()                                             # DEBUG: timing

    # Search for peaks for the coordinates we got
    peaks_too = ('peak_metadata' in request.query_string)
    all_hits = region_get_hits(atlas, assembly, chromosome, start, end,
                               peaks_too=peaks_too)
    result['timing'].append({'peaks': (time.time() - begin)})       # DEBUG: timing
    begin = time.time()                                             # DEBUG: timing
    result['notification'] = all_hits['message']
    if all_hits.get('dataset_count', 0) == 0:
        return result

    # if more than one peak found return the experiments with those peak files
    dataset_count = all_hits['dataset_count']
    if dataset_count > MAX_CLAUSES_FOR_ES:
        log.error("REGION_SEARCH WARNING: region covered by %d datasets is being restricted to %d"
                  % (dataset_count, MAX_CLAUSES_FOR_ES))
        all_hits['dataset_paths'] = all_hits['dataset_paths'][:MAX_CLAUSES_FOR_ES]
        dataset_count = len(all_hits['dataset_paths'])

    if dataset_count:

        # set_type = ['Experiment']
        set_indices = atlas.set_indices()
        allowed_status = atlas.allowed_statuses()
        facets = _FACETS
        if regulome:
            facets = _REGULOME_FACETS

        query = get_filtered_query('Dataset', [], set(), principals, atlas.set_type())
        del query['query']
        query['post_filter']['bool']['must'].append({'terms':
                                                    {'embedded.@id': all_hits['dataset_paths']}})
        query['post_filter']['bool']['must'].append({'terms': {'embedded.status': allowed_status}})

        used_filters = set_filters(request, query, result)
        used_filters['@id'] = all_hits['dataset_paths']
        used_filters['status'] = allowed_status
        query['aggs'] = set_facets(facets, used_filters, principals, ['Dataset'])
        schemas = (types[item_type].schema for item_type in ['Experiment'])
        es_results = es.search(
            body=query, index=set_indices, doc_type=set_indices, size=size, request_timeout=60
        )
        result['@graph'] = list(format_results(request, es_results['hits']['hits']))
        result['total'] = total = es_results['hits']['total']
        result['facets'] = format_facets(es_results, facets, used_filters, schemas, total,
                                         principals)
        if len(result['@graph']) < dataset_count:  # paths should be the chosen few
            all_hits['dataset_paths'] = [dataset['@id'] for dataset in result['@graph']]

        if peaks_too:
            result['peaks'] = all_hits['peaks']
        result['download_elements'] = get_peak_metadata_links(request, result['assembly'],
                                                              chromosome, start, end)
        if result['total'] > 0:
            result['notification'] = 'Success: ' + result['notification']
            position_for_browser = format_position(result['coordinates'], 200)
            result.update(search_result_actions(request, ['Experiment'], es_results,
                          position=position_for_browser))
        result.pop('batch_download', None)  # not desired for region OR regulome

        result['timing'].append({'datasets': (time.time() - begin)})  # DEBUG: timing
        begin = time.time()                                           # DEBUG: timing
        vis = update_viusalize(result, assembly, all_hits['dataset_paths'], allowed_status)
        if vis is not None:
            result['visualize_batch'] = vis
        result['timing'].append({'visualize': (time.time() - begin)})  # DEBUG: timing
        begin = time.time()                                            # DEBUG: timing

        if regulome:
            # score regulome SNPs or point locations
            if (rsid is not None or (int(end) - int(start)) <= 1):
                result['nearby_snps'] = atlas.nearby_snps(result['assembly'], chromosome,
                                                          int(start), rsid)
                result['timing'].append({'nearby_snps': (time.time() - begin)})  # DEBUG: timing
                begin = time.time()                                              # DEBUG: timing
                # NOTE: Needs all hits rather than 'released' or set reduced by facet selection
                regdb_score = atlas.regulome_score(all_hits['datasets'])
                if regdb_score:
                    result['regulome_score'] = regdb_score
            result['timing'].append({'scoring': (time.time() - begin)})  # DEBUG: timing
        else:  # not regulome then clean up message
            if result['notification'].startswith('Success'):
                result['notification'] = 'Success'

    return result


# @view_config(route_name='jbrest', request_method='GET', permission='search')
@view_config(route_name='jbrest')
def jbrest(context, request):
    '''Limited JBrowse REST API support for select region sets'''
    # This allows including SNPs in biodalliance straight from es index and without bigBeds
    #    jbQuery: 'type=HTMLFeatures'
    #    jbURI: .../jbrest/snp141/hg19/features/chr19?start=234&end=5678
    # or jbURI: .../jbrest/snp141/GRCh38/stats/global or

    parts = request.path.split('/')
    parts.pop(0)  # Domain
    parts.pop(0)  # page: jbrest
    region_set = parts.pop(0)
    assembly = parts.pop(0)
    if region_set != 'snp141' or assembly not in ['GRCh38', 'hg19']:
        log.error('jbrest: unsupported request %s', request.url)
        return request.response

    atlas = RegionAtlas(request.registry['snp_search'])
    what = parts.pop(0)
    if what == 'features':
        chrom = parts.pop(0)
        if not chrom.startswith('chr'):
            chrom = 'chr' + chrom
        start = int(request.params.get('start', '-1'))
        end = int(request.params.get('end', '-1'))
        if start < 0 or end < 0 or end < start:
            log.error('jbrest: invalid coordinates %s', request.url)
            return request.response
        snps = atlas.find_snps(assembly, chrom, start, end)
        features = []
        for snp in snps:                         # quick view expects half open
            features.append({'start': snp['start'] - 1, 'end': snp['end'],
                             'name': snp['rsid'], 'uniqueID': snp['rsid']})
        request.response.content_type = 'application/json'
        request.query_string += "&format=json"
        return {'features': features}
    # elif what == 'stats':
    #    if parts[0] != 'global':
    #        log.error('jbrest: only global stats supported %s', request.url)
    #        return response
    #    counts = atlas.counts(assembly)
    #    stats = {}
    #    stats['featureCount'] = counts['SNPs'][assembly]
    #    stats['featureDensity'] = 0.02  # counts['SNPs'][assembly] / 3000000000.0
    #    response.body = bytes_(json.dumps(stats), 'utf-8')

    log.error('jbrest unknown command: %s', request.url)
    return request.response


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
    # NOTE: attempt to use suggest on SNPs in es led to es failure during indexing
    # if text.startswith('rs'):
    es = request.registry[ELASTIC_SEARCH]
    query = {
        "suggest": {
            "default-suggest": {
                "text": text,
                "completion": {
                    "field": "suggest",
                    "size": 20
                }
            }
        }
    }
    try:
        results = es.search(index='annotations', body=query)
    except Exception:
        return result
    else:
        for item in results['suggest']['default-suggest'][0]['options']:
            species = _GENOME_TO_SPECIES.get(requested_genome, 'homo_sapiens').replace('_', ' ')
            if species == item['_source']['payload']['species']:
                result['@graph'].append(item)
        result['@graph'] = result['@graph'][:10]
        return result
