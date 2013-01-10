from pyramid.config import Configurator
from sqlalchemy import engine_from_config
from .storage import DBSession
STATIC_MAX_AGE = 0

routes = {
    '': 'home',
    'antibodies/': 'antibodies',
    'antibodies/{antibody}': 'antibody',
    }


def api_routes(config):
    for pattern, name in routes.items():
        config.add_route(name, pattern)


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    config = Configurator(settings=settings)
    config.include('pyramid_tm')
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)

    # Render an HTML page to browsers and a JSON document for API clients
    config.add_renderer(None, 'encoded.renderers.PageOrJSON')

    # Static resources
    config.add_static_view('static', 'static', cache_max_age=STATIC_MAX_AGE)
    config.add_static_view('tests/js', 'tests/js', cache_max_age=STATIC_MAX_AGE)
    config.add_route('favicon', 'favicon.ico')

    config.include(api_routes)

    config.scan(ignore='encoded.tests')
    return config.make_wsgi_app()
