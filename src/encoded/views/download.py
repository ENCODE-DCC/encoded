import collections

from pyramid.view import view_config
from pyramid.response import Response
from ..embedding import embed
from urllib.parse import (
    parse_qs,
    urlencode,
)

_exp_columns = [
    'accession',
    'assay_term_name',
    'biosample_term_id',
    'biosample_term_name',
    'files.accession',
    'files.href',
    'files.file_format',
    'files.file_size',
    'files.output_type',
    'files.lab',
    'files.md5sum'
]


def flatten(d, parent_key='', sep='.'):
    items = []
    for k, v in d.items():
        new_key = parent_key + sep + k if parent_key else k
        if isinstance(v, collections.MutableMapping):
            items.extend(flatten(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)


@view_config(route_name='metadata', request_method='GET')
def metadata_csv(context, request):

    param_list = parse_qs(request.matchdict['search_params'].encode('utf-8'))
    param_list['frame'] = ['object']
    param_list['field'] = _exp_columns
    param_list['limit'] = ['all']

    path = '/search/?%s' % urlencode(param_list, True)
    results = embed(request, path, as_user=True)

    data = ['accession\texperiment\tassay\tbiosample_term_id \
    \tbiosample_term_name\tfile_format\tsize\toutput_type\tlab\tmd5sum\thref']
    for row in results['@graph']:
        data_row = []
        for column in _exp_columns:
            if column.startswith('files'):
                row = flatten(row)
                for f in row['files']:
                    new_row = '\t'.join(data_row)
                    if 'file_format' in param_list:
                        if f['file_format'] in param_list['files.file_format']:
                            new_row = '{accession}\t{row}\t{format}\t{size}\t{type}\t{lab}\t{md5}\t{href}'.format(
                                accession=f['accession'],
                                row=new_row,
                                format=f['file_format'],
                                size=f['file_size'],
                                type=f['output_type'],
                                lab=f['lab'],
                                md5=f['md5sum'],
                                href=f['href']
                            )
                    else:
                        new_row = '{accession}\t{row}\t{format}\t{size}\t{type}\t{lab}\t{md5}\t{href}'.format(
                            accession=f['accession'],
                            row=new_row,
                            format=f['file_format'],
                            size=f['file_size'],
                            type=f['output_type'],
                            lab=f['lab'],
                            md5=f['md5sum'],
                            href=f['href']
                        )
                    data.append(new_row)
                break
            elif column in row:
                data_row.append(row[column])
            else:
                data_row.append('')
    return Response(
        content_type='text/tsv',
        body='\n'.join(data),
        content_disposition='attachment; filename="%s"' % 'metadata.tsv'
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
