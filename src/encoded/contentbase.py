from pyramid.events import (
    ContextFound,
    subscriber,
)
from pyramid.httpexceptions import (
    HTTPForbidden,
    HTTPInternalServerError,
    HTTPNotFound,
)
from pyramid.location import lineage
from pyramid.security import (
    Allow,
    Everyone,
    has_permission,
)
from pyramid.threadlocal import (
    get_current_request,
    manager,
)
from pyramid.view import view_config
from urllib import unquote
from uuid import UUID
from .objtemplate import ObjectTemplate
from .schema_utils import validate_request
from .storage import (
    DBSession,
    CurrentStatement,
    Resource,
)


def includeme(config):
    config.scan(__name__)


def make_subrequest(request, path):
    """ Make a subrequest

    Copies request environ data for authentication.

    May be better to just pull out the resource through traversal and manually
    perform security checks.
    """
    env = request.environ.copy()
    if path and '?' in path:
        path_info, query_string = path.split('?', 1)
        path_info = unquote(path_info)
    else:
        path_info = unquote(path)
        query_string = ''
    env['PATH_INFO'] = path_info
    env['QUERY_STRING'] = query_string
    subreq = request.__class__(env, method='GET', content_type=None,
                               body=b'')
    subreq.remove_conditional_headers()
    # XXX "This does not remove headers like If-Match"
    return subreq


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
    subreq = make_subrequest(request, path)
    subreq.override_renderer = 'null_renderer'
    try:
        result = request.invoke_subrequest(subreq)
    except HTTPNotFound:
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


def no_body_needed(request):
    # No need for request data when rendering the single page html
    return request.environ.get('encoded.format') == 'html'


def validate_item_content(context, request):
    data = request.json_body
    if isinstance(context, Item):
        schema = context.__parent__.schema
    else:
        schema = context.schema
    if schema is None:
        request.validated = data
        return
    validate_request(schema, request)


def permission_checker(context, request):
    def checker(permission):
        return has_permission(permission, context, request)
    return checker


class Root(object):
    __name__ = ''
    __parent__ = None

    __acl__ = [
        (Allow, Everyone, 'list'),
        (Allow, 'group:admin', 'add'),
        (Allow, Everyone, 'view'),
        (Allow, 'group:admin', 'edit'),
        (Allow, Everyone, 'traverse'),
    ]

    def __init__(self, **properties):
        self.properties = properties
        self.collections = {}

    def __call__(self, request):
        return self

    def __getitem__(self, name):
        return self.collections[name]

    def __json__(self, request=None):
        return self.properties.copy()

    def location(self, name):
        """ Attach a collection at the location ``name``.

        Use as a decorator on Collection subclasses.
        """
        def decorate(factory):
            self.collections[name] = factory(self, name)
            return factory
        return decorate


class Item(object):
    # See http://docs.pylonsproject.org/projects/pyramid/en/latest/narr/resources.html
    def __init__(self, collection, model, acl=None):
        self.__name__ = model.rid
        self.__parent__ = collection
        self.model = model
        if acl is not None:
            self.__acl__ = acl

    @property
    def properties(self):
        return self.model.statement.object

    def __json__(self, request):
        properties = self.properties.copy()
        links = self.expand_links(properties, request)
        if links is not None:
            properties['_links'] = links
        return properties

    def expand_links(self, properties, request):
        # Expand templated links
        ns = properties.copy()
        ns['collection_uri'] = request.resource_path(self.__parent__)
        ns['item_type'] = self.model.predicate
        ns['permission'] = permission_checker(self, get_current_request())
        compiled = ObjectTemplate(self.__parent__.links)
        links = compiled(ns)
        # Embed resources
        embedded = self.__parent__.embedded
        for rel, value in links.items():
            if rel not in embedded:
                continue
            if isinstance(value, list):
                for member in value:
                    embed(request, member['href'])
            else:
                embed(request, value['href'])
        return links


class CustomItemMeta(type):
    """ Give each collection its own Item class to enable
        specific view registration.
    """
    def __init__(self, name, bases, attrs):
        super(CustomItemMeta, self).__init__(name, bases, attrs)
        if 'Item' in attrs:
            return
        item_bases = tuple(base.Item for base in bases
                           if issubclass(base, Collection))
        qualname = getattr(self, '__qualname__', self.__name__)  # PY3 only
        item_attrs = {
            '__module__': self.__module__,
            '__name__': 'Item',
            '__qualname__': qualname + '.Item',
        }
        self.Item = type('Item', item_bases, item_attrs)


