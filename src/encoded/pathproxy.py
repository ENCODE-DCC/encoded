""" Path based proxy similar to rewrite rule
"""

from wsgiproxy import TransparentProxy
import re


def pathproxy(global_conf, method='GET', **settings):
    proxy = TransparentProxy(**settings)
    pattern = re.compile(r'^/?(https?)\:/+([^/]+)(.*)$')

    def app(environ, start_response):
        """ url of form
            /script_name/http:/example.org/path?query
        """
        environ = environ.copy()
        environ['REQUEST_METHOD'] = 'method'
        environ.pop('SERVER_PORT', None)
        match = pattern.match(environ['PATH_INFO'])
        if match is None:
            raise ValueError(environ['PATH_INFO'])
        environ['wsgi.url_scheme'], environ['HTTP_HOST'], environ['PATH_INFO'] = match.groups()
        return proxy(environ, start_response)

    return app
