from pkg_resources import resource_filename
from pyramid.response import FileResponse
from pyramid.view import view_config


index_html = resource_filename('encoded', 'index.html')
favicon_ico = resource_filename('encoded', 'static/img/favicon.ico')


@view_config(route_name='antibodies')
@view_config(route_name='home')
def single_page(request):
    return FileResponse(index_html, request=request)


@view_config(route_name='favicon', http_cache=(3600, {'public': True}))
def favicon_view(request):
    return FileResponse(favicon_ico, request=request)
