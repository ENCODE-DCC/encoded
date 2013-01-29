from pyramid.view import view_config
from ..storage import (
    DBSession,
    CurrentStatement,
    Resource,
    )

collections = [
    ('antibodies', 'antibody'),
    ('organisms', 'organism'),
    ('sources', 'source'),
    ('targets', 'target'),
    ('validations', 'validation'),
    ('approvals', 'approval'),
    ]


def includeme(config):
    config.add_route('home', '')
    for collection, item_type in collections:
        config.add_route(collection, '/%s/' % collection)
        config.add_route(item_type, '/%s/{name}' % collection)
    config.scan('.views')


class CollectionViews(object):
    collection = None
    item_type = None
    properties = None

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

    def list(self):
        session = DBSession()
        query = session.query(CurrentStatement).filter(CurrentStatement.predicate == self.item_type)
        items = []
        for model in query.all():
            item = model.statement.__json__()
            item['_links'] = {
                'self': {'href': self.item_uri(model.rid)},
                'collection': {'href': self.collection_uri},
                }
            items.append(item)
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

        if self.properties:
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
        item_uri = self.item_uri(model.rid)
        result = model.statement.__json__()
        result['_links'] = {
            '/rels/actions': [
                {
                    'name': 'save',
                    'title': 'Save',
                    'method': 'POST',
                    'type': 'application/json',
                    'href': item_uri,
                    },
                ],
            'self': {'href': item_uri},
            'collection': {'href': self.collection_uri},
            'profile': {'href': '/profiles/' + self.item_type},
            }
        return result
