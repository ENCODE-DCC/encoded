# See http://docs.pylonsproject.org/projects/pyramid/en/latest/narr/resources.html

from pyramid.events import (
    ContextFound,
    subscriber,
)
from pyramid.httpexceptions import (
    HTTPConflict,
    HTTPForbidden,
    HTTPInternalServerError,
    HTTPNotFound,
)
from pyramid.location import lineage
from pyramid.security import (
    ALL_PERMISSIONS,
    Allow,
    Authenticated,
    Deny,
    Everyone,
    has_permission,
)
from pyramid.threadlocal import (
    manager,
)
from pyramid.view import view_config
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import FlushError
from urllib import unquote
from uuid import (
    UUID,
    uuid4,
)
from .objtemplate import ObjectTemplate
from .schema_utils import validate_request
from .storage import (
    DBSession,
    CurrentStatement,
    Resource,
    Key,
)
_marker = object()


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


def setting_uuid_permitted(context, request):
    data = request.json
    _uuid = data.get('_uuid', _marker)
    if _uuid is _marker:
        return

    result = has_permission('add_with_uuid', context, request)
    if not result:
        msg = 'Unauthorized: setting _uuid not permitted'
        raise HTTPForbidden(msg, result=result)

    try:
        UUID(_uuid)
    except ValueError:
        msg = "%r is not a %r" % (_uuid, 'uuid')
        request.errors.add('body', ['_uuid'], msg)

    request.validated['_uuid'] = _uuid


def validate_item_content(context, request):
    data = request.json
    data.pop('_uuid', None)
    if isinstance(context, Item):
        schema = context.__parent__.schema
    else:
        schema = context.schema
    if schema is None:
        request.validated.update(data)
        return
    validate_request(schema, request, data)


def permission_checker(context, request):
    def checker(permission):
        return has_permission(permission, context, request)
    return checker


def acl_from_settings(settings):
    acl = []
    for k, v in settings.iteritems():
        if k.startswith('allow.'):
            action = Allow
            permission = k[len('allow.'):]
            principals = v.split()
        elif k.startswith('deny.'):
            action = Deny
            permission = k[len('deny.'):]
            principals = v.split()
        else:
            continue
        if permission == 'ALL_PERMISSIONS':
            permission = ALL_PERMISSIONS
        for principal in principals:
            if principal == 'Authenticated':
                principal = Authenticated
            elif principal == 'Everyone':
                principal = Everyone
            acl.append((action, principal, permission))
    return acl


class Root(object):
    __name__ = ''
    __parent__ = None

    def __init__(self, **properties):
        self.properties = properties
        self.collections = {}
        self.by_item_type = {}

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
            collection = factory(self, name)
            self.collections[name] = collection
            self.by_item_type[collection.item_type] = collection
            return factory
        return decorate


class MergedLinksMeta(type):
    """ Merge the links from the subclass with its bases
    """
    def __init__(self, name, bases, attrs):
        super(MergedLinksMeta, self).__init__(name, bases, attrs)
        self.merged_links = {}
        for cls in reversed(self.mro()):
            links = vars(cls).get('links', None)
            if links is not None:
                self.merged_links.update(links)
        self.merged_keys = []
        for cls in reversed(self.mro()):
            for key in vars(cls).get('keys', []):
                if isinstance(key, basestring):
                    key = {'name': '{item_type}:' + key,
                           'value': '{%s}' % key, 'templated': True}
                self.merged_keys.append(key)


class Item(object):
    __metaclass__ = MergedLinksMeta
    keys = []
    embedded = {}
    links = {
        'self': {'href': '{collection_uri}{_uuid}', 'templated': True},
        'collection': {'href': '{collection_uri}', 'templated': True},
        'profile': {'href': '/profiles/{item_type}.json', 'templated': True},
    }

    def __init__(self, collection, model):
        self.__name__ = model.rid
        self.__parent__ = collection
        self.model = model

    @property
    def properties(self):
        return self.model.statement.object

    def __json__(self, request):
        links = self.expand_links(request)
        if links is None:
            return self.properties
        properties = self.properties.copy()
        properties['_links'] = links
        return properties

    def template_namespace(self, request=None):
        # Expand templated links
        ns = self.properties.copy()
        ns['item_type'] = self.model.predicate
        ns['_uuid'] = self.model.rid
        if request is not None:
            ns['collection_uri'] = request.resource_path(self.__parent__)
            ns['permission'] = permission_checker(self, request)
        return ns

    def expand_links(self, request):
        # Expand templated links
        ns = self.template_namespace(request)
        compiled = ObjectTemplate(self.merged_links)
        links = compiled(ns)
        # Embed resources
        embedded = self.embedded
        for rel, value in links.items():
            if rel not in embedded:
                continue
            if isinstance(value, list):
                for member in value:
                    embed(request, member['href'])
            else:
                embed(request, value['href'])
        return links

    def create_keys(self):
        session = DBSession()
        ns = self.template_namespace()
        compiled = ObjectTemplate(self.merged_keys)
        keys = compiled(ns)
        for key_spec in keys:
            key = Key(rid=self.model.rid, **key_spec)
            session.add(key)

    @classmethod
    def create(cls, parent, uuid, properties, sheets=None):
        item_type = parent.item_type
        session = DBSession()
        property_sheets = {}
        if properties is not None:
            property_sheets[item_type] = properties
        if sheets is not None:
            property_sheets.update(sheets)
        resource = Resource(property_sheets, uuid)
        session.add(resource)
        model = resource.data[item_type]
        item = cls(parent, model)
        item.create_keys()
        try:
            session.flush()
        except (IntegrityError, FlushError):
            raise HTTPConflict()
        return item

    def update(self, properties, sheets=None):
        if properties is not None:
            self.model.resource[self.model.predicate] = properties
        if sheets is not None:
            for key, value in sheets.items():
                self.model.resource[key] = value


