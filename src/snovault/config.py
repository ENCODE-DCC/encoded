import venusian
from pyramid.interfaces import (
    PHASE2_CONFIG,
)
from .interfaces import (
    COLLECTIONS,
    PHASE1_5_CONFIG,
    ROOT,
    TYPES,
)


def includeme(config):
    registry = config.registry
    registry[COLLECTIONS] = CollectionsTool()
    config.set_root_factory(root_factory)
    # Set a default root if none has been configured.
    config.action(
        ('default_root',), set_default_root,
        args=(config.registry, ), order=PHASE2_CONFIG)


def set_default_root(registry):
    from .resources import Root
    if ROOT not in registry:
        registry[ROOT] = Root(registry)


def root_factory(request):
    return request.registry[ROOT]


def root(factory):
    """ Set the root
    """

    def set_root(config, factory):
        root = factory(config.registry)
        config.registry[ROOT] = root

    def callback(scanner, factory_name, factory):
        scanner.config.action(('root',), set_root,
                              args=(scanner.config, factory),
                              order=PHASE1_5_CONFIG)
    venusian.attach(factory, callback, category='pyramid')

    return factory


def collection(name, **kw):
    """ Attach a collection at the location ``name``.

    Use as a decorator on Collection subclasses.
    """

    def set_collection(config, Collection, name, Item, **kw):
        registry = config.registry
        ti = registry[TYPES].register(Item)
        collection = Collection(registry, name, ti, **kw)
        registry[COLLECTIONS].register(name, collection)

    def decorate(Item):

        def callback(scanner, factory_name, factory):
            scanner.config.action(('collection', name), set_collection,
                                  args=(scanner.config, Item.Collection, name, Item),
                                  kw=kw,
                                  order=PHASE2_CONFIG)
        venusian.attach(Item, callback, category='pyramid')
        return Item

    return decorate


def abstract_collection(name, **kw):
    """ Attach a collection at the location ``name``.

    Use as a decorator on Collection subclasses.
    """

    def set_collection(config, Collection, name, Item, **kw):
        registry = config.registry
        ti = registry[TYPES].register_abstract(Item.__name__)
        registry[TYPES].all[Item] = ti  # XXX Ugly this is here.
        collection = Collection(registry, name, ti, **kw)
        registry[COLLECTIONS].register(name, collection)

    def decorate(Item):

        def callback(scanner, factory_name, factory):
            scanner.config.action(('collection', name), set_collection,
                                  args=(scanner.config, Item.AbstractCollection, name, Item),
                                  kw=kw,
                                  order=PHASE2_CONFIG)
        venusian.attach(Item, callback, category='pyramid')
        return Item

    return decorate


class CollectionsTool(dict):
    def __init__(self):
        self.by_item_type = {}

    def register(self, name, value):
        self[name] = value
        ti = value.type_info
        self[ti.name] = value
        if hasattr(ti, 'item_type'):
            self[ti.item_type] = value
            self.by_item_type[value.type_info.item_type] = value
