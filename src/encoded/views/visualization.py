from pyramid.response import Response
from pyramid.view import view_config
from ..contentbase import Item, embed
from pyramid.httpexceptions import HTTPFound
from collections import OrderedDict


def getTrack(file_json, label):
    data = OrderedDict([
        ('graphTypeDefault', 'bars'),
        ('maxHeightPixels', '100:32:8'),
        ('color', '128,0,0'),
        ('visibility', 'pack'),
        ('longLabel', label + ' - ' + file_json['accession']),
        ('shortLabel', file_json['accession']),
        ('bigDataUrl', 'http://encodedcc.sdsc.edu/warehouse/' + file_json['download_path']),
        ('type', file_json['file_format']),
        ('track', file_json['accession']),
    ])
    return data


def getGenomeTxt(properties):
    genome = OrderedDict([('trackDb', 'hg19/trackDb.txt'), ('genome', 'hg19')])
    if properties['replicates'][0]['library']['biosample']['organism']['name'] != 'human':
        genome['genome'] = 'mm9'
        genome['trackDb'] = 'mm9/trackDb.txt'
    genome_array = []
    for i in range(len(genome)):
        temp = list(genome.popitem())
        str1 = ' '.join(temp)
        genome_array.append(str1)
    return genome_array


def getHubTxt(accession):
    hub = OrderedDict([
        ('email', 'jseth@stanford.edu'),
        ('genomesFile', 'genomes.txt'),
        ('longLabel', 'ENCODE Data Coordination Center Data Hub'),
        ('shortLabel', 'Hub (' + accession + ')'),
        ('hub', 'ENCODE_DCC_' + accession)
    ])
    hub_array = []
    for i in range(len(hub)):
        temp = list(hub.popitem())
        str1 = ' '.join(temp)
        hub_array.append(str1)
    return hub_array


def getTrackDbTxt(files_json, label):
    tracks = []
    for file_json in files_json:
        if file_json['file_format'] in ['bigWig', 'bigBed']:
            track = getTrack(file_json, label)
            for i in range(len(track)):
                temp = list(track.popitem())
                str1 = ' '.join(temp)
                tracks.append(str1)
            tracks.append('')
    return tracks


@view_config(name='visualize', context=Item, request_method='GET',
             permission='view')
def visualize(context, request):
    embedded = embed(request, request.resource_path(context))
    if embedded['replicates'][0]['library']['biosample']['organism']['name'] != 'human':
        db = 'db=mm9'
    else:
        db = 'db=hg19'
    hub_url = (request.url).replace('@@visualize', '@@hub')
    UCSC_url = 'http://genome.ucsc.edu/cgi-bin/hgTracks?udcTimeout=1&' + db + \
        '&hubUrl=' + hub_url + '/hub.txt'
    print UCSC_url
    return HTTPFound(location=UCSC_url)


@view_config(name='hub', context=Item, request_method='GET',
             permission='view')
def hub(context, request):

    embedded = embed(request, request.resource_path(context))
    files_json = embedded.get('files', None)
    if files_json is not None:
        url_ret = (request.url).split('@@hub')
        if url_ret[1] == '/hub.txt':
            return Response('\n'.join(getHubTxt(embedded['accession'])), content_type='text/plain')
        elif url_ret[1] == '/genomes.txt':
            return Response('\n'.join(getGenomeTxt(embedded)), content_type='text/plain')
        else:
            long_label = embedded['assay_term_name'] + ' of ' + embedded['biosample_term_name']
            return Response('\n'.join(getTrackDbTxt(files_json, long_label)), content_type='text/plain')
