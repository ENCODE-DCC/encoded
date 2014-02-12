import pyramid.tweens
import time
from pyramid.settings import asbool
from pyramid.threadlocal import manager as threadlocal_manager
from sqlalchemy import event
from sqlalchemy.engine import Engine
from urllib import urlencode


def includeme(config):
    config.add_tween('.stats.stats_tween_factory',
        under=pyramid.tweens.INGRESS)


def get_root_request():
    if threadlocal_manager.stack:
        return threadlocal_manager.stack[0]['request']


def requests_timing_hook(prefix='requests'):
    count_key = prefix + '_count'
    time_key = prefix + '_time'

    def response_hook(r, *args, **kwargs):
        request = get_root_request()
        if request is None:
            return

        stats = request._stats
        stats[count_key] = stats.get(count_key, 0) + 1
        # requests response.elapsed is a timedelta
        e = r.elapsed
        duration = (e.days * 86400 + e.seconds) * 1000000 + e.microseconds
        stats[time_key] = stats.get(time_key, 0) + duration

    return response_hook


# See http://www.sqlalchemy.org/trac/wiki/UsageRecipes/Profiling
@event.listens_for(Engine, 'before_cursor_execute')
def before_cursor_execute(
        conn, cursor, statement, parameters, context, executemany):
    context._query_start_time = int(time.time() * 1e6)


@event.listens_for(Engine, 'after_cursor_execute')
def after_cursor_execute(
        conn, cursor, statement, parameters, context, executemany):
    end = int(time.time() * 1e6)

    request = get_root_request()
    if request is None:
        return

    stats = request._stats
    stats['db_count'] = stats.get('db_count', 0) + 1
    duration = end - context._query_start_time
    stats['db_time'] = stats.get('db_time', 0) + duration


# http://docs.pylonsproject.org/projects/pyramid/en/latest/narr/hooks.html#creating-a-tween-factory
def stats_tween_factory(handler, registry):

    def stats_tween(request):
        stats = request._stats = {}
        begin = stats['wsgi_begin'] = int(time.time() * 1e6)
        response = handler(request)
        end = stats['wsgi_end'] = int(time.time() * 1e6)
        stats['wsgi_time'] = end - begin
        
        environ = request.environ
        if 'mod_wsgi.queue_start' in environ:
            queue_begin = int(environ['mod_wsgi.queue_start'])
            stats['queue_begin'] = queue_begin
            stats['queue_time'] = begin - queue_begin

        xs = response.headers['X-Stats'] = urlencode(sorted(stats.items()))
        if getattr(request, '_stats_html_attribute', False):
            response.body = response.body.replace('<html', '<html data-stats="%s"' % xs, 1)
        return response

    return stats_tween
