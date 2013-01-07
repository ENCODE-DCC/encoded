from pkg_resources import resource_filename
from pyramid.response import FileResponse
from pyramid.view import view_config


index_html = resource_filename('encoded', 'index.html')
favicon_ico = resource_filename('encoded', 'static/img/favicon.ico')

MODELS = [
    {
        'uuid': 'a0000000000000000000000000000001',
        'title': 'First model',
        },
    {
        'uuid': 'b0000000000000000000000000000002',
        'title': 'Second model',
        },
    {
        'uuid': 'c0000000000000000000000000000003',
        'title': 'Third model',
        },
    ]

uuid_model = {model['uuid']: model for model in MODELS}


@view_config(route_name='fallback', request_method='GET')
def html_page(request):
    path = request.matchdict['path']
    if path and path[0] == 'api':
        raise KeyError(request.path_info)
    subreq = request.copy()
    subreq.path_info = '/api' + request.path_info
    response = request.invoke_subrequest(subreq)
    return FileResponse(index_html, request=request)


@view_config(route_name='home', renderer='json')
def home(request):
    return {}


@view_config(route_name='antibodies', renderer='json')
def antibodies(request):
    return MODELS


@view_config(route_name='antibody', renderer='json')
def antibody(request):
    antibody_id = request.matchdict['antibody']
    model = uuid_model[antibody_id]
    return model


@view_config(route_name='favicon', http_cache=(3600, {'public': True}))
def favicon_view(request):
    return FileResponse(favicon_ico, request=request)
