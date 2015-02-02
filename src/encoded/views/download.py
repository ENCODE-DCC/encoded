from pyramid.view import view_config
from pyramid.response import Response
from ..embedding import embed
from urllib.parse import (
    parse_qs,
    urlencode,
)

_exp_columns = [
    'accession',
    'assay_term_id',
    'assay_term_name',
    'biosample_term_id',
    'biosample_term_name',
    'biosample_type',
    'target'
]


@view_config(route_name='metadata', request_method='GET')
def metadata_csv(context, request):

    param_list = parse_qs(request.matchdict['search_params'].encode('utf-8'))
    param_list['frame'] = ['object']
    param_list['field'] = _exp_columns
    param_list['limit'] = ['all']

    path = '/search/?%s' % urlencode(param_list, True)
    results = embed(request, path, as_user=True)

    data = []
    for row in results['@graph']:
        data_row = ''
        for column in _exp_columns:
            row_column = ''
            if column in row:
                row_column = row[column]
            if data_row == '':
                data_row = '{value}'.format(
                    data_row=data_row,
                    value=row_column
                )
            else:
                data_row = '{data_row},{value}'.format(
                    data_row=data_row,
                    value=row_column
                )
        data.append(data_row)
    return Response(
        content_type='text/csv',
        body='\n'.join(data),
        content_disposition='attachment; filename="%s"' % 'metadata.csv'
    )


@view_config(route_name='batch_download', request_method='GET')
def batch_download(context, request):

    # adding extra params to get requied columsn
    param_list = parse_qs(request.matchdict['search_params'].encode('utf-8'))
    param_list['field'] = ['files.href', 'files.md5sum', 'files.file_size', 'files.file_format']
    param_list['files.status'] = ['released']
    param_list['limit'] = ['all']

    path = '/search/?%s' % urlencode(param_list, True)
    results = embed(request, path, as_user=True)
    metadata_link = '{host_url}/metadata/{search_params}'.format(
        host_url=request.host_url,
        search_params=request.matchdict['search_params']
    )
    files = [metadata_link]
    if 'files.file_format' in param_list:
        for exp in results['@graph']:
            for f in exp['files']:
                if f['file_format'] in param_list['file_format']:
                    files.append('{host_url}{href}#md5={md5};size={size}'.format(
                        host_url=request.host_url,
                        href=f['href'],
                        md5=f['md5sum'],
                        size=f['file_size']
                    ))
    else:
        for exp in results['@graph']:
            for f in exp['files']:
                files.append('{host_url}{href}#md5={md5};size={size}'.format(
                    host_url=request.host_url,
                    href=f['href'],
                    md5=f['md5sum'],
                    size=f['file_size']
                ))
    return Response(
        content_type='text/plain',
        body='\n'.join(files),
        content_disposition='attachment; filename="%s"' % 'files.txt'
    )
