from pyramid.config import Configurator
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

    # Static resources
    config.add_static_view('static', 'static', cache_max_age=STATIC_MAX_AGE)
    config.add_static_view('tests/js', 'tests/js', cache_max_age=STATIC_MAX_AGE)
    config.add_route('favicon', 'favicon.ico')

    config.include(api_routes, route_prefix='/api')

    config.add_route('fallback', '*path')

    config.scan(ignore='encoded.tests')
    return config.make_wsgi_app()
