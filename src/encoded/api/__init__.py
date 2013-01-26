from pyramid.view import view_config
from ..storage import (
    DBSession,
    CurrentStatement,
    Resource,
    )

routes = {
    '': 'home',
    'antibodies/': 'antibodies',
    'antibodies/{name}': 'antibody',
    }


def includeme(config):
    for pattern, name in routes.items():
        config.add_route(name, pattern)
    config.scan('.views')


class CollectionViewsMeta(type):
    def __init__(cls, name, bases, dct):
        super(CollectionViewsMeta, cls).__init__(name, bases, dct)
        if bases == (object, ):
            return
        view_config(route_name=cls.collection, request_method='GET', attr='list')(cls)
        view_config(route_name=cls.collection, request_method='POST', attr='create')(cls)
        view_config(route_name=cls.item_type, request_method='GET', attr='get')(cls)


class CollectionViews(object):
    __metaclass__ = CollectionViewsMeta
    collection = None
    item_type = None
    properties = None

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
        import pytest; pytest.set_trace()
        session = DBSession()
        resource = Resource({self.item_type: self.request.json_body})
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