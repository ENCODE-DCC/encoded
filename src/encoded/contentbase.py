# See http://docs.pylonsproject.org/projects/pyramid/en/latest/narr/resources.html

import venusian
from pyramid.events import (
    ContextFound,
    subscriber,
)
from pyramid.httpexceptions import (
    HTTPConflict,
    HTTPForbidden,
    HTTPInternalServerError,
    HTTPNotFound,
    HTTPNotModified,
)
from pyramid.interfaces import (
    PHASE1_CONFIG,
    PHASE2_CONFIG,
)
from pyramid.location import lineage
from pyramid.security import (
    ALL_PERMISSIONS,
    Allow,
    Authenticated,
    Deny,
    Everyone,
    authenticated_userid,
    has_permission,
)
from pyramid.settings import asbool
from pyramid.threadlocal import (
    manager,
)
from pyramid.view import view_config
from sqlalchemy import (
    func,
    orm,
)
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import FlushError
from urllib import (
    quote,
    unquote,
)
from uuid import (
    UUID,
    uuid4,
)
from .objtemplate import ObjectTemplate
from .schema_utils import validate_request
from .storage import (
    DBSession,
    CurrentPropertySheet,
    Resource,
    Key,
    Link,
    TransactionRecord,
)
from collections import OrderedDict
from .validation import ValidationFailure
LOCATION_ROOT = __name__ + ':location_root'
_marker = object()


def includeme(config):
    config.scan(__name__)
    config.set_root_factory(root_factory)


def root_factory(request):
    return request.registry[LOCATION_ROOT]


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


def validate_item_content(context, request):
    data = request.json
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


def uncamel(string):
    """ CamelCase -> camel_case
    """
    out = ''
    before = ''
    for char in string:
        if char.isupper() and before.isalnum() and not before.isupper():
            out += '_'
        out += char.lower()
        before = char
    return out


def location_root(factory):
    """ Set the location root
    """

    def set_root(config, factory):
        acl = acl_from_settings(config.registry.settings)
        root = factory(acl)
        config.registry[LOCATION_ROOT] = root

    def callback(scanner, factory_name, factory):
        scanner.config.action(('location_root',), set_root,
                              args=(scanner.config, factory),
                              order=PHASE1_CONFIG)
    venusian.attach(factory, callback, category='pyramid')

    return factory


def location(name, factory=None):
    """ Attach a collection at the location ``name``.

    Use as a decorator on Collection subclasses.
    """

    def set_location(config, name, factory):
        root = config.registry[LOCATION_ROOT]
        root.attach(name, factory)

    def decorate(factory):
        def callback(scanner, factory_name, factory):
            scanner.config.action(('location', name), set_location,
                                  args=(scanner.config, name, factory),
                                  order=PHASE2_CONFIG)
        venusian.attach(factory, callback, category='pyramid')
        return factory

    return decorate


class Root(object):
    __name__ = ''
    __parent__ = None

    def __init__(self, acl=None):
        if acl is not None:
            self.__acl__ = acl
        self.collections = {}
        self.by_item_type = {}

    def __getitem__(self, name):
        return self.collections[name]

    def __setitem__(self, name, value):
        self.collections[name] = value
        self.by_item_type[value.item_type] = value

    def attach(self, name, factory):
        value = factory(self, name)
        self[name] = value

    def __json__(self, request=None):
        return self.properties.copy()


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
                           'value': '{%s}' % key, '$templated': True}
                self.merged_keys.append(key)


class Item(object):
    __metaclass__ = MergedLinksMeta
    keys = []
    embedded = {}
    links = {
        '@id': {'$value': '{item_uri}', '$templated': True},
        # 'collection': '{collection_uri}',
        '@type': [
            {'$value': '{item_type}', '$templated': True},
            'item',
        ],
    }

    def __init__(self, collection, model):
        self.__name__ = model.rid
        self.__parent__ = collection
        self.model = model

    @property
    def item_type(self):
        return self.model.item_type

    @property
    def schema(self):
        return self.__parent__.schema

    @property
    def properties(self):
        return self.model['']

    @property
    def uuid(self):
        return self.model.rid

    def __json__(self, request):
        properties = self.properties.copy()
        links = self.expand_links(request)
        properties.update(links)
        return properties

    def template_namespace(self, request=None):
        # Expand $templated links
        ns = self.properties.copy()
        ns['item_type'] = self.item_type
        ns['uuid'] = self.uuid
        if request is not None:
            ns['collection_uri'] = request.resource_path(self.__parent__)
            ns['item_uri'] = request.resource_path(self)
            ns['permission'] = permission_checker(self, request)
        return ns

    def expand_links(self, request):
        # Expand $templated links
        ns = self.template_namespace(request)
        compiled = ObjectTemplate(self.merged_links)
        return compiled(ns)

    def expand_embedded(self, request, properties):
        embedded = self.embedded
        for name in properties:
            if name not in embedded:
                continue
            value = properties[name]
            if isinstance(value, list):
                properties[name] = [embed(request, member) for member in value]
            else:
                properties[name] = embed(request, value)

    def create_keys(self):
        session = DBSession()
        ns = self.template_namespace()
        compiled = ObjectTemplate(self.merged_keys)
        keys = compiled(ns)
        for key_spec in keys:
            key = Key(rid=self.uuid, **key_spec)
            session.add(key)

    def create_rels(self):
        if self.schema is None:
            return
        session = DBSession()
        properties = self.properties
        source = self.uuid
        _rels = []

        for name, prop in self.schema['properties'].iteritems():
            if 'linkTo' not in prop:
                continue
            targets = properties.get(name, [])
            if not isinstance(targets, list):
                targets = [targets]
            for target in targets:
                _rels.append((name, UUID(target)))

        rels = set(_rels)
        if len(rels) != len(_rels):
            msg = "Duplicate links"
            raise ValidationFailure('body', None, msg)

        for rel, target in rels:
            link = Link(source_rid=source, rel=rel, target_rid=target)
            session.add(link)

    @classmethod
    def create(cls, parent, uuid, properties, sheets=None):
        item_type = parent.item_type
        session = DBSession()
        property_sheets = {}
        if properties is not None:
            property_sheets[''] = properties
        if sheets is not None:
            property_sheets.update(sheets)
        resource = Resource(item_type, property_sheets, uuid)
        session.add(resource)
        item = cls(parent, resource)
        item.create_keys()
        item.create_rels()
        try:
            session.flush()
        except (IntegrityError, FlushError):
            raise HTTPConflict()
        return item

    def update_keys(self):
        session = DBSession()
        ns = self.template_namespace()
        compiled = ObjectTemplate(self.merged_keys)
        _keys = [(key['name'], key['value']) for key in compiled(ns)]
        keys = set(_keys)

        if len(keys) != len(_keys):
            msg = "Duplicate keys"
            raise ValidationFailure('body', None, msg)

        existing = {
            (key.name, key.value)
            for key in self.model.unique_keys
        }

        to_remove = existing - keys
        to_add = keys - existing

        for pk in to_remove:
            key = session.query(Key).get(pk)
            session.delete(key)

        for name, value in to_add:
            key = Key(rid=self.uuid, name=name, value=value)
            session.add(key)

    def update_rels(self):
        if self.schema is None:
            return
        session = DBSession()
        properties = self.properties
        source = self.uuid
        _rels = []

        for name, prop in self.schema['properties'].iteritems():
            if 'linkTo' not in prop:
                continue
            targets = properties.get(name, [])
            if not isinstance(targets, list):
                targets = [targets]
            for target in targets:
                _rels.append((name, UUID(target)))

        rels = set(_rels)
        if len(rels) != len(_rels):
            msg = "Duplicate links"
            raise ValidationFailure('body', None, msg)

        existing = {
            (link.rel, link.target_rid)
            for link in self.model.rels
        }

        to_remove = existing - rels
        to_add = rels - existing

        for rel, target in to_remove:
            link = session.query(Link).get((source, rel, target))
            session.delete(link)

        for rel, target in to_add:
            link = Link(source_rid=source, rel=rel, target_rid=target)
            session.add(link)

    def update(self, properties, sheets=None):
        if properties is not None:
            self.model[''] = properties
        if sheets is not None:
            for key, value in sheets.items():
                self.model[key] = value
        session = DBSession()
        try:
            self.update_keys()
            self.update_rels()
            session.flush()
        except (IntegrityError, FlushError):
            raise HTTPConflict()


