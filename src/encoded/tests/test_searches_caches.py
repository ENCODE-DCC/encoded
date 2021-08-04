import pytest


def test_searches_caches_should_cache_search_results(dummy_request):
    from encoded.searches.caches import should_cache_search_results
    dummy_request.environ['QUERY_STRING'] = 'type=RNAExpression'
    assert should_cache_search_results({}, dummy_request)
    dummy_request.environ['QUERY_STRING'] = 'type=RNAExpression&limit=25'
    assert should_cache_search_results({}, dummy_request)
    dummy_request.environ['QUERY_STRING'] = 'type=RNAExpression&limit=1'
    assert should_cache_search_results({}, dummy_request)
    dummy_request.environ['QUERY_STRING'] = 'type=RNAExpression&limit=all'
    assert not should_cache_search_results({}, dummy_request)
    dummy_request.environ['QUERY_STRING'] = 'type=RNAExpression&limit="24"'
    assert not should_cache_search_results({}, dummy_request)
    dummy_request.environ['QUERY_STRING'] = 'type=RNAExpression&limit=100'
    assert not should_cache_search_results({}, dummy_request)
    dummy_request.environ['QUERY_STRING'] = 'type=RNAExpression&limit=1000'
    assert not should_cache_search_results({}, dummy_request)
    dummy_request.environ['QUERY_STRING'] = 'type=RNAExpression&limit=abcd'
    assert not should_cache_search_results({}, dummy_request)
    dummy_request.environ['QUERY_STRING'] = 'type=RNAExpression&limit=0'
    assert should_cache_search_results({}, dummy_request)


def test_searches_caches_make_key_from_request(dummy_request):
    from encoded.searches.caches import make_key_from_request
    from functools import partial
    make_key_from_request = partial(make_key_from_request, 'rnaget-request')
    dummy_request.environ['QUERY_STRING'] = 'type=RNAExpression'
    assert (
        make_key_from_request({}, dummy_request)
        == "rnaget-request.(('type', 'RNAExpression'),)"
    )
    dummy_request.environ['QUERY_STRING'] = 'type=RNAExpression&b.s=a&limit=10'
    assert (
        make_key_from_request({}, dummy_request)
        == "rnaget-request.(('b.s', 'a'), ('limit', '10'), ('type', 'RNAExpression'))"
    )
    dummy_request.environ['QUERY_STRING'] = 'limit=10&b.s=a&type=RNAExpression'
    assert (
        make_key_from_request({}, dummy_request)
        == "rnaget-request.(('b.s', 'a'), ('limit', '10'), ('type', 'RNAExpression'))"
    )
    dummy_request.environ['QUERY_STRING'] = 'type=Experiment&type=File&field=replicates.library.biosample'
    assert (
        make_key_from_request({}, dummy_request)
        == "rnaget-request.(('field', 'replicates.library.biosample'), ('type', 'Experiment'), ('type', 'File'))"
    )


def test_searches_caches_redis_lru_cache():
    from encoded.searches.caches import RedisLRUCache
    client = {}
    rc = RedisLRUCache(client)
    with pytest.raises(KeyError):
        rc['x']
    rc['x'] = {'a': 'b', 'c': 'd'}
    assert rc['x'] == {'a': 'b', 'c': 'd'}
    assert client['x'] == '{"a": "b", "c": "d"}'
