from pyramid.response import Response
from pyramid.view import view_config
from ..contentbase import Item
from ..embedding import embed
from collections import OrderedDict
import cgi
from urllib.parse import (
    parse_qs,
    urlencode,
)

TAB = '\t'
NEWLINE = '\n'
HUB_TXT = 'hub.txt'
GENOMES_TXT = 'genomes.txt'
TRACKDB_TXT = 'trackDb.txt'
BIGWIG_FILE_TYPES = ['bigWig']
BIGBED_FILE_TYPES = ['narrowPeak', 'broadPeak', 'bigBed']
FILE_QUERY = {
    'files.file_format': BIGBED_FILE_TYPES + BIGWIG_FILE_TYPES,
    'limit': ['all'],
    'frame': ['embedded']
}


def render(data):
    arr = []
    for i in range(len(data)):
        temp = list(data.popitem())
        str1 = ' '.join(temp)
        arr.append(str1)
    return arr


def get_parent_track(accession, label, visibility):
    parent = OrderedDict([
        ('sortOrder', 'view=+'),
        ('type', 'bed 3'),
        ('subGroup1', 'view Views PK=Peaks SIG=Signals'),
        ('dragAndDrop', 'subTracks'),
        ('visibility', visibility),
        ('compositeTrack', 'on'),
        ('longLabel', label),
        ('shortLabel', label),
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
        ('visibility', 'pack'),
        ('longLabel', label + ' ' + replicate_number),
        ('shortLabel', f['accession']),
        ('parent', parent + ' on'),
        ('bigDataUrl', '{href}?proxy=true'.format(**f)),
        ('type', file_format),
        ('track', f['accession']),
    ])

    if parent == '':
        del(track['parent'])
        del(track['subGroups'])
        track_array = render(track)
        return NEWLINE.join(track_array)
    track_array = render(track)
    return (NEWLINE + (2 * TAB)).join(track_array)


