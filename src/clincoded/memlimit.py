# https://code.google.com/p/modwsgi/wiki/RegisteringCleanupCode


class Generator2:
    def __init__(self, iterable, callback, environ):
        self.__iterable = iterable
        self.__callback = callback
        self.__environ = environ

    def __iter__(self):
        for item in self.__iterable:
            yield item

    def close(self):
        try:
            if hasattr(self.__iterable, 'close'):
                self.__iterable.close()
        finally:
            self.__callback(self.__environ)


class ExecuteOnCompletion2:
    def __init__(self, application, callback):
        self.__application = application
        self.__callback = callback

    def __call__(self, environ, start_response):
        try:
            result = self.__application(environ, start_response)
        except:
            self.__callback(environ)
            raise
        return Generator2(result, self.__callback, environ)


import logging
import psutil
import humanfriendly


def rss_checker(rss_limit=None):
    log = logging.getLogger(__name__)
    process = psutil.Process()

    def callback(environ):
        rss = process.memory_info().rss
        if rss_limit and rss > rss_limit:
            msg = "Restarting process. Memory usage exceeds limit of %d: %d"
            log.error(msg, rss_limit, rss)
            process.kill()

    return callback


def filter_app(app, global_conf, rss_limit=None):
    if rss_limit is not None:
        rss_limit = humanfriendly.parse_size(rss_limit)

    callback = rss_checker(rss_limit)
    return ExecuteOnCompletion2(app, callback)
