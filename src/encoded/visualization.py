from pyramid.response import Response
from pyramid.view import view_config
from contentbase import Item
from collections import OrderedDict
import cgi
from urllib.parse import (
    parse_qs,
    urlencode,
)


def includeme(config):
    config.add_route('batch_hub', '/batch_hub/{search_params}/{txt}')
    config.add_route('batch_hub:trackdb', '/batch_hub/{search_params}/{assembly}/{txt}')
    config.scan(__name__)


TAB = '\t'
NEWLINE = '\n'
HUB_TXT = 'hub.txt'
GENOMES_TXT = 'genomes.txt'
TRACKDB_TXT = 'trackDb.txt'
BIGWIG_FILE_TYPES = ['bigWig']
BIGBED_FILE_TYPES = ['bigBed']


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

    file_format = 'bigWig'
    sub_group = 'view=SIG'

    if f['file_format'] in BIGBED_FILE_TYPES:
        sub_group = 'view=PK'
        file_format = 'bigBed 6 +'
        if f.get('file_format_type') == 'gappedPeak':
            file_format = 'bigBed 12 +'

    label = label + ' - {title} {format} {output}'.format(
        title=f['title'],
        format=f.get('file_format_type', ''),
        output=f['output_type']
    )

    replicate_number = 'rep unknown'
    if len(f['biological_replicates']) == 1:
        replicate_number = 'rep {rep}'.format(
            rep=str(f['biological_replicates'][0])
        )
    elif len(f['biological_replicates']) > 1:
        replicate_number = 'pooled from reps{reps}'.format(
            reps=str(f['biological_replicates'])
        )

    track = OrderedDict([
        ('subGroups', sub_group),
        ('visibility', 'dense'),
        ('longLabel', label + ' ' + replicate_number),
        ('shortLabel', f['title']),
        ('parent', parent + ' on'),
        ('bigDataUrl', '{href}?proxy=true'.format(**f)),
        ('type', file_format),
        ('track', f['title']),
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
        ('type', 'bigBed 6 +'),
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
        ('visibility', 'dense'),
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


def generate_trackDb(embedded, visibility, assembly=None):

    files = embedded.get('files', None)

    # checks if there is assembly specified for each experiment
    new_files = []
    if assembly is not None:
        for f in files:
            if 'assembly' in f and f['assembly'] == assembly:
                new_files.append(f)
    if len(new_files):
        files = new_files

    #   Datasets may have >1  assays, biosamples, or targets
    if type(embedded.get('assay_term_name', 'Unknown')) == list:
        assays = ', '.join(embedded['assay_term_name'])
    else:
        assays = embedded.get('assay_term_name', 'Unknown Assay')

    #   Datasets may have >1  assays, biosamples, or targets
    if type(embedded.get('biosample_term_name', 'Unknown')) == list:
        biosamples = ', '.join(embedded['biosample_term_name'])
    else:
        biosamples = embedded.get('biosample_term_name', 'Unknown Biosample')

    #   Datasets may have >1  assays, biosamples, or targets
    if type(embedded.get('target', None)) == list:
        targets = ', '.join([ t['label'] for t in embedded['target'] ])
    elif embedded.get('target', None):
        targets = embedded['target']['label']
    else:
        targets = ''

    long_label = '{assay_term_name} of {biosample_term_name} - {accession}'.format(
        assay_term_name=assays,
        biosample_term_name=biosamples,
        accession=embedded['accession']
    )
    if targets:
        long_label = long_label + '(Target - {label})'.format(
            label=targets
        )
    parent = get_parent_track(embedded['accession'], long_label, visibility)
    track_label = '{assay} of {biosample} - {accession}'.format(
        assay=assays,
        biosample=biosamples,
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
        embedded = request.embed(request.resource_path(item))
    else:
        embedded = request.embed(request.resource_path(context))
    link = request.host_url + '/experiments/' + embedded['accession']
    files_json = embedded.get('files', None)
    data_accession = '<a href={link}>{accession}<a></p>' \
        .format(link=link, accession=embedded['accession'])
    data_description = '<h2>{description}</h2>' \
        .format(description=cgi.escape(embedded['description']))
    data_files = ''
    for f in files_json:
        if f['file_format'] in BIGBED_FILE_TYPES + BIGWIG_FILE_TYPES:
            replicate_number = 'rep unknown'
            if len(f['biological_replicates']) == 1:
                replicate_number = str(f['biological_replicates'][0])
            elif len(f['biological_replicates']) > 1:
                replicate_number = 'pooled from reps {reps}'.format(
                    reps=str(f['biological_replicates'])
                )
            data_files = data_files + \
                '<tr><td>{title}</batch_hub/type%3Dexperiment/hub.txt/td><td>{file_type}</td><td>{output_type}</td><td>{replicate_number}</td><td><a href="{request.host_url}{href}">Click here</a></td></tr>'\
                .format(replicate_number=replicate_number, request=request, **f)

    file_table = '<table><tr><th>Accession</th><th>File type</th><th>Output type</th><th>Biological replicate</th><th>Download link</th></tr>{files}</table>' \
        .format(files=data_files)
    header = '<p>This trackhub was automatically generated from the files and metadata for the experiment - ' + \
        data_accession
    return data_description + header + file_table


def generate_batch_hubs(context, request):
    '''search for the input params and return the trackhub'''

    results = {}
    txt = request.matchdict['txt']
    param_list = parse_qs(request.matchdict['search_params'].replace(',,', '&'))

    view = 'search'
    if 'region' in param_list:
        view = 'region-search'

    if len(request.matchdict) == 3:

        # Should generate a HTML page for requests other than trackDb.txt
        if txt != TRACKDB_TXT:
            data_policy = '<br /><a href="http://encodeproject.org/ENCODE/terms.html">ENCODE data use policy</p>'
            return generate_html(context, request) + data_policy

        assembly = str(request.matchdict['assembly'])
        params = {
            'files.file_format': BIGBED_FILE_TYPES + BIGWIG_FILE_TYPES,
            'status': ['released'],
        }
        params.update(param_list)
        params.update({
            'assembly': [assembly],
            'limit': ['all'],
            'frame': ['embedded'],
        })
        path = '/%s/?%s' % (view, urlencode(params, True))
        results = request.embed(path, as_user=True)['@graph']
        # if files.file_format is a input param
        if 'files.file_format' in param_list:
            results = [
                result
                for result in results
                if any(
                    f['file_format'] in BIGWIG_FILE_TYPES + BIGBED_FILE_TYPES
                    for f in result.get('files', [])
                )
            ]
        trackdb = ''
        for i, experiment in enumerate(results):
            if i < 5:
                if i == 0:
                    trackdb = generate_trackDb(experiment, 'full', None)
                else:
                    trackdb = trackdb + NEWLINE + generate_trackDb(experiment, 'full', None)
            else:
                trackdb = trackdb + NEWLINE + generate_trackDb(experiment, 'hide', None)
        return trackdb
    elif txt == HUB_TXT:
        return NEWLINE.join(get_hub('search'))
    elif txt == GENOMES_TXT:
        path = '/%s/?%s' % (view, urlencode(param_list, True))
        results = request.embed(path, as_user=True)
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
    embedded = request.embed(request.resource_path(context))

    assemblies = ''
    if 'assembly' in embedded:
        assemblies = embedded['assembly']

    if url_ret[1][1:] == HUB_TXT:
        return Response(
            NEWLINE.join(get_hub(embedded['accession'])),
            content_type='text/plain'
        )
    elif url_ret[1][1:] == GENOMES_TXT:
        g_text = ''
        for assembly in assemblies:
            if g_text == '':
                g_text = NEWLINE.join(get_genomes_txt(assembly))
            else:
                g_text = g_text + 2 * NEWLINE + NEWLINE.join(get_genomes_txt(assembly))
        return Response(g_text, content_type='text/plain')
    elif url_ret[1][1:].endswith(TRACKDB_TXT):
        parent_track = generate_trackDb(embedded, 'full', url_ret[1][1:].split('/')[0])
        return Response(parent_track, content_type='text/plain')
    else:
        data_policy = '<br /><a href="http://encodeproject.org/ENCODE/terms.html">ENCODE data use policy</p>'
        return Response(generate_html(context, request) + data_policy, content_type='text/html')


@view_config(route_name='batch_hub')
@view_config(route_name='batch_hub:trackdb')
def batch_hub(context, request):
    ''' View for batch track hubs '''
    return Response(generate_batch_hubs(context, request), content_type='text/plain')
