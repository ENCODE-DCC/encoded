from collections import OrderedDict
from pyramid.view import view_config
from pyramid.response import Response
from ..embedding import embed
from ..contentbase import simple_path_ids
from urllib.parse import (
    parse_qs,
    urlencode,
)

import csv
import io

# includes concatenated properties
_tsv_mapping = OrderedDict([
    ('File accession', ['files.accession']),
    ('File format', ['files.file_format']),
    ('Output type', ['files.output_type']),
    ('Experiment accession', ['accession']),
    ('Assay', ['assay_term_name']),
    ('Biosample term id', ['biosample_term_id']),
    ('Biosample term name', ['biosample_term_name']),
    ('Biosample type', ['biosample_type']),
    ('Biosample life stage', ['replicates.library.biosample.life_stage']),
    ('Biosample sex', ['replicates.library.biosample.sex']),
    ('Biosample organism', ['replicates.library.biosample.organism.scientific_name']),
    ('Biosample treatments', ['replicates.library.biosample.treatments.treatment_term_name']),
    ('Biosample subcellular fraction term name', ['replicates.library.biosample.subcellular_fraction_term_name']),
    ('Biosample phase', ['replicates.library.biosample.phase']),
    ('Experiment target', ['target.name']),
    ('Antibody accession', ['replicates.antibody.accession']),
    ('Library made from', ['replicates.library.nucleic_acid_term_name']),
    ('Library depleted in', ['replicates.library.depleted_in_term_name']),
    ('Library extraction method', ['replicates.library.extraction_method']),
    ('Library lysis method', ['replicates.library.lysis_method']),
    ('Library crosslinking method', ['replicates.library.crosslinking_method']),
    ('Experiment date released', ['date_released']),
    ('Project', ['award.project']),
    ('Run type', ['replicates.library.paired_ended']),
    ('Read length', ['files.replicate.read_length']),
    ('Library fragmentation method', ['files.replicate.library']),
    ('Library size range', ['files.replicate.library']),
    ('Biosample Age', ['files.replicate.library']),
    ('Biological replicate', ['files.replicate.biological_replicate_number']),
    ('Technical replicate', ['files.replicate.technical_replicate_number']),
    ('Size', ['files.file_size']),
    ('Lab', ['files.lab.title']),
    ('md5sum', ['files.md5sum']),
    ('File download URL', ['files.href']),
    ('Assembly', ['files.assembly']),
    ('Platform', ['files.platform.title'])
])


@view_config(route_name='metadata', request_method='GET')
def metadata_tsv(context, request):

    param_list = parse_qs(request.matchdict['search_params'])
    param_list['field'] = []
    header = []
    file_attributes = []
    for prop in _tsv_mapping:
        header.append(prop)
        param_list['field'] = param_list['field'] + _tsv_mapping[prop]
        if _tsv_mapping[prop][0].startswith('files'):
            file_attributes = file_attributes + _tsv_mapping[prop]
    param_list['limit'] = ['all']
    path = '/search/?%s' % urlencode(param_list, True)
    results = embed(request, path, as_user=True)
    rows = []
    for row in results['@graph']:
        if row['files']:
            exp_data_row = []
            for column in header:
                if not _tsv_mapping[column][0].startswith('files'):
                    temp = []
                    for c in _tsv_mapping[column]:
                        c_value = []
                        for value in simple_path_ids(row, c):
                            if isinstance(value, bool) and c == 'replicates.library.paired_ended':
                                if not value:
                                    value = 'single-ended'
                                else:
                                    value = 'paired-ended'
                            if str(value) not in c_value:
                                c_value.append(str(value))
                        if len(temp):
                            if len(c_value):
                                temp = [x + ' ' + c_value[0] for x in temp]
                        else:
                            temp = c_value
                    exp_data_row.append(', '.join(list(set(temp))))
            f_attributes = ['files.accession', 'files.file_format',
                            'files.output_type']
            for f in row['files']:
                if 'files.file_format' in param_list:
                    if f['file_format'] not in param_list['files.file_format']:
                        continue
                f['href'] = request.host_url + f['href']
                f_row = []
                for attr in f_attributes:
                    f_row.append(f[attr[6:]])
                data_row = f_row + exp_data_row
                internal_prop = True
                for prop in file_attributes:
                    if prop in f_attributes:
                        continue
                    if prop == 'files.replicate.library':
                        if not internal_prop:
                            continue
                        internal_prop = False
                        libraries = []
                        for l in simple_path_ids(f, prop[6:]):
                            libraries.append(l)
                        if len(libraries):
                            library = embed(request, libraries[0])
                            data_row.append(library.get('fragmentation_method', ''))
                            data_row.append(library.get('size_range', ''))
                            if 'biosample' in library:
                                data_row.append(library['biosample'].get('age_display', ''))
                            else:
                                data_row.append('')
                            continue
                        else:
                            data_row = data_row + [''] * 3
                            continue
                    path = prop[6:]
                    temp = []
                    for value in simple_path_ids(f, path):
                        temp.append(str(value))
                    data_row.append(', '.join(list(set(temp))))
                rows.append(data_row)
    fout = io.StringIO()
    writer = csv.writer(fout, delimiter='\t')
    writer.writerow(header)
    writer.writerows(rows)
    return Response(
        content_type='text/tsv',
        body=fout.getvalue(),
        content_disposition='attachment;filename="%s"' % 'metadata.tsv'
    )


@view_config(route_name='batch_download', request_method='GET')
def batch_download(context, request):

    # adding extra params to get requied columsn
    param_list = parse_qs(request.matchdict['search_params'])
    param_list['field'] = ['files.href', 'files.file_format']
    param_list['limit'] = ['all']

    path = '/search/?%s' % urlencode(param_list, True)
    results = embed(request, path, as_user=True)
    metadata_link = '{host_url}/metadata/{search_params}/metadata.tsv'.format(
        host_url=request.host_url,
        search_params=request.matchdict['search_params']
    )
    files = [metadata_link]
    if 'files.file_format' in param_list:
        for exp in results['@graph']:
            for f in exp['files']:
                if f['file_format'] in param_list['files.file_format']:
                    files.append('{host_url}{href}'.format(
                        host_url=request.host_url,
                        href=f['href']
                    ))
    else:
        for exp in results['@graph']:
            for f in exp['files']:
                files.append('{host_url}{href}'.format(
                    host_url=request.host_url,
                    href=f['href']
                ))
    return Response(
        content_type='text/plain',
        body='\n'.join(files),
        content_disposition='attachment; filename="%s"' % 'files.txt'
    )
