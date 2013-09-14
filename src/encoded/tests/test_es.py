import pytest
from pyelasticsearch import ElasticSearch, IndexAlreadyExistsError

pytestmark = [
    pytest.mark.es,
]


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


def test_data_index(workbook, testapp):
    ''' method tests the ElasticSearch connection by putting in the mapping and indexing the documents '''
    
    connection = ElasticSearch('http://localhost:9200')

    # Eventually we should be able to get the mapping from the schema
    mapping = {
        'basic': {
            'properties': {
                'target': {
                    'properties': {
                        'lab': {
                            'properties': {
                                'title': {
                                    'type': 'string',
                                    'index': 'not_analyzed'
                                }
                            }
                        }
                    }
                },
                'antibody': {
                    'properties': {
                        'host_organism': {
                            'properties': {
                                'name': {
                                    'type': 'string',
                                    'index': 'not_analyzed'
                                }
                            }
                        }
                    }
                }
            }
        }
    }

    res = testapp.get('/antibodies/?limit=all').maybe_follow(status=200)
    items = res.json['@graph']

    index = 'test'
    try:
        indexer = connection.create_index(index)
        assert indexer == {'acknowledged': True, 'ok': True}
    except IndexAlreadyExistsError:
        connection.delete_index(index)
        connection.create_index(index)
    mapper = connection.put_mapping(index, 'basic', mapping)
    assert mapper == {'acknowledged': True, 'ok': True}

    for item in items:
        item_json = testapp.get(str(item['@id']), headers={'Accept': 'application/json'}, status=200)
        document_id = str(item_json.json['@id'])[-37:-1]
        document = item_json.json
        connection.index(index, 'basic', document, document_id)

    connection.refresh(index)
    count = connection.count('*:*', index=index)
    assert count['count'] == len(items)
