from pyramid.response import Response
from pyramid.view import view_config
from ..contentbase import Item, embed
from collections import OrderedDict

tab = '\t'
newline = '\n'


def render(data):
    arr = []
    for i in range(len(data)):
        temp = list(data.popitem())
        str1 = ' '.join(temp)
        arr.append(str1)
    return arr


def getParentTrack(accession, label):
    parent = OrderedDict([
        ('type', 'bed 3'),
        ('subGroup1', 'view Views PK=Peaks SIG=Signals'),
        ('dragAndDrop', 'subTracks'),
        ('visibility', 'dense'),
        ('compositeTrack', 'on'),
        ('longLabel', accession + ' of ' + label),
        ('shortLabel', accession),
        ('track', accession)
    ])
    parent_array = render(parent)
    return newline.join(parent_array)


def getTrack(f, label, parent):
    file_format = 'bigWig'
    if f['file_format'] in ['narrowPeak', 'broadPeak', 'bigBed']:
        file_format = 'bigBed'
    replicate_number = str(0)
    if 'replicate' in f:
        replicate_number = str(f['replicate']['biological_replicate_number'])
    track = OrderedDict([
        ('color', '255,255,255'),
        ('maxHeightPixels', '100:32:8'),
        ('longLabel', label + ' - ' + f['accession'] + ' - ' + replicate_number),
        ('shortLabel', f['accession']),
        ('parent', parent + ' on'),
        ('bigDataUrl', 'http://encodedcc.sdsc.edu/warehouse/' + f['download_path']),
        ('type', file_format),
        ('track', f['accession']),
    ])
    track_array = render(track)
    return (newline + (2 * tab)).join(track_array)


def getPeaksView(accession, view):
    s_label = view + 's'
    track_name = view + '-view'
    view_data = OrderedDict([
        ('type', 'bigBed'),
        ('viewUI', 'on'),
        ('visibility', 'dense'),
        ('view', 'PK'),
        ('shortLabel', s_label),
        ('parent', accession),
        ('track', track_name)
    ])
    view_array = render(view_data)
    return (newline + tab).join(view_array)


def getSignalsView(accession, view):
    s_label = view + 's'
    track_name = view + '-view'
    view_data = OrderedDict([
        ('type', 'bigWig'),
        ('viewUI', 'on'),
        ('visibility', 'dense'),
        ('view', 'SIG'),
        ('shortLabel', s_label),
        ('parent', accession),
        ('track', track_name)
    ])
    view_array = render(view_data)
    return (newline + tab).join(view_array)


def getGenomeTxt(properties):
    assembly = properties['files'][0]['assembly']
    genome = OrderedDict([
        ('trackDb', assembly + '/trackDb.txt'),
        ('genome', assembly)
    ])
    return render(genome)


def getHubTxt(accession):
    hub = OrderedDict([
        ('email', 'jseth@stanford.edu'),
        ('genomesFile', 'genomes.txt'),
        ('longLabel', 'ENCODE Data Coordination Center Data Hub'),
        ('shortLabel', 'Hub (' + accession + ')'),
        ('hub', 'ENCODE_DCC_' + accession)
    ])
    return render(hub)


@view_config(name='hub', context=Item, request_method='GET', permission='view')
def hub(context, request):
    embedded = embed(request, request.resource_path(context))
    files_json = embedded.get('files', None)
    url_ret = (request.url).split('@@hub')
    if url_ret[1] == '/hub.txt':
        return Response(newline.join(getHubTxt(embedded['accession'])), content_type='text/plain')
    elif url_ret[1] == '/genomes.txt':
        return Response(newline.join(getGenomeTxt(embedded)), content_type='text/plain')
    else:
        long_label = embedded['assay_term_name'] + ' of ' + embedded['biosample_term_name']
        parent = getParentTrack(embedded['accession'], long_label)
        peak_view = ''
        signal_view = ''
        signal_count = 0
        call_count = 0
        for f in files_json:
            if f['file_format'] in ['narrowPeak', 'broadPeak', 'bigBed']:
                if call_count == 0:
                    peak_view = getPeaksView(embedded['accession'], 'PK') + newline + (2 * tab)
                peak_view = peak_view + (2 * newline) + (2 * tab) + getTrack(f, long_label, 'PK-view')
                call_count = call_count + 1
            elif f['file_format'] == 'bigWig':
                if signal_count == 0:
                    signal_view = getSignalsView(embedded['accession'], 'SIG') + newline + (2 * tab)
                else:
                    signal_view = signal_view + newline
                signal_view = signal_view + newline + (2 * tab) + getTrack(f, long_label, 'SIG-view') + \
                    newline + (2 * tab) + 'graphTypeDefault bars'
                signal_count = signal_count + 1
        if signal_view == '':
            parent = parent + (newline * 2) + tab + peak_view
        elif peak_view == '':
            parent = parent + (newline * 2) + tab + signal_view
        else:
            parent = parent + (newline * 2) + tab + peak_view + (newline * 2) + tab + signal_view
        return Response(parent, content_type='text/plain')