class CustomItemMeta(MergedLinksMeta):
    """ Give each collection its own Item class to enable
        specific view registration.
    """
    def __init__(self, name, bases, attrs):
        super(CustomItemMeta, self).__init__(name, bases, attrs)

        # XXX Remove this, too magical.
        if self.item_type is None and 'item_type' not in attrs:
            self.item_type = uncamel(self.__name__)

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
    properties = OrderedDict()
    item_type = None
    unique_key = None
    columns = {}
    links = {
        '@id': {'$value': '{collection_uri}', '$templated': True},
        '@type': [
            {'$value': '{item_type}_collection', '$templated': True},
            'collection',
        ],
        'all': {'$value': '{collection_uri}?limit=all', '$templated': True},
        'actions': [
            {
                'name': 'add',
                'title': 'Add',
                'profile': '/profiles/{item_type}.json',
                'method': 'POST',
                'href': '',
                '$templated': True,
                'condition': 'permission:add',
            },
        ],
    }

    def __init__(self, parent, name):
        self.__name__ = name
        self.__parent__ = parent

        self.embedded_paths = set()
        for column in self.columns:
            path = tuple(
                name for name in column.split('.')[:-1]
                if name not in ('length', '0')
            )
            self.embedded_paths.add(path)

    def __getitem__(self, name):
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
        try:
            uuid = UUID(name)
        except ValueError:
            return self.get_by_name(name, default)
        else:
            return self.get_by_uuid(uuid, default)

    def get_by_uuid(self, uuid, default=None):
        session = DBSession()
        #if (Resource, (uuid,)) not in session.identity_map:
        #    print 'Uncached %s/%s' % (self.item_type, uuid)
        model = session.query(Resource).get(uuid)
        if model is None:
            return default
        if model.item_type != self.item_type:
            return None
        return self.Item(self, model)

    def get_by_name(self, name, default=None):
        if self.unique_key is None:
            return default
        pkey = (self.unique_key, name)
        session = DBSession()
        # Eager load related resources here.
        key = session.query(Key).options(
            orm.joinedload_all(
                Key.resource,
                Resource.data,
                CurrentPropertySheet.propsheet,
                innerjoin=True,
            ),
            orm.joinedload_all(
                Key.resource,
                Resource.rels,
                Link.target,
                Resource.data,
                CurrentPropertySheet.propsheet,
            ),
        ).get(pkey)
        if key is None:
            return default
        model = key.resource
        return self.Item(self, model)

    def add(self, properties):
        uuid = properties.get('uuid', _marker)
        if uuid is _marker:
            uuid = uuid4()
        else:
            properties = properties.copy()
            del properties['uuid']
        item = self.Item.create(self, uuid, properties)
        self.after_add(item)
        return item

    def after_add(self, item):
        '''Hook for subclasses'''

    def __json__(self, request):
        limit = request.params.get('limit', 30)
        if limit in ('', 'all'):
            limit = None
        if limit is not None:
            limit = int(limit)
        session = DBSession()
        query = session.query(Resource).filter(
            Resource.item_type == self.item_type
        )

        properties = self.properties.copy()
        properties['count'] = query.count()
        # Expand $templated links
        ns = properties.copy()
        ns['collection_uri'] = request.resource_path(self)
        ns['item_type'] = self.item_type
        ns['permission'] = permission_checker(self, request)
        compiled = ObjectTemplate(self.merged_links)
        links = compiled(ns)
        properties.update(links)
        items = properties['items'] = []
        properties['columns'] = self.columns

        query = query.options(
            orm.joinedload_all(
                Resource.rels,
                Link.target,
                Resource.data,
                CurrentPropertySheet.propsheet,
            ),
        )

        for model in query.limit(limit).all():
            item_uri = request.resource_path(self, model.rid)
            rendered = embed(request, item_uri + '?embed=false')

            for path in self.embedded_paths:
                expand_path(request, rendered, path)

            if not self.columns:
                items.append(rendered)
                continue

            subset = {
                '@id': rendered['@id'],
                '@type': rendered['@type'],
            }
            for column in self.columns:
                subset[column] = column_value(rendered, column)

            items.append(subset)
            

        return properties

    def expand_embedded(self, request, properties):
        pass


