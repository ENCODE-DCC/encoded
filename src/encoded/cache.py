from pyramid.threadlocal import manager
from sqlalchemy.util import LRUCache


class ManagerLRUCache(object):
    def __init__(self, name):
        self.name = name

    @property
    def cache(self):
        # manager.stack[0] is shared between requests
        if len(manager.stack) < 2:
            return None
        threadlocals = manager.stack[1]
        if self.name not in threadlocals:
            threadlocals[self.name] = LRUCache()
        return threadlocals[self.name]

    def get(self, key, default=None):
        cache = self.cache
        if cache is None:
            return
        cached = cache.get(key)
        if cached is not None:
            return cached[1]
        return default

    def __contains__(self, key):
        cache = self.cache
        if cache is None:
            return False
        return key in cache

    def __setitem__(self, key, value):
        cache = self.cache
        if cache is None:
            return
        self.cache[key] = value
