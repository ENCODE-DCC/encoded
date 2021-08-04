import json

from redis import StrictRedis
from encoded.searches.interfaces import REDIS_CLIENT
from snovault.elasticsearch.searches.parsers import ParamsParser


def includeme(config):
    settings = config.registry.settings
    config.registry[REDIS_CLIENT] = StrictRedis(
        host=settings.get('local_storage_host'),
        port=settings.get('local_storage_port'),
        socket_timeout=3,
        db=4,
    )


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
