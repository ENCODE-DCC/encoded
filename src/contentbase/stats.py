import psutil
import time
import pyramid.tweens
from pyramid.threadlocal import manager as threadlocal_manager
from sqlalchemy import event
from sqlalchemy.engine import Engine
from urllib.parse import urlencode


def includeme(config):
    config.add_tween('contentbase.stats.stats_tween_factory', under=pyramid.tweens.INGRESS)


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


class ElasticsearchConnectionMixin(object):
    stats_count_key = 'es_count'
    stats_time_key = 'es_time'

    def stats_record(self, duration):
        request = get_root_request()
        if request is None:
            return

        duration = int(duration * 1e6)
        stats = request._stats
        stats[self.stats_count_key] = stats.get(self.stats_count_key, 0) + 1
        stats[self.stats_time_key] = stats.get(self.stats_time_key, 0) + duration

    def log_request_success(self, method, full_url, path, body, status_code, response, duration):
        self.stats_record(duration)
        return super(ElasticsearchConnectionMixin, self).log_request_success(
            method, full_url, path, body, status_code, response, duration)

    def log_request_fail(self, method, full_url, body, duration, status_code=None, exception=None):
        self.stats_record(duration)
        return super(ElasticsearchConnectionMixin, self).log_request_fail(
            method, full_url, body, duration, status_code, exception)


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
    process = psutil.Process()

    def stats_tween(request):
        stats = request._stats = {}
        rss_begin = stats['rss_begin'] = process.memory_info().rss
        begin = stats['wsgi_begin'] = int(time.time() * 1e6)
        response = handler(request)
        end = stats['wsgi_end'] = int(time.time() * 1e6)
        rss_end = stats['rss_end'] = process.memory_info().rss
        stats['wsgi_time'] = end - begin
        stats['rss_change'] = rss_end - rss_begin

        environ = request.environ
        if 'mod_wsgi.queue_start' in environ:
            queue_begin = int(environ['mod_wsgi.queue_start'])
            stats['queue_begin'] = queue_begin
            stats['queue_time'] = begin - queue_begin

        xs = response.headers['X-Stats'] = urlencode(sorted(stats.items()))
        if getattr(request, '_stats_html_attribute', False):
            response.set_cookie('X-Stats', xs)
        return response

    return stats_tween
