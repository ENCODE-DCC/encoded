from pyramid.response import Response
from pyramid.view import view_config
from ..contentbase import Item, embed
from ..renderers import make_subrequest
from collections import OrderedDict
import cgi

TAB = '\t'
NEWLINE = '\n'
HUB_TXT = 'hub.txt'
GENOMES_TXT = 'genomes.txt'
TRACKDB_TXT = 'trackDb.txt'
BIGWIG_FILE_TYPES = ['bigWig']
BIGBED_FILE_TYPES = ['narrowPeak', 'broadPeak', 'bigBed']


def render(data):
    arr = []
    for i in range(len(data)):
        temp = list(data.popitem())
        str1 = ' '.join(temp)
        arr.append(str1)
    return arr


def get_parent_track(accession, label):
    parent = OrderedDict([
        ('sortOrder', 'view=+'),
        ('type', 'bed 3'),
        ('subGroup1', 'view Views PK=Peaks SIG=Signals'),
        ('dragAndDrop', 'subTracks'),
        ('visibility', 'full'),
        ('compositeTrack', 'on'),
        ('longLabel', label),
        ('shortLabel', accession),
        ('track', accession)
    ])
    parent_array = render(parent)
    return NEWLINE.join(parent_array)


def get_track(f, label, parent):
    '''Returns tracks for each file'''

    file_format = 'bigWig 1.000000 3291154.000000'
    sub_group = 'view=SIG'
    
    if f['file_format'] in BIGBED_FILE_TYPES:
        file_format = 'bigBed'
        sub_group = 'view=PK'

    label = label + ' - {accession} {format} {output}'.format(
        accession=f['accession'],
        format=f['file_format'],
        output=f['output_type']
    )

    replicate_number = 'pooled'
    if 'replicate' in f:
        replicate_number = 'rep {rep}'.format(
            rep=str(f['replicate']['biological_replicate_number'])
        )

    track = OrderedDict([
        ('subGroups', sub_group),
        ('visibility', 'full'),
        ('longLabel', label + ' ' + replicate_number),
        ('shortLabel', f['accession']),
        ('parent', parent + ' on'),
        ('bigDataUrl', '{href}?proxy=true'.format(**f)),
        ('type', file_format),
        ('track', f['accession']),
    ])
    track_array = render(track)
    return (NEWLINE + (2 * TAB)).join(track_array)


def get_peak_view(accession, view):
    s_label = view + 's'
    track_name = view + 'View'
    view_data = OrderedDict([
        ('autoScale', 'on'),
        ('type', 'bigBed'),
        ('viewUi', 'on'),
        ('visibility', 'dense'),
        ('view', 'PK'),
        ('shortLabel', s_label),
        ('parent', accession),
        ('track', track_name)
    ])
    view_array = render(view_data)
    return (NEWLINE + TAB).join(view_array)


def get_signal_view(accession, view):
    s_label = view + 's'
    track_name = view + 'View'
    view_data = OrderedDict([
        ('autoScale', 'on'),
        ('maxHeightPixels', '100:32:8'),
        ('type', 'bigWig'),
        ('viewUi', 'on'),
        ('visibility', 'full'),
        ('view', 'SIG'),
        ('shortLabel', s_label),
        ('parent', accession),
        ('track', track_name)
    ])
    view_array = render(view_data)
    return (NEWLINE + TAB).join(view_array)


def get_genomes_txt(assembly):
    genome = OrderedDict([
        ('trackDb', assembly + '/trackDb.txt'),
        ('genome', assembly)
    ])
    return render(genome)


def get_hub(label):
    hub = OrderedDict([
        ('email', 'encode-help@lists.stanford.edu'),
        ('genomesFile', 'genomes.txt'),
        ('longLabel', 'ENCODE Data Coordination Center Data Hub'),
        ('shortLabel', 'Hub (' + label + ')'),
        ('hub', 'ENCODE_DCC_' + label)
    ])
    return render(hub)


def generate_trackDb(files, parent, label, accession):
    
    peak_view = ''
    signal_view = ''
    signal_count = 0
    call_count = 0
    for f in files:
        if f['file_format'] in BIGBED_FILE_TYPES:
            if call_count == 0:
                peak_view = get_peak_view(accession, 'PK') + NEWLINE + (2 * TAB)
            else:
                peak_view = peak_view + NEWLINE
            peak_view = peak_view + NEWLINE + (2 * TAB) + get_track(f, label, 'PKView')
            call_count = call_count + 1
        elif f['file_format'] == 'bigWig':
            if signal_count == 0:
                signal_view = get_signal_view(accession, 'SIG') + NEWLINE + (2 * TAB)
            else:
                signal_view = signal_view + NEWLINE
            signal_view = signal_view + NEWLINE + (2 * TAB) + get_track(f, label, 'SIGView')
            signal_count = signal_count + 1
    if signal_view == '':
        parent = parent + (NEWLINE * 2) + TAB + peak_view
    elif peak_view == '':
        parent = parent + (NEWLINE * 2) + TAB + signal_view
    else:
        parent = parent + (NEWLINE * 2) + TAB + peak_view + (NEWLINE * 2) + TAB + signal_view
    if not parent.endswith('\n'):
        parent = parent + '\n'
    return parent


