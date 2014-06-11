from pyramid.response import Response
from pyramid.view import view_config
from ..contentbase import Item, embed
from collections import OrderedDict
import cgi

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
        ('longLabel', label + ' - ' + accession),
        ('shortLabel', accession),
        ('track', accession)
    ])
    parent_array = render(parent)
    return newline.join(parent_array)


def getTrack(f, label, parent):
    file_format = 'bigWig'
    sub_group = 'view=SIG'
    if f['file_format'] in ['narrowPeak', 'broadPeak', 'bigBed']:
        file_format = 'bigBed'
        sub_group = 'view=PK'
    replicate_number = ''
    if 'replicate' in f:
        replicate_number = ' (rep - ' + str(f['replicate']['biological_replicate_number']) + ')'
    else:
        replicate_number = ' - pooled'
    track = OrderedDict([
        ('subGroups', sub_group),
        ('longLabel', label + ' - ' + f['accession'] + replicate_number),
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
    track_name = view + 'View'
    view_data = OrderedDict([
        ('maxHeightPixels', '100:32:8'),
        ('type', 'bigBed'),
        ('viewUi', 'on'),
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
    track_name = view + 'View'
    view_data = OrderedDict([
        ('maxHeightPixels', '100:32:8'),
        ('type', 'bigWig'),
        ('viewUi', 'on'),
        ('visibility', 'dense'),
        ('view', 'SIG'),
        ('shortLabel', s_label),
        ('parent', accession),
        ('track', track_name)
    ])
    view_array = render(view_data)
    return (newline + tab).join(view_array)


def getGenomeTxt(properties):
    assembly = properties['assembly']
    genome = OrderedDict([
        ('trackDb', assembly + '/trackDb.txt'),
        ('genome', assembly)
    ])
    return render(genome)


def getHubTxt(accession):
    hub = OrderedDict([
        ('email', 'encode-help@lists.stanford.edu'),
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
    assembly = ''
    if 'assembly' in embedded:
        assembly = embedded['assembly']
    if url_ret[1] == '/hub.txt':
        return Response(newline.join(getHubTxt(embedded['accession'])), content_type='text/plain')
    elif url_ret[1] == '/genomes.txt':
        return Response(newline.join(getGenomeTxt(embedded)), content_type='text/plain')
    elif url_ret[1] == '/' + assembly + '/trackDb.txt':
        if 'target' in embedded:
            long_label = embedded['assay_term_name'] + ' of ' + \
                embedded['biosample_term_name']
        else:
            long_label = embedded['assay_term_name'] + ' of ' + \
                embedded['biosample_term_name'] + ' (' + \
                embedded['target']['name'] + ')'
        parent = getParentTrack(embedded['accession'], long_label)
        peak_view = ''
        signal_view = ''
        signal_count = 0
        call_count = 0
        for f in files_json:
            if f['file_format'] in ['narrowPeak', 'broadPeak', 'bigBed']:
                if call_count == 0:
                    peak_view = getPeaksView(embedded['accession'], 'PK') + newline + (2 * tab)
                else:
                    peak_view = peak_view + newline
                peak_view = peak_view + (2 * newline) + (2 * tab) + getTrack(f, long_label, 'PKView')
                call_count = call_count + 1
            elif f['file_format'] == 'bigWig':
                if signal_count == 0:
                    signal_view = getSignalsView(embedded['accession'], 'SIG') + newline + (2 * tab)
                else:
                    signal_view = signal_view + newline
                signal_view = signal_view + newline + (2 * tab) + getTrack(f, long_label, 'SIGView')
                signal_count = signal_count + 1
        if signal_view == '':
            parent = parent + (newline * 2) + tab + peak_view
        elif peak_view == '':
            parent = parent + (newline * 2) + tab + signal_view
        else:
            parent = parent + (newline * 2) + tab + peak_view + (newline * 2) + tab + signal_view
        return Response(parent, content_type='text/plain')
    else:
        data_accession = '<a href={link}>{accession}<a></p>' \
            .format(link=url_ret[0], accession=embedded['accession'])
        data_description = '<p>{description}</p>' \
            .format(description=cgi.escape(embedded['description']))
        data_files = ''
        for f in files_json:
            if f['file_format'] in ['narrowPeak', 'broadPeak', 'bigBed', 'bigWig']:
                if 'replicate' in f:
                    replicate_number = 'rep - ' + \
                        str(f['replicate']['biological_replicate_number'])
                else:
                    replicate_number = 'pooled'
                data_files = data_files + '<tr><td>{accession}</td><td>{file_format}</td><td>{output_type}</td><td>{replicate_number}</td></tr>'\
                    .format(
                        accession=f['accession'],
                        file_format=f['file_format'],
                        output_type=f['output_type'],
                        replicate_number=replicate_number
                    )
        file_table = '<table><tr><th>Accession</th><th>File format</th><th>Output type</th><th>Replicate</th></tr>{files}</table>' \
            .format(files=data_files)
        data_policy = '<a href="http://encodeproject.org/ENCODE/terms.html">ENCODE data use policy</p>'
        header = '<p><This trackhub was automatically generated from the files and metadata for experiment '\
            + data_accession
        return Response(header + data_description + file_table + data_policy, content_type='text/html')
