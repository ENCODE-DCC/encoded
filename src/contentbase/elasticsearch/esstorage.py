from contentbase.util import get_root_request
from elasticsearch.helpers import scan
from pyramid.threadlocal import get_current_request
from zope.interface import alsoProvides
from .interfaces import (
    ELASTIC_SEARCH,
    ICachedItem,
)


def includeme(config):
    from contentbase import STORAGE
    registry = config.registry
    es = registry[ELASTIC_SEARCH]
    es_index = registry.settings['contentbase.elasticsearch.index']
    wrapped_storage = registry[STORAGE]
    registry[STORAGE] = PickStorage(ElasticSearchStorage(es, es_index), wrapped_storage)


class CachedModel(object):
    def __init__(self, hit):
        self.hit = hit
        self.source = hit['_source']

    @property
    def item_type(self):
        return self.source['item_type']

    @property
    def properties(self):
        return self.source['properties']

    @property
    def propsheets(self):
        return self.source['propsheets']

    @property
    def uuid(self):
        return self.source['uuid']

    @property
    def tid(self):
        return self.source['tid']

    def invalidated(self):
        request = get_root_request()
        if request is None:
            return False
        edits = dict.get(request.session, 'edits', None)
        if edits is None:
            return False
        version = self.hit['_version']
        source = self.source
        linked_uuids = set(source['linked_uuids'])
        embedded_uuids = set(source['embedded_uuids'])
        for xid, updated, linked in edits:
            if xid < version:
                continue
            if not embedded_uuids.isdisjoint(updated):
                return True
            if not linked_uuids.isdisjoint(linked):
                return True
        return False

    def used_for(self, item):
        alsoProvides(item, ICachedItem)


class PickStorage(object):
    def __init__(self, read, write):
        self.read = read
        self.write = write

    def storage(self):
        request = get_current_request()
        if request and request.datastore == 'elasticsearch':
            return self.read
        return self.write

    def get_by_uuid(self, uuid):
        storage = self.storage()
        model = storage.get_by_uuid(uuid)
        if storage is self.read:
            if model is None or model.invalidated():
                return self.write.get_by_uuid(uuid)
        return model

    def get_by_unique_key(self, unique_key, name):
        storage = self.storage()
        model = storage.get_by_unique_key(unique_key, name)
        if storage is self.read:
            if model is None or model.invalidated():
                return self.write.get_by_unique_key(unique_key, name)
        return model

    def get_rev_links(self, model, item_type, rel):
        return self.storage().get_rev_links(model, item_type, rel)

    def __iter__(self, item_type=None):
        return self.storage().__iter__(item_type)

    def __len__(self, item_type=None):
        return self.storage().__len__(item_type)

    def create(self, item_type, uuid):
        return self.write.create(item_type, uuid)

    def update(self, model, properties=None, sheets=None, unique_keys=None, links=None):
        return self.write.update(model, properties, sheets, unique_keys, links)


class ElasticSearchStorage(object):
    writeable = False

    def __init__(self, es, index):
        self.es = es
        self.index = index

    def _one(self, query):
        data = self.es.search(index=self.index, body=query)
        hits = data['hits']['hits']
        if len(hits) != 1:
            return None
        model = CachedModel(hits[0])
        return model

    def get_by_uuid(self, uuid):
        query = {
            'filter': {'term': {'uuid': uuid}},
            'version': True,
        }
        return self._one(query)

    def get_by_unique_key(self, unique_key, name):
        term = 'unique_keys.' + unique_key
        query = {
            'filter': {'term': {term: name}},
            'version': True,
        }
        return self._one(query)

    def get_rev_links(self, model, item_type, rel):
        query = {
            'fields': ['uuid'],
            'filter': {
                'and': [
                    {'term': {'links.' + rel: str(model.uuid)}},
                    {'term': {'item_type': item_type}},
                ],
            },
            'version': True,
        }
        data = self.es.search(index=self.index, body=query)
        return [
            hit['fields']['uuid'][0] for hit in data['hits']['hits']
        ]

    def __iter__(self, item_type=None):
        query = {
            'fields': ['uuid'],
            'filter': {'term': {'item_type': item_type}} if item_type else {'match_all': {}},
        }
        for hit in scan(self.es, query=query):
            yield hit['fields']['uuid'][0]

    def __len__(self, item_type=None):
        query = {
            'filter': {'term': {'item_type': item_type}} if item_type else {'match_all': {}},
        }
        return self.es.count(index=self.index, body=query)
