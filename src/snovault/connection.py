from past.builtins import basestring
from pyramid.decorator import reify
from uuid import UUID
from .cache import ManagerLRUCache
from .interfaces import (
    CONNECTION,
    STORAGE,
    TYPES,
)


def includeme(config):
    registry = config.registry
    registry[CONNECTION] = Connection(registry)


class UnknownItemTypeError(Exception):
    pass


class Connection(object):
    ''' Intermediates between the storage and the rest of the system
    '''
    def __init__(self, registry):
        self.registry = registry
        self.item_cache = ManagerLRUCache('snovault.connection.item_cache', 1000)
        self.unique_key_cache = ManagerLRUCache('snovault.connection.key_cache', 1000)

    @reify
    def storage(self):
        return self.registry[STORAGE]

    @reify
    def types(self):
        return self.registry[TYPES]

    def get_by_uuid(self, uuid, default=None):
        if isinstance(uuid, basestring):
            try:
                uuid = UUID(uuid)
            except ValueError:
                return default
        elif not isinstance(uuid, UUID):
            raise TypeError(uuid)

        uuid = str(uuid)
        cached = self.item_cache.get(uuid)
        if cached is not None:
            return cached

        model = self.storage.get_by_uuid(uuid)
        if model is None:
            return default

        try:
            Item = self.types.by_item_type[model.item_type].factory
        except KeyError:
            raise UnknownItemTypeError(model.item_type)

        item = Item(self.registry, model)
        model.used_for(item)
        self.item_cache[uuid] = item
        return item

    def get_by_unique_key(self, unique_key, name, default=None):
        pkey = (unique_key, name)

        cached = self.unique_key_cache.get(pkey)
        if cached is not None:
            return self.get_by_uuid(cached)

        model = self.storage.get_by_unique_key(unique_key, name)
        if model is None:
            return default

        uuid = model.uuid
        self.unique_key_cache[pkey] = uuid
        cached = self.item_cache.get(uuid)
        if cached is not None:
            return cached

        try:
            Item = self.types.by_item_type[model.item_type].factory
        except KeyError:
            raise UnknownItemTypeError(model.item_type)

        item = Item(self.registry, model)
        model.used_for(item)
        self.item_cache[uuid] = item
        return item

    def get_rev_links(self, model, rel, *types):
        item_types = [self.types[t].item_type for t in types]
        return self.storage.get_rev_links(model, rel, *item_types)

    def __iter__(self, *types):
        if not types:
            item_types = self.types.by_item_type.keys()
        else:
            item_types = [self.types[t].item_type for t in types]
        for uuid in self.storage.__iter__(*item_types):
            yield uuid

    def __len__(self, *types):
        if not types:
            item_types = self.types.by_item_type.keys()
        else:
            item_types = [self.types[t].item_type for t in types]
        return self.storage.__len__(*item_types)

    def __getitem__(self, uuid):
        item = self.get_by_uuid(uuid)
        if item is None:
            raise KeyError(uuid)
        return item

    def create(self, type_, uuid):
        ti = self.types[type_]
        return self.storage.create(ti.item_type, uuid)

    def update(self, model, properties, sheets=None, unique_keys=None, links=None):
        self.storage.update(model, properties, sheets, unique_keys, links)
