from pyramid.config import Configurator
STATIC_MAX_AGE = 0

routes = {
    '': 'home',
    'antibodies/': 'antibodies',
    'favicon.ico': 'favicon',
    }


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    config = Configurator(settings=settings)
    config.add_static_view('static', 'static', cache_max_age=STATIC_MAX_AGE)
    config.add_static_view('tests/js', 'tests/js', cache_max_age=STATIC_MAX_AGE)
    for pattern, name in routes.items():
        config.add_route(name, pattern)
    config.scan()
    return config.make_wsgi_app()
