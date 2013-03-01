from pyramid.exceptions import NotFound
from pyramid.security import (
    Allow,
    Everyone,
)
from pyramid.threadlocal import manager
from ..resource import view
from ..storage import (
    DBSession,
    CurrentStatement,
    Resource,
)


def includeme(config):
    config.scan('.views')


def embed(request, path, result=None):
    # Should really be more careful about what gets included instead.
    # Cache cut response time from ~800ms to ~420ms.
    embedded = None
    if manager.stack:
        embedded = manager.stack[0].setdefault('encoded_embedded', {})
    if result is not None:
        embedded[path] = result
        return result
    result = embedded.get(path, None)
    if result is not None:
        return result
    subreq = request.blank(path)
    subreq.override_renderer = 'null_renderer'
    try:
        result = request.invoke_subrequest(subreq)
    except NotFound:
        raise KeyError(path)
    if embedded is not None:
        embedded[path] = result
    return result


def maybe_include_embedded(request, result):
    if len(manager.stack) != 1:
        return
    embedded = manager.stack[0].get('encoded_embedded', None)
    if embedded:
        result['_embedded'] = {'resources': embedded}


class CollectionViews(object):
    schema = None
    properties = None
    links = {
        'self': {'href': '{collection_uri}{_uuid}', 'templated': True},
        'collection': {'href': '{collection_uri}', 'templated': True},
        'profile': {'href': '/profiles/{item_type}', 'templated': True},
    }
    embedded = {}

    __acl__ = [
        (Allow, Everyone, 'list'),
        (Allow, Everyone, 'add'),
        (Allow, Everyone, 'view'),
        (Allow, Everyone, 'edit'),
    ]

    def __init__(self, request):
        self.request = request
        self.collection_uri = request.route_path(self.__collection_route__)
        self.item_type = self.__route__

    def item_uri(self, name):
        return self.request.route_path(self.__route__, path_segment=name)

    def maybe_embed(self, rel, href):
        if rel in self.embedded:
            embed(self.request, href)

    def expand_links(self, model, item):
        # This should probably go on a metaclass
        merged_links = {}
        for cls in reversed(type(self).mro()):
            merged_links.update(vars(cls).get('links', {}))
        links = {}
        for rel, value_template in merged_links.items():
            if value_template is None:
                continue
            if isinstance(value_template, list):
                out = []
                for member in value_template:
                    value = member.copy()
                    templated = value.pop('templated', False)
                    repeat = value.pop('repeat', None)
                    if not templated:
                        out.append(value)
                        self.maybe_embed(rel, value['href'])
                        continue
                    if repeat:
                        ns = item.copy()
                        repeat_name, repeater = repeat.split()
                        for repeat_value in item[repeater]:
                            ns[repeat_name] = repeat_value
                            value = value.copy()
                            value['href'] = member['href'].format(
                                collection_uri=self.collection_uri,
                                item_type=self.item_type,
                                **ns)
                            out.append(value)
                            self.maybe_embed(rel, value['href'])
                    else:
                        ns = item
                        ns[repeat_name] = repeat_value
                        value['href'] = member['href'].format(
                            collection_uri=self.collection_uri,
                            item_type=self.item_type,
                            **ns)
                        out.append(value)
                        self.maybe_embed(rel, value['href'])
                value = out
            elif value_template.get('templated', False):
                value = value_template.copy()
                del value['templated']
                assert 'repeat' not in value
                value['href'] = value['href'].format(
                    collection_uri=self.collection_uri,
                    item_type=self.item_type,
                    **item)
                self.maybe_embed(rel, value['href'])
            else:
                assert 'repeat' not in value
                value = value_template
                self.maybe_embed(rel, value['href'])
            links[rel] = value
        return links

    def make_item(self, model):
        item = model.statement.__json__()
        links = self.expand_links(model, item)
        if links is not None:
            item['_links'] = links
        return item

    def no_body_needed(self):
        # No need for request data when rendering the single page html
        return self.request.environ.get('encoded.format') == 'html'

    @view(permission='list')
    def collection_get(self):
        try:
            nrows = self.request.params['limit']
        except KeyError:
            nrows = None
        if self.no_body_needed():
            return {}
        session = DBSession()
        query = session.query(CurrentStatement).filter(CurrentStatement.predicate == self.item_type).limit(nrows)
        items = []
        for model in query.all():
            item = self.make_item(model)
            item_uri = item['_links']['self']['href']
            embed(self.request, item_uri, item)
            items.append({'href': item_uri})
        result = {
            '_embedded': {
                'items': items,
            },
            '_links': {
                'self': {'href': self.collection_uri},
                'items': items,
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

        maybe_include_embedded(self.request, result)
        return result

    @view(validators=('validate_collection_post',), permission='add')
    def collection_post(self):
        session = DBSession()
        item = self.request.validated
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

    def validate_collection_post(self):
        data = self.request.json_body
        if self.schema is None:
            self.request.validated = data
            return
        for error in self.schema.iter_errors(data):
            self.request.errors.add('body', list(error.path), error.message)
        if not self.request.errors:
            self.request.validated = self.schema.serialize(data)

    @view(permission='view')
    def get(self):
        key = (self.request.matchdict['path_segment'], self.item_type)
        session = DBSession()
        model = session.query(CurrentStatement).get(key)
        if model is None:
            raise NotFound()
        if self.no_body_needed():
            return {}
        result = self.make_item(model)
        maybe_include_embedded(self.request, result)
        return result