class Collection(object):
    __metaclass__ = CustomItemMeta
    Item = Item
    schema = None
    properties = None
    item_type = None
    links = {
        'self': {'href': '{collection_uri}{_uuid}', 'templated': True},
        'collection': {'href': '{collection_uri}', 'templated': True},
        'profile': {'href': '/profiles/{item_type}.json', 'templated': True},
    }
    embedded = {}

    def __init__(self, parent, name):
        self.__name__ = name
        self.__parent__ = parent
        if self.item_type is None:
            self.item_type = type(self).__name__.lower()

        merged_links = {}
        for cls in reversed(type(self).mro()):
            merged_links.update(vars(cls).get('links', {}))
        self.links = merged_links

    def item_acl(self, model):
        return None

    def __getitem__(self, name):
        try:
            name = UUID(name)
        except ValueError:
            raise KeyError(name)
        try:
            item = self.get(name)
        except KeyError:
            # Just in case we get an unexpected KeyError
            # FIXME: exception logging.
            raise HTTPInternalServerError('Traversal raised KeyError')
        if item is None:
            raise KeyError(name)
        return item

    def get(self, name, default=None):
        key = (name, self.item_type)
        session = DBSession()
        model = session.query(CurrentStatement).get(key)
        if model is not None:
            return self.make_item(model)
        return default

    def make_item(self, model):
        acl = self.item_acl(model)
        return self.Item(self, model, acl)

    def add(self, properties):
        rid = properties.get('_uuid', None)
        session = DBSession()
        resource = Resource({self.item_type: properties}, rid)
        session.add(resource)
        item = self.make_item(resource.data[self.item_type])
        self.after_add(item)
        return item

    def after_add(self, item):
        '''Hook for subclasses'''


@view_config(context=Collection, permission='list', request_method='GET')
def collection_list(context, request):
    nrows = request.params.get('limit', None)
    if no_body_needed(request):
        return {}
    session = DBSession()
    query = session.query(CurrentStatement).filter(CurrentStatement.predicate == context.item_type).limit(nrows)
    items = []
    for model in query.all():
        item = context.make_item(model)
        properties = item.__json__(request)
        item_uri = request.resource_path(context, item.__name__)
        embed(request, item_uri, properties)
        items.append({'href': item_uri})
    collection_uri = request.resource_path(context)
    result = {
        '_embedded': {
            'items': items,
        },
        '_links': {
            'self': {'href': collection_uri},
            'items': items,
            '/rels/actions': [
                {
                    'name': 'add-antibody',
                    'title': 'Add antibody',
                    'method': 'POST',
                    'type': 'application/json',
                    'href': collection_uri,
                }
            ],
        },
    }

    if context.properties is not None:
        result.update(context.properties)

    maybe_include_embedded(request, result)
    return result


@view_config(context=Collection, validators=(validate_item_content,), permission='add', request_method='POST')
def collection_add(context, request):
    properties = request.validated
    item = context.add(properties)
    item_uri = request.resource_path(context, item.__name__)
    request.response.status = 201
    request.response.location = item_uri
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


@subscriber(ContextFound)
def traversal_security(event):
    """ Check traversal was permitted at each step
    """
    request = event.request
    for resource in reversed(list(lineage(request.context))):
        result = has_permission('traverse', resource, request)
        if not result:
            msg = 'Unauthorized: traversal failed permission check'
            raise HTTPForbidden(msg, result=result)


@view_config(context=Item, permission='view', request_method='GET')
def item_view(context, request):
    if no_body_needed(request):
        return {}
    properties = context.__json__(request)
    maybe_include_embedded(request, properties)
    return properties


@view_config(context=Item, validators=[validate_item_content], permission='edit', request_method='POST')
def item_edit(context, request):
    uuid = context.model.rid
    collection = context.__parent__
    properties = request.validated
    properties['_uuid'] = uuid  # XXX Should this really be stored in object?
    context.model.resource[collection.item_type] = properties
    item_uri = request.resource_path(context.__parent__, context.__name__)
    request.response.status = 200
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