def get_peak_view(accession, view):
    s_label = view + 's'
    track_name = view + 'View'
    view_data = OrderedDict([
        ('autoScale', 'on'),
        ('type', 'bigBed'),
        ('viewUi', 'on'),
        ('visibility', 'pack'),
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
        ('visibility', 'pack'),
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


def generate_trackDb(embedded, visibility):

    files = embedded.get('files', None)
    long_label = '{assay_term_name} of {biosample_term_name} - {accession}'.format(
        assay_term_name=embedded['assay_term_name'],
        biosample_term_name=embedded['biosample_term_name'],
        accession=embedded['accession']
    )
    if 'target' in embedded:
        long_label = long_label + '(Target - {label})'.format(
            label=embedded['target']['label']
        )
    parent = get_parent_track(embedded['accession'], long_label, visibility)
    track_label = '{assay} of {biosample} - {accession}'.format(
        assay=embedded['assay_term_name'],
        biosample=embedded['biosample_term_name'],
        accession=embedded['accession']
    )
    peak_view = ''
    signal_view = ''
    signal_count = 0
    call_count = 0
    for f in files:
        if f['file_format'] in BIGBED_FILE_TYPES:
            if call_count == 0:
                peak_view = get_peak_view(
                    embedded['accession'],
                    embedded['accession'] + 'PK'
                ) + NEWLINE + (2 * TAB)
            else:
                peak_view = peak_view + NEWLINE
            peak_view = peak_view + NEWLINE + (2 * TAB) + get_track(
                f, track_label,
                embedded['accession'] + 'PKView'
            )
            call_count = call_count + 1
        elif f['file_format'] == 'bigWig':
            if signal_count == 0:
                signal_view = get_signal_view(
                    embedded['accession'],
                    embedded['accession'] + 'SIG'
                ) + NEWLINE + (2 * TAB)
            else:
                signal_view = signal_view + NEWLINE
            signal_view = signal_view + NEWLINE + (2 * TAB) + get_track(
                f, track_label,
                embedded['accession'] + 'SIGView'
                )
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


def generate_html(context, request):
    ''' Generates and returns HTML for the track hub'''

    url_ret = (request.url).split('@@hub')
    embedded = {}
    if url_ret[0] == request.url:
        item = request.root.__getitem__((request.url.split('/')[-1])[:-5])
        embedded = embed(request, request.resource_path(item))
    else:
        embedded = embed(request, request.resource_path(context))
    link = request.host_url + '/experiments/' + embedded['accession']
    files_json = embedded.get('files', None)
    data_accession = '<a href={link}>{accession}<a></p>' \
        .format(link=link, accession=embedded['accession'])
    data_description = '<h2>{description}</h2>' \
        .format(description=cgi.escape(embedded['description']))
    data_files = ''
    for f in files_json:
        if f['file_format'] in BIGBED_FILE_TYPES + BIGWIG_FILE_TYPES:
            replicate_number = 'pooled'
            if 'replicate' in f:
                replicate_number = str(f['replicate']['biological_replicate_number'])
            data_files = data_files + \
                '<tr><td>{accession}</td><td>{file_format}</td><td>{output_type}</td><td>{replicate_number}</td><td><a href="{request.host_url}{href}">Click here</a></td></tr>'\
                .format(replicate_number=replicate_number, request=request, **f)

    file_table = '<table><tr><th>Accession</th><th>File format</th><th>Output type</th><th>Biological replicate</th><th>Download link</th></tr>{files}</table>' \
        .format(files=data_files)
    header = '<p>This trackhub was automatically generated from the files and metadata for the experiment - ' + \
        data_accession
    return data_description + header + file_table


def generate_batch_hubs(context, request):
    '''search for the input params and return the trackhub'''

    results = {}
    txt = request.matchdict['txt']
    param_list = parse_qs(request.matchdict['search_params'].encode('utf-8').replace(',,', '&'))

    if len(request.matchdict) == 3:

        # Should generate a HTML page for requests other than trackDb.txt
        if txt != TRACKDB_TXT:
            data_policy = '<br /><a href="http://encodeproject.org/ENCODE/terms.html">ENCODE data use policy</p>'
            return generate_html(context, request) + data_policy

        assembly = str(request.matchdict['assembly'])
        params = dict(param_list, **FILE_QUERY)
        params['assembly'] = [assembly]
        path = '/search/?%s' % urlencode(params, True)
        results = embed(request, path, as_user=True)
        trackdb = ''
        for i, experiment in enumerate(results['@graph']):
            if i < 5:
                if i == 0:
                    trackdb = generate_trackDb(experiment, 'full')
                else:
                    trackdb = trackdb + NEWLINE + generate_trackDb(experiment, 'full')
            else:
                trackdb = trackdb + NEWLINE + generate_trackDb(experiment, 'hide')
        return trackdb
    elif txt == HUB_TXT:
        return NEWLINE.join(get_hub('search'))
    elif txt == GENOMES_TXT:
        path = '/search/?%s' % urlencode(param_list, True)
        results = embed(request, path, as_user=True)
        g_text = ''
        if 'assembly' in param_list:
            for assembly in param_list.get('assembly'):
                if g_text == '':
                    g_text = NEWLINE.join(get_genomes_txt(assembly))
                else:
                    g_text = g_text + 2 * NEWLINE + NEWLINE.join(get_genomes_txt(assembly))
        else:
            for facet in results['facets']:
                if facet['field'] == 'assembly':
                    for term in facet['terms']:
                        if term['doc_count'] != 0:
                            if g_text == '':
                                g_text = NEWLINE.join(get_genomes_txt(term['key']))
                            else:
                                g_text = g_text + 2 * NEWLINE + NEWLINE.join(get_genomes_txt(term['key']))
        return g_text


@view_config(name='hub', context=Item, request_method='GET', permission='view')
def hub(context, request):
    ''' Creates trackhub on fly for a given experiment '''

    url_ret = (request.url).split('@@hub')
    embedded = embed(request, request.resource_path(context))

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
        parent_track = generate_trackDb(embedded, 'full')
        return Response(parent_track, content_type='text/plain')
    else:
        data_policy = '<br /><a href="http://encodeproject.org/ENCODE/terms.html">ENCODE data use policy</p>'
        return Response(generate_html(context, request) + data_policy, content_type='text/html')
