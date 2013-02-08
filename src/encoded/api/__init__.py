from pyramid.threadlocal import manager
from pyramid.view import view_config
from ..storage import (
    DBSession,
    CurrentStatement,
    Resource,
    )

collections = [
    ('users', 'user'),
    ('antibodies', 'antibody_approval'),
    ('organisms', 'organism'),
    ('sources', 'source'),
    ('targets', 'target'),
    ('validations', 'validation'),
    ('antibody-lots', 'antibody_lot'),
    ]


def includeme(config):
    config.add_route('home', '')
    for collection, item_type in collections:
        config.add_route(collection, '/%s/' % collection)
        config.add_route(item_type, '/%s/{name}' % collection)
    config.scan('.views')


def include(request, path):
    # Should really be more careful about what gets included instead.
    # Cache cut response time from ~800ms to ~420ms.
    cache = None
    if manager.stack:
        cache = manager.stack[0].setdefault('encoded_include_cache', {})
        result = cache.get(path, None)
        if result is not None:
            return result
    subreq = request.blank(path)
    subreq.override_renderer = 'null_renderer'
    result = request.invoke_subrequest(subreq)
    if cache is not None:
        cache[path] = result
    return result


class CollectionViews(object):
    collection = None
    item_type = None
    properties = None
    links = {
        'self': {'href': '/{collection}/{_uuid}', 'templated': True},
        'collection': {'href': '/{collection}/', 'templated': True},
        'profile': {'href': '/profiles/{item_type}', 'templated': True},
        }
    embedded = None

    @classmethod
    def config(cls, **settings):
        settings['_depth'] = settings.get('_depth', 0) + 1

        def decorate(wrapped):
            assert issubclass(wrapped, cls), "Can only configure %s" % cls.__name__
            view_config(route_name=wrapped.collection, request_method='GET', attr='list', **settings)(wrapped)
            view_config(route_name=wrapped.collection, request_method='POST', attr='create', **settings)(wrapped)
            view_config(route_name=wrapped.item_type, request_method='GET', attr='get', **settings)(wrapped)
            return wrapped

        return decorate

    def __init__(self, request):
        self.request = request
        self.collection_uri = request.route_path(self.collection)

    def item_uri(self, name):
        return self.request.route_path(self.item_type, name=name)

    def expand_embedded(self, model, item):
        if self.embedded is None:
            return None
        objects = {}
        for rel, value in self.embedded.items():
            if isinstance(value, basestring):
                value = include(self.request, value.format(
                    collection_uri=self.collection_uri,
                    item_type=self.item_type,
                    collection=self.collection,
                    **item))
            objects[rel] = value
        return objects

    def expand_links(self, model, item):
        # This should probably go on a metaclass
        merged_links = {}
        for cls in reversed(type(self).mro()):
            merged_links.update(vars(cls).get('links', {}))
        links = {}
        for rel, value in merged_links.items():
            if value is None:
                continue
            if isinstance(value, list):
                raise NotImplemented()
            if value.get('templated', False):
                value = value.copy()
                del value['templated']
                value['href'] = value['href'].format(
                    collection_uri=self.collection_uri,
                    item_type=self.item_type,
                    collection=self.collection,
                    **item)
            links[rel] = value
        return links

    def make_item(self, model):
        item = model.statement.__json__()
        links = self.expand_links(model, item)
        if links is not None:
            item['_links'] = links
        embedded = self.expand_embedded(model, item)
        if embedded is not None:
            item['_embedded'] = embedded
        return item

    def list(self):
        session = DBSession()
        query = session.query(CurrentStatement).filter(CurrentStatement.predicate == self.item_type)
        items = [self.make_item(model) for model in query.all()]
        result = {
            '_embedded': {
                'items': items,
                },
            '_links': {
                'self': {'href': self.collection_uri},
                '/rels/actions': [
                    {
                        'name': 'add-antibody',
                        'title': 'Add antibody',
                        'method': 'POST',
                        'type': 'application/json',
                        'href': self.collection_uri,
                        }
                    ],
                },
            }

        if self.properties is not None:
            result.update(self.properties)

        return result

    def create(self):
        session = DBSession()
        item = self.request.json_body
        rid = item.get('_uuid', None)
        resource = Resource({self.item_type: item}, rid)
        session.add(resource)
        item_uri = self.item_uri(resource.rid)
        self.request.response.status = 201
        self.request.response.location = item_uri
        result = {
            'result': 'success',
            '_links': {
                'profile': {'href': '/profiles/result'},
                'items': [
                    {'href': item_uri},
                    ],
                },
            }
        return result

    def get(self):
        key = (self.request.matchdict['name'], self.item_type)
        session = DBSession()
        model = session.query(CurrentStatement).get(key)
        item = self.make_item(model)
        return item