def search_hubs(request):
    ''' should return files '''
    
    search_params = request.matchdict['search_params']
    search_params = search_params.replace(',,', '&')
    subreq = make_subrequest(request, '/search/?%s' % search_params)
    subreq.override_renderer = 'null_renderer'
    subreq.remote_user = 'INDEXER'
    files = []
    try:
        results = request.invoke_subrequest(subreq)
        for result in results['@graph']:
            subreq2 = make_subrequest(request, result['@id'])
            subreq2.override_renderer = 'null_renderer'
            subreq2.remote_user = 'INDEXER'
            dataset = request.invoke_subrequest(subreq2)
            for f in dataset['files']:
                if f['file_format'] in BIGBED_FILE_TYPES or f['file_format'] in BIGWIG_FILE_TYPES:
                    files.append(f)
    except Exception as e:
        print e
    else:
        parent_track = get_parent_track('search', 'search_trackhub')
        data = generate_trackDb(files, parent_track, 'search_trackhub', 'search')
        return data


def generate_batch_hubs(request):
    '''search for the input params and return the trackhub'''

    txt = request.matchdict['txt']
    if len(request.matchdict) == 3:
        if txt == TRACKDB_TXT:
            return search_hubs(request)
    elif txt == HUB_TXT:
        return NEWLINE.join(get_hub('search'))
    elif txt == GENOMES_TXT:
        params = request.matchdict['search_params']
        for param in params.split(',,'):
            if param.startswith('assembly'):
                g_txt = get_genomes_txt(param.split('=')[1])
                return NEWLINE.join(g_txt)
    else:
        print "Here I am supposed to generate HTML file"


@view_config(name='hub', context=Item, request_method='GET', permission='view')
def hub(context, request):
    ''' Creates trackhub on fly for a given experiment '''

    url_ret = (request.url).split('@@hub')
    embedded = embed(request, request.resource_path(context))
    files_json = embedded.get('files', None)
    
    assembly = ''
    if 'assembly' in embedded:
        assembly = embedded['assembly']
    
    if url_ret[1][1:] == HUB_TXT:
        return Response(
            NEWLINE.join(get_hub(embedded['accession'])),
            content_type='text/plain'
        )
    elif url_ret[1][1:] == GENOMES_TXT:
        return Response(
            NEWLINE.join(get_genomes_txt(embedded['assembly'])),
            content_type='text/plain'
        )
    elif url_ret[1][1:] == assembly + '/' + TRACKDB_TXT:
        long_label = '{assay_term_name} of {biosample_term_name} - {accession}'.format(
            assay_term_name=embedded['assay_term_name'],
            biosample_term_name=embedded['biosample_term_name'],
            accession=embedded['accession']
        )
        if 'target' in embedded:
            long_label = long_label + '(Target - {label})'.format(
                label=embedded['target']['label']
            )
        parent = get_parent_track(embedded['accession'], long_label)
        track_label = '{assay} of {biosample} - {accession}'.format(
            assay=embedded['assay_term_name'],
            biosample=embedded['biosample_term_name'],
            accession=embedded['accession']
        )
        parent_track = generate_trackDb(files_json, parent, track_label, embedded['accession'])
        return Response(parent_track, content_type='text/plain')
    else:
        # Generates and returns HTML for the track hub
        data_accession = '<a href={link}>{accession}<a></p>' \
            .format(link=url_ret[0], accession=embedded['accession'])
        data_description = '<h2>{description}</h2>' \
            .format(description=cgi.escape(embedded['description']))
        data_files = ''
        for f in files_json:
            if f['file_format'] in ['narrowPeak', 'broadPeak', 'bigBed', 'bigWig']:
                replicate_number = 'pooled'
                if 'replicate' in f:
                    replicate_number = str(f['replicate']['biological_replicate_number'])
                data_files = data_files + \
                    '<tr><td>{accession}</td><td>{file_format}</td><td>{output_type}</td><td>{replicate_number}</td><td><a href="{request.host_url}{href}">Click here</a></td></tr>'\
                    .format(replicate_number=replicate_number, request=request, **f)

        file_table = '<table><tr><th>Accession</th><th>File format</th><th>Output type</th><th>Biological replicate</th><th>Download link</th></tr>{files}</table>' \
            .format(files=data_files)
        data_policy = '<br /><a href="http://encodeproject.org/ENCODE/terms.html">ENCODE data use policy</p>'
        header = '<p>This trackhub was automatically generated from the files and metadata for the experiment - ' + \
            data_accession
        return Response(data_description + header + file_table + data_policy, content_type='text/html')
