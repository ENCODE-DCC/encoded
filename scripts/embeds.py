'''
For each object, count the number of objects in which it is embedded.

Usage: bin/py embeds.py > embeds.jsonlines
'''

from elasticsearch import Elasticsearch
from elasticsearch.helpers import scan
import json

es = Elasticsearch('localhost:9200')


def embeds_uuid(es, uuid, item_type):
    query = {
        'query': {'terms': {'embedded_uuids': [uuid]}},
        'aggregations': {
            'item_type': {'terms': {'field': 'item_type'}},
        },
    }
    res = es.search(index='encoded', search_type='count', body=query)
    return {
        'uuid': uuid,
        'item_type': item_type,
        'embeds': res['hits']['total']['value'],
        'buckets': res['aggregations']['item_type']['buckets'],
    }


uuid_type = [(hit['_id'], hit['_type']) for hit in scan(es, query={'fields': []})]


# rows = [embeds_uuid(es, uuid, item_type) for uuid, item_type in uuid_type]
for uuid, item_type in uuid_type:
    data = embeds_uuid(es, uuid, item_type)
    print(json.dumps(data))
