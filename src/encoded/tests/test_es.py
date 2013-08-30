from pyelasticsearch import ElasticSearch


def test_es_conn():
    connection = ElasticSearch('http://localhost:9200')
    assert connection.servers.live == ['http://localhost:9200']


def test_create_index():
    connection = ElasticSearch('http://localhost:9200')
    result = connection.create_index('test_index')
    assert result == {'acknowledged': True, 'ok': True}


def test_delete_index():
    connection = ElasticSearch('http://localhost:9200')
    result = connection.delete_index('test_index')
    assert result == {'acknowledged': True, 'ok': True}
