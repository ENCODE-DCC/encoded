from pyramid.httpexceptions import HTTPUnprocessableEntity
from pyramid.view import view_config
from snovault import TYPES
from urllib.parse import urljoin, urlencode


def includeme(config):
    '''Associated views routes'''
    config.add_route('batch_igv', '/batch-igv.json')
    config.scan(__name__)


@view_config(name='igv.json', context='.types.dataset.Dataset', request_method='GET', permission='view')
def dataset_igv(context, request):
    # Disable rendering as html.
    request.accept = 'application/json'
    assemblies = request.params.getall('assembly')
    if len(assemblies) != 1:
        return HTTPUnprocessableEntity("Must specify exactly one assembly")
    assembly = assemblies[0]
    obj = request.embed('/%s' % context.uuid, as_user=True)
    index_mapping = request.registry[TYPES]["File"].schema.get('file_format_index_file_extension', {})
    tracks = list(itertracks(assembly, request.url, index_mapping, [obj]))
    return {
        'reference': assembly,
        'tracks': tracks,
    }


@view_config(route_name='batch_igv', request_method='GET', permission='search')
def search_igv(context, request):
    # Disable rendering as html.
    request.accept = 'application/json'
    params = request.params.dict_of_lists()
    assemblies = params.get('assembly', [])
    if len(assemblies) != 1:
        return HTTPUnprocessableEntity("Must specify exactly one assembly")
    assembly = assemblies[0]
    view = 'region-search' if 'region' in request.params else 'search'
    params['field'] = ALL_FIELDS
    params['frame'] = []
    params['limit'] = ['all']
    results = request.embed('/%s/?%s' % (view, urlencode(params, doseq=True)), as_user=True)
    index_mapping = request.registry[TYPES]["File"].schema.get('file_format_index_file_extension', {})
    tracks = list(itertracks(assembly, request.url, index_mapping, results['@graph']))
    return {
        'reference': assembly,
        'tracks': tracks,
    }


TRACK_MAP = {
    'bigBed': { 'type': 'annotation', 'format': 'bigBed' },
    'bigWig': { 'type': 'wig', 'format': 'bigWig' },

    ## These all require tabix / bam index files to be available for efficient visualization.
    # ('bed', 'narrowPeak'): { 'type': 'annotation', 'format': 'narrowPeak' },
    # ('bed', 'broadPeak'): { 'type': 'annotation', 'format': 'broadPeak'  },
    # 'gff3': { 'type': 'annotation', 'format': 'gff3'  },
    # 'gtf': { 'type': 'annotation', 'format': 'gtf' },
    # 'bam': { 'type': 'alignment', 'format': 'bam' },
    # 'vcf': { 'type': 'variant', 'format': 'vcf' },
    # ('bed', 'bedGraph'): { 'type': 'wig', 'format': 'bedGraph' },

    ## I don't think wig has an index file format, just use bedGraph or bigWig.
    # 'wig': { 'type': 'wig', 'format': 'wig' },
}

FILE_FIELDS = {
    'file_format',
    'file_format_type',
    'href',
    'accession',
    'assembly',
}
DATASET_FIELDS = {
    'accession',
 } | {'files.' + field for field in FILE_FIELDS}
ALL_FIELDS = FILE_FIELDS | DATASET_FIELDS


def itertracks(assembly, baseurl, index_mapping, results):
    for result in results:
        if 'File' in result['@type']:
            yield from filetracks(assembly, baseurl, index_mapping, result)
        elif 'Dataset' in result['@type']:
            for obj in result.get('files', []):
                yield from filetracks(assembly, baseurl, index_mapping, obj)


def filetracks(assembly, baseurl, index_mapping, obj):
    if obj.get('assembly') != assembly:
        return
    file_format = obj.get('file_format')
    file_format_type = obj.get('file_format_type')
    base = TRACK_MAP.get((file_format, file_format_type))
    if base is None:
        base = TRACK_MAP.get(file_format)
    if base is None:
        return
    if 'href' not in obj or 'accession' not in obj:
        return
    url = urljoin(baseurl, obj['href'])
    data = {
        "name": obj['accession'],
        "url": url,
    }
    ext = index_mapping.get(file_format)
    if ext:
        data["indexURL"] = url + ext
    data.update(base)
    yield data


def file_igv_viewable(obj):
    if 'href' not in obj or 'accession' not in obj or 'assembly' not in obj:
        return False
    file_format = obj.get('file_format')
    file_format_type = obj.get('file_format_type')
    base = TRACK_MAP.get((file_format, file_format_type))
    if base is None:
        base = TRACK_MAP.get(file_format)
    return base is not None