def column_value(obj, column):
    path = column.split('.')
    value = obj
    for name in path:
        # Hardcoding few lines here should be gone with ES
        if name == 'length':
            return len(value)
        elif name == '0':
            if not value:
                return ''
            value = value[0]
        else:
            value = value.get(name, None)
            if value is None:
                return ''
    return value


def expand_path(request, obj, path):
    if not path:
        return
    name = path[0]
    remaining = path[1:]
    value = obj[name]
    if isinstance(value, list):
        for index, member in enumerate(value):
            if not isinstance(member, dict):
                member = value[index] = embed(request, member + '?embed=false')
            expand_path(request, member, remaining)
    else:
        if not isinstance(value, dict):
            value = obj[name] = embed(request, value + '?embed=false')
        expand_path(request, value, remaining)


def etag_conditional(view_callable):
    """ ETag conditional GET support

    Returns 304 Not Modified when the last transaction id, server process id,
    format and userid all match.

    This might not be strictly correct due to MVCC visibility on postgres.
    Perhaps use ``select txid_current_snapshot();`` instead there.
    """
    def wrapped(context, request):
        if len(manager.stack) != 1:
            return view_callable(context, request)
        format = request.environ.get('encoded.format', 'html')
        if format == 'html':
            last_tid = None
        else:
            session = DBSession()
            last_tid = session.query(func.max(TransactionRecord.order)).scalar()
        processid = request.registry['encoded.processid']
        userid = authenticated_userid(request) or ''
        etag = u'%s;%s;%s;%s' % (last_tid, processid, format, userid)
        etag = quote(etag.encode('utf-8'), ';:@')
        if etag in request.if_none_match:
            raise HTTPNotModified()
        result = view_callable(context, request)
        request.response.etag = etag
        cache_control = request.response.cache_control
        cache_control.private = True
        cache_control.max_age = 0
        cache_control.must_revalidate = True
        return result

    return wrapped


@view_config(context=Collection, permission='list', request_method='GET',
             decorator=etag_conditional)
def collection_list(context, request):
    return item_view(context, request)


@view_config(context=Collection, permission='add', request_method='POST',
             validators=[validate_item_content])
def collection_add(context, request):
    properties = request.validated
    item = context.add(properties)
    item_uri = request.resource_path(item)
    request.response.status = 201
    request.response.location = item_uri
    result = {
        'status': 'success',
        '@type': ['result'],
        'items': [item_uri],
    }
    return result


@subscriber(ContextFound)
def traversal_security(event):
    """ Check traversal was permitted at each step
    """
    request = event.request
    traversed = reversed(list(lineage(request.context)))
    # Required to view the root page as anonymous user
    # XXX Needs test once login based browser tests work.
    next(traversed)  # Skip root object
    for resource in traversed:
        result = has_permission('traverse', resource, request)
        if not result:
            msg = 'Unauthorized: traversal failed permission check'
            raise HTTPForbidden(msg, result=result)


@view_config(context=Item, permission='view', request_method='GET',
             decorator=etag_conditional)
def item_view(context, request):
    properties = context.__json__(request)
    if asbool(request.params.get('embed', True)):
        context.expand_embedded(request, properties)
    return properties


@view_config(context=Item, permission='edit', request_method='POST',
             validators=[validate_item_content])
def item_edit(context, request):
    properties = request.validated
    context.update(properties)
    item_uri = request.resource_path(context)
    request.response.status = 200
    result = {
        'status': 'success',
        '@type': ['result'],
        'items': [item_uri],
    }
    return result