class CustomItemMeta(MergedLinksMeta):
    """ Give each collection its own Item class to enable
        specific view registration.
    """
    def __init__(self, name, bases, attrs):
        super(CustomItemMeta, self).__init__(name, bases, attrs)

        # XXX Remove this, too magical.
        if self.item_type is None and 'item_type' not in attrs:
            self.item_type = self.__name__.lower()

        if 'Item' in attrs:
            assert 'item_links' not in attrs
            assert 'item_embedded' not in attrs
            assert 'item_keys' not in attrs
            return
        item_bases = tuple(base.Item for base in bases
                           if issubclass(base, Collection))
        qualname = getattr(self, '__qualname__', self.__name__)  # PY3 only
        item_attrs = {
            '__module__': self.__module__,
            '__name__': 'Item',
            '__qualname__': qualname + '.Item',
        }
        if 'item_links' in attrs:
            item_attrs['links'] = attrs['item_links']
        if 'item_embedded' in attrs:
            item_attrs['embedded'] = attrs['item_embedded']
        if 'item_keys' in attrs:
            item_attrs['keys'] = attrs['item_keys']
        self.Item = type('Item', item_bases, item_attrs)


class Collection(object):
    __metaclass__ = CustomItemMeta
    Item = Item
    schema = None
    properties = {}
    item_type = None
    links = {
        'self': {'href': '{collection_uri}', 'templated': True},
        'items': [{
            'href': '{item_uri}',
            'templated': True,
            'repeat': 'item_uri item_uris',
        }],
        'actions': [
            {
                'name': 'add',
                'title': 'Add',
                'profile': '/profiles/{item_type}.json',
                'method': 'POST',
                'href': '',
                'templated': True,
                'condition': 'permission:add',
            },
        ],
    }

    def __init__(self, parent, name):
        self.__name__ = name
        self.__parent__ = parent

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
            return self.Item(self, model)
        return default

    def add(self, properties):
        uuid = properties.get('_uuid', _marker)
        if uuid is _marker:
            uuid = uuid4()
        else:
            properties = properties.copy()
            del properties['_uuid']
        item = self.Item.create(self, uuid, properties)
        self.after_add(item)
        return item

    def after_add(self, item):
        '''Hook for subclasses'''

    def __json__(self, request):
        nrows = request.params.get('limit', None)
        session = DBSession()
        query = session.query(CurrentStatement).filter(
            CurrentStatement.predicate == self.item_type
        ).limit(nrows)

        item_uris = []
        for model in query.all():
            item_uri = request.resource_path(self, model.rid)
            embed(request, item_uri)
            item_uris.append(item_uri)

        properties = self.properties.copy()

        # Expand templated links
        ns = properties.copy()
        ns['collection_uri'] = request.resource_path(self)
        ns['item_type'] = self.item_type
        ns['item_uris'] = item_uris
        ns['permission'] = permission_checker(self, request)
        compiled = ObjectTemplate(self.merged_links)
        links = compiled(ns)
        if links is not None:
            properties['_links'] = links

        return properties


@view_config(context=Collection, permission='list', request_method='GET')
def collection_list(context, request):
    return item_view(context, request)


@view_config(context=Collection, permission='add', request_method='POST',
             validators=[setting_uuid_permitted, validate_item_content])
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
    ancestors = lineage(request.context)
    next(ancestors)  # skip self
    for resource in reversed(list(ancestors)):
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


@view_config(context=Item, permission='edit', request_method='POST',
             validators=[validate_item_content])
def item_edit(context, request):
    properties = request.validated
    context.update(properties)
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
