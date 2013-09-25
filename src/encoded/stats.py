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
    stats['db_time'] = stats.get('db_time', 0)  + duration


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
            stats.append(('queue_begin', queue_begin))
            stats.append(('queue_time', begin - queue_begin))

        response.headers['X-Stats'] = urlencode(sorted(stats.items()))
        return response

    return stats_tween
