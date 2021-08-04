import json

from redis import StrictRedis
from encoded.searches.interfaces import REDIS_LRU_CACHE
from snovault.elasticsearch.searches.parsers import ParamsParser
from snovault.elasticsearch.searches.responses import FieldedInMemoryResponse
from snovault.elasticsearch.searches.responses import FieldedResponse


_redis_lru_cache = RedisLRUCache(None)


def includeme(config):
    # Handle to grab outside of the request cycle
    # for configuring decorator.
    global _redis_lru_cache
    settings = config.registry.settings
    client = StrictRedis(
        host=settings.get('local_storage_host'),
        port=settings.get('local_storage_port'),
        socket_timeout=3,
        db=4,
    )
    # Bind client asynchronously.
    _redis_lru_cache.client = client
    config.registry[REDIS_LRU_CACHE] = _redis_lru_cache


class RedisLRUCache():

    def __init__(self, client):
        self.client = client

    def __setitem__(self, key, item):
        self.client[key] = json.dumps(item)

    def __getitem__(self, key):
        value = self.client[key]
        return json.loads(value)


def should_cache_search_results(context, request):
    pr = ParamsParser(request)
    limit = pr.get_one_value(
        params=pr.get_limit()
    )
    if limit is None:
        return True
    limit = pr.maybe_int(limit)
    if isinstance(limit, int) and limit <= 25:
        return True
    return False


def make_key_from_request(prefix, context, request):
    pr = ParamsParser(request)
    return f'{prefix}.{str(tuple(sorted(pr._params())))}'


def cached_fielded_response_factory(context, request):
    # If we're caching we want to render results in memory,
    # else we return default FieldedResponse.
    if should_cache_search_results(context, request):
        return FieldedInMemoryResponse
    return FieldedResponse


def get_redis_lru_cache():
    return _redis_lru_cache
