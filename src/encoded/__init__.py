from pyramid.config import Configurator
from sqlalchemy import engine_from_config
from .storage import DBSession
STATIC_MAX_AGE = 0


def static_resources(config):
    config.add_static_view('static', 'static', cache_max_age=STATIC_MAX_AGE)

    favicon_path = '/static/img/favicon.ico'
    if config.route_prefix:
        favicon_path = '/%s%s' % (config.route_prefix, favicon_path)
    config.add_route('favicon.ico', 'favicon.ico')

    def favicon(request):
        subreq = request.copy()
        subreq.path_info = favicon_path
        response = request.invoke_subrequest(subreq)
        return response

    config.add_view(favicon, route_name='favicon.ico')


def tests_js(config):
    config.add_static_view('tests/js', 'tests/js', cache_max_age=STATIC_MAX_AGE)


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    config = Configurator(settings=settings)
    config.include('pyramid_tm')
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)

    # Render an HTML page to browsers and a JSON document for API clients
    config.add_renderer(None, 'encoded.renderers.PageOrJSON')
    config.include('.api')

    config.include(static_resources)
    config.include(tests_js)

    return config.make_wsgi_app()
