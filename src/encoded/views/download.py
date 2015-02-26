from collections import OrderedDict
from pyramid.view import view_config
from pyramid.response import Response
from ..embedding import embed
from urllib.parse import (
    parse_qs,
    urlencode,
)

import csv
import io

# includes concatenated properties
_tsv_mapping = OrderedDict([
    ('Accession', ('files.accession')),
    ('Experiment', ('accession')),
    ('Assay', ('assay_term_name')),
    ('Biosample term id', ('biosample_term_id')),
    ('Biosample term name', ('biosample_term_name')),
    ('Biosample type', ('biosample_type')),
    ('Biosample life stage', ('replicates.library.biosample.life_stage')),
    ('Biosample sex', ('replicates.library.biosample.sex')),
    ('Biosample organism', ('replicates.library.biosample.organism.name')),
    ('Biosample treatments', ('replicates.library.biosample.treatments.treatment_term_name')),
    ('Biosample subcellular fraction term name', ('replicates.library.biosample.subcellular_fraction_term_name')),
    ('Biosample phase', ('replicates.library.biosample.phase')),
    ('Experiment target', 'target.name'),
    ('Antibody accession', ('replicates.antibody.accession')),
    ('Nucleic acid term name', ('replicates.library.nucleic_acid_term_name')),
    ('Depleted in term name', ('replicates.library.depleted_in_term_name')),
    ('Library extraction method', ('replicates.library.extraction_method')),
    ('Library fragmentation method', ('replicates.library.fragmentation_method')),
    ('Libary lysis method', ('replicates.library.lysis_method')),
    ('Read length', ('replicates.library.read_length')),
    ('Paired endedness', ('replicates.library.paired_ended')),
    ('Experiment date released', ('date_released')),
    ('Project', ('award.project')),
    ('File format', ('files.file_format')),
    ('Size', ('files.file_size')),
    ('Output type', ('files.output_type')),
    ('Lab', ('files.lab')),
    ('md5sum', ('files.md5sum')),
    ('href', ('files.href')),
    ('Assembly', ('files.assembly'))
])


def dict_generator(indict, pre=None):
    pre = pre[:] if pre else []
    if isinstance(indict, dict):
        for key, value in indict.items():
            if isinstance(value, dict):
                for d in dict_generator(value, [key] + pre):
                    yield d
            elif isinstance(value, list) or isinstance(value, tuple):
                for v in value:
                    for d in dict_generator(v, [key] + pre):
                        yield d
            else:
                yield pre + [key, value]
    else:
        yield indict


@view_config(route_name='metadata', request_method='GET')
def metadata_tsv(context, request):

    param_list = parse_qs(request.matchdict['search_params'].encode('utf-8'))
    param_list['field'] = []
    header = []
    file_attributes = []
    for prop in _tsv_mapping:
        header.append(prop)
        param_list['field'] = param_list['field'] + [_tsv_mapping[prop]]
        if _tsv_mapping[prop].startswith('files'):
            file_attributes.append(_tsv_mapping[prop])
    param_list['limit'] = ['all']
    path = '/search/?%s' % urlencode(param_list, True)
    results = embed(request, path, as_user=True)
    rows = []
    for row in results['@graph']:
        if row['files']:
            exp_data_row = []
            new_data = []
            for arr in dict_generator(row):
                new_data.append(arr)
            for column in header:
                if not _tsv_mapping[column].startswith('files'):
                    path = _tsv_mapping[column].split('.')
                    temp = []
                    for ld in new_data:
                        if sorted(path) == sorted(ld[:-1]):
                            if isinstance(ld[-1], list):
                                temp = temp + ld[-1]
                            else:
                                temp.append(str(ld[-1]))
                    exp_data_row.append(', '.join(list(set(temp))))
            for f in row['files']:
                if 'files.file_format' in param_list:
                    if f['file_format'] not in param_list['files.file_format']:
                        continue
                f['href'] = request.host_url + f['href']
                for prop in file_attributes:
                    value = ''
                    if prop.split('.')[1] in f:
                        value = f[prop.split('.')[1]]
                    if prop.split('.')[1:][0] == 'accession':
                        data_row = [value] + exp_data_row
                    else:
                        data_row.append(value)
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
    param_list = parse_qs(request.matchdict['search_params'].encode('utf-8'))
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
