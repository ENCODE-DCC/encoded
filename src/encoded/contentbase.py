# See http://docs.pylonsproject.org/projects/pyramid/en/latest/narr/resources.html
import logging
import sys
import venusian
from collections import Mapping
from future.utils import (
    raise_with_traceback,
    itervalues,
)
from itertools import islice
from past.builtins import basestring
from posixpath import join
from pyramid.decorator import reify
from pyramid.exceptions import PredicateMismatch
from pyramid.httpexceptions import (
    HTTPInternalServerError,
    HTTPNotFound,
    HTTPPreconditionFailed,
)
from pyramid.interfaces import (
    PHASE2_CONFIG,
)
from pyramid.security import (
    Allow,
    Everyone,
    principals_allowed_by_permission,
)
from pyramid.settings import asbool
from pyramid.traversal import (
    find_resource,
    find_root,
    resource_path,
)
from pyramid.view import (
    render_view_to_response,
    view_config,
)
from urllib.parse import urlencode
from uuid import (
    UUID,
    uuid4,
)
from .cache import ManagerLRUCache
from .calculated import (
    calculate_properties,
    calculated_property,
)
from .decorator import classreify
from .embedding import (
    embed,
    expand_path,
    make_subrequest,
)
from .schema_utils import validate_request
from .storage import RDBStorage
from collections import (
    defaultdict,
)
from .validation import ValidationFailure

PHASE1_5_CONFIG = -15


ROOT = LOCATION_ROOT = 'root'
TYPES = 'types'
CONNECTION = 'connection'
COLLECTIONS = 'collections'
STORAGE = 'storage'

_marker = object()

logger = logging.getLogger(__name__)


def includeme(config):
    registry = config.registry
    config.scan(__name__)
    registry[COLLECTIONS] = CollectionsTool()
    types = registry[TYPES] = TypesTool()
    storage = registry[STORAGE] = RDBStorage()
    registry[CONNECTION] = Connection(registry, types=types, storage=storage)
    config.set_root_factory(root_factory)


def root_factory(request):
    return request.registry[ROOT]


def aslist(value):
    if isinstance(value, basestring):
        return [value]
    return value


# No-validation validators

def no_validate_item_content_post(context, request):
    data = request.json
    request.validated.update(data)


def no_validate_item_content_put(context, request):
    data = request.json
    if 'uuid' in data:
        if UUID(data['uuid']) != context.uuid:
            msg = 'uuid may not be changed'
            raise ValidationFailure('body', ['uuid'], msg)
    request.validated.update(data)


def no_validate_item_content_patch(context, request):
    data = context.properties.copy()
    data.update(request.json)
    if 'uuid' in data:
        if UUID(data['uuid']) != context.uuid:
            msg = 'uuid may not be changed'
            raise ValidationFailure('body', ['uuid'], msg)
    request.validated.update(data)


# Schema checking validators

def validate_item_content_post(context, request):
    data = request.json
    schema = request.registry['calculated_properties'].schema_for(context.Item)
    if schema is None:
        request.validated.update(data)
        return
    validate_request(schema, request, data)


def validate_item_content_put(context, request):
    data = request.json
    schema = request.registry['calculated_properties'].schema_for(context.__class__)
    if schema is None:
        if 'uuid' in data:
            if UUID(data['uuid']) != context.uuid:
                msg = 'uuid may not be changed'
                raise ValidationFailure('body', ['uuid'], msg)
        request.validated.update(data)
        return

    current = context.upgrade_properties(finalize=False).copy()
    current['uuid'] = str(context.uuid)
    validate_request(schema, request, data, current)


def validate_item_content_patch(context, request):
    data = context.upgrade_properties(finalize=False).copy()
    if 'schema_version' in data:
        del data['schema_version']
    data.update(request.json)
    schema = request.registry['calculated_properties'].schema_for(context.__class__)
    if schema is None:
        if 'uuid' in data:
            if UUID(data['uuid']) != context.uuid:
                msg = 'uuid may not be changed'
                raise ValidationFailure('body', ['uuid'], msg)
        request.validated.update(data)
        return
    current = context.upgrade_properties(finalize=False).copy()
    current['uuid'] = str(context.uuid)
    validate_request(schema, request, data, current)


def permission_checker(context, request):
    def checker(permission):
        return request.has_permission(permission, context)
    return checker


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
        registry[TYPES].register(Item.item_type, Item)
        collection = Collection(registry, name, Item.item_type, **kw)
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


class CollectionsTool(dict):
    def __init__(self):
        self.by_item_type = {}

    def register(self, name, value):
        self[name] = value
        self[value.item_type] = value
        self.by_item_type[value.item_type] = value


class TypesTool(object):
    def __init__(self):
        self.types = {}
        self.type_back_rev = {}

    def register(self, item_type, factory):
        self.types[item_type] = factory

        # Calculate the reverse rev map
        for prop_name, spec in factory.rev.items():
            rev_item_type, rel = spec
            back = self.type_back_rev.setdefault(rev_item_type, {}).setdefault(rel, set())
            back.add((item_type, prop_name))

    def __getitem__(self, name):
        return self.types[name]


class Connection(object):
    ''' Intermediates between the storage and the rest of the system
    '''
    def __init__(self, registry, types, storage):
        self.registry = registry
        self.types = types
        self.storage = storage
        self.item_cache = ManagerLRUCache('encoded_item_cache', 1000)
        self.unique_key_cache = ManagerLRUCache('encoded_key_cache', 1000)

    def get_by_uuid(self, uuid, default=None):
        if isinstance(uuid, basestring):
            try:
                uuid = UUID(uuid)
            except ValueError:
                return default
        elif not isinstance(uuid, UUID):
            raise TypeError(uuid)

        cached = self.item_cache.get(uuid)
        if cached is not None:
            return cached

        model = self.storage.get_by_uuid(uuid)
        if model is None:
            return default

        Item = self.types[model.item_type]
        item = Item(self.registry, model)
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

        uuid = model.rid
        self.unique_key_cache[pkey] = uuid
        cached = self.item_cache.get(uuid)
        if cached is not None:
            return cached

        Item = self.types[model.item_type]
        item = Item(self.registry, model)
        self.item_cache[uuid] = item
        return item

    def __iter__(self, item_type=None, batchsize=1000):
        for uuid in self.storage.__iter__(item_type, batchsize):
            yield uuid

    def __len__(self, item_type=None):
        return self.storage.__len__(item_type)

    def create(self, item_type, uuid):
        return self.storage.create(item_type, uuid)

    def update(self, model, properties, sheets=None, unique_keys=None, links=None):
        self.storage.update(model, properties, sheets, unique_keys, links)


class Root(object):
    __name__ = ''
    __parent__ = None
    __acl__ = [
        (Allow, 'remoteuser.INDEXER', ('view', 'list', 'index')),
        (Allow, 'remoteuser.EMBED', ('view', 'expand', 'audit')),
    ]

    def __init__(self, registry):
        self.registry = registry
        self.collections = registry[COLLECTIONS]
        self.connection = registry[CONNECTION]

        # BBB
        self.get_by_uuid = self.connection.get_by_uuid
        self.by_item_type = self.collections.by_item_type

    def __getitem__(self, name):
        try:
            resource = self.get(name)
        except KeyError:
            # Just in case we get an unexpected KeyError
            # FIXME: exception logging.
            raise HTTPInternalServerError('Traversal raised KeyError')
        if resource is None:
            raise KeyError(name)
        return resource

    def __contains__(self, name):
        return self.get(name, None) is not None

    def get(self, name, default=None):
        resource = self.collections.get(name, None)
        if resource is not None:
            return resource
        resource = self.connection.get_by_uuid(name, None)
        if resource is not None:
            return resource
        return default

    def __json__(self, request=None):
        return self.properties.copy()


class Collection(Mapping):
    properties = {}
    unique_key = None

    def __init__(self, registry, name, item_type, properties=None, acl=None, unique_key=None):
        self.registry = registry
        self.__name__ = name
        self.item_type = item_type
        self.connection = registry[CONNECTION]
        if properties is not None:
            self.properties = properties
        if acl is not None:
            self.__acl__ = acl
        if unique_key is not None:
            self.unique_key = unique_key

    @reify
    def __parent__(self):
        return self.registry[ROOT]

    @reify
    def Item(self):
        types = self.registry[TYPES]
        return types[self.item_type]

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

    def __iter__(self, batchsize=1000):
        for uuid in self.connection.__iter__(self.item_type, batchsize):
            yield uuid

    def __len__(self):
        return self.connection.__len__(self.item_type)

    def get(self, name, default=None):
        resource = self.connection.get_by_uuid(name, None)
        if resource is not None:
            if resource.collection is not self and resource.__parent__ is not self:
                return default
            return resource
        if self.unique_key is not None:
            resource = self.connection.get_by_unique_key(self.unique_key, name)
            if resource is not None:
                if resource.collection is not self and resource.__parent__ is not self:
                    return default
                return resource
        return default

    def __json__(self, request):
        return self.properties.copy()


class Item(object):
    item_type = 'item'
    base_types = ['item']
    name_key = None
    rev = {}
    embedded = ()
    audit_inherit = None
    schema = None
    Collection = Collection

    def __init__(self, registry, model):
        self.registry = registry
        self.model = model

    def __repr__(self):
        return '<%s at %s>' % (type(self).__name__, resource_path(self))

    @reify
    def collection(self):
        collections = self.registry[COLLECTIONS]
        return collections.by_item_type[self.item_type]

    @property
    def __parent__(self):
        return self.collection

    @property
    def __name__(self):
        if self.name_key is None:
            return str(self.uuid)
        return self.properties.get(self.name_key, None) or str(self.uuid)

    @classreify
    def schema_version(cls):
        try:
            return cls.schema['properties']['schema_version']['default']
        except (KeyError, TypeError):
            return None

    @property
    def properties(self):
        return self.model.properties

    @property
    def propsheets(self):
        return self.model.propsheets

    @property
    def uuid(self):
        return self.model.uuid

    @property
    def tid(self):
        return self.model.tid

    @classreify
    def schema_links(cls):
        if not cls.schema:
            return ()
        return [
            key for key, prop in cls.schema['properties'].items()
            if 'linkTo' in prop or 'linkTo' in prop.get('items', ())
        ]

    @property
    def merged_back_rev(self):
        merged = {}
        types = [self.item_type] + self.base_types
        for item_type in reversed(types):
            merged.update(self.registry[TYPES].type_back_rev.get(item_type, ()))
        return merged

    def links(self, properties):
        return {
            name: aslist(properties.get(name, ()))
            for name in self.schema_links
        }

    def rev_links(self):
        links = {}
        for name, spec in self.rev.items():
            links[name] = value = []
            for link in self.model.revs:
                if (link.source.item_type, link.rel) == spec:
                    value.append(link.source_rid)
        return links

    def get_rev_links(self, name):
        spec = self.rev[name]
        return [
            link.source_rid
            for link in self.model.revs
            if (link.source.item_type, link.rel) == spec
        ]

    @classreify
    def schema_keys(cls):
        if not cls.schema:
            return ()
        keys = defaultdict(list)
        for key, prop in cls.schema['properties'].items():
            uniqueKey = prop.get('items', prop).get('uniqueKey')
            if uniqueKey is True:
                uniqueKey = '%s:%s' % (cls.item_type, key)
            if uniqueKey is not None:
                keys[uniqueKey].append(key)
        return keys

    def unique_keys(self, properties):
        return {
            name: [v for prop in props for v in aslist(properties.get(prop, ()))]
            for name, props in self.schema_keys.items()
        }

    def upgrade_properties(self, finalize=True):
        properties = self.properties.copy()
        current_version = properties.get('schema_version', '')
        target_version = self.schema_version
        if target_version is not None and current_version != target_version:
            migrator = self.registry['migrator']
            try:
                properties = migrator.upgrade(
                    self.item_type, properties, current_version, target_version,
                    finalize=finalize, context=self, registry=self.registry)
            except RuntimeError:
                raise
            except Exception:
                logger.warning(
                    'Unable to upgrade %s from %r to %r',
                    resource_path(self.__parent__, self.uuid),
                    current_version, target_version, exc_info=True)
        return properties

    def __json__(self, request):
        # Record embedding objects
        request._embedded_uuids.add(str(self.uuid))
        return self.upgrade_properties()

    def __resource_url__(self, request, info):
        # Record linking objects
        request._linked_uuids.add(str(self.uuid))
        return None

    @classmethod
    def expand_page(cls, request, properties):
        return properties

    @classmethod
    def create(cls, registry, properties, sheets=None):
        if 'uuid' in properties:
            uuid = UUID(properties['uuid'])
        else:
            uuid = uuid4()
        model = registry[CONNECTION].create(cls.item_type, uuid)
        self = cls(registry, model)
        self._update(properties, sheets)
        return self

    def update(self, properties, sheets=None):
        self._update(properties, sheets)

    def _update(self, properties, sheets=None):
        unique_keys = None
        links = None
        if properties is not None:
            if 'uuid' in properties:
                properties = properties.copy()
                del properties['uuid']

            unique_keys = self.unique_keys(properties)
            for k, values in unique_keys.items():
                if len(set(values)) != len(values):
                    msg = "Duplicate keys for %r: %r" % (k, values)
                    raise ValidationFailure('body', [], msg)

            links = self.links(properties)
            for k, values in links.items():
                if len(set(values)) != len(values):
                    msg = "Duplicate links for %r: %r" % (k, values)
                    raise ValidationFailure('body', [], msg)

        connection = self.registry[CONNECTION]
        connection.update(self.model, properties, sheets, unique_keys, links)

    @calculated_property(name='@id', schema={
        "type": "string",
    })
    def jsonld_id(self, request):
        return request.resource_path(self)

    @calculated_property(name='@type', schema={
        "type": "array",
        "items": {
            "type": "string",
        },
    })
    def jsonld_type(self):
        return [self.item_type] + self.base_types

    @calculated_property(name='uuid')
    def prop_uuid(self):
        return str(self.uuid)


def etag_tid(view_callable):
    def wrapped(context, request):
        result = view_callable(context, request)
        root = request.root
        embedded = (root.get_by_uuid(uuid) for uuid in sorted(request._embedded_uuids))
        uuid_tid = ((item.uuid, item.tid) for item in embedded)
        request.response.etag = '&'.join('%s=%s' % (u, t) for u, t in uuid_tid)
        cache_control = request.response.cache_control
        cache_control.private = True
        cache_control.max_age = 0
        cache_control.must_revalidate = True
        return result

    return wrapped


def if_match_tid(view_callable):
    """ ETag conditional PUT/PATCH support

    Returns 412 Precondition Failed when etag does not match.
    """
    def wrapped(context, request):
        if_match = str(request.if_match)
        if if_match == '*':
            return view_callable(context, request)
        uuid_tid = (v.split('=', 1) for v in if_match.strip('"').split('&'))
        root = request.root
        mismatching = (
            root.get_by_uuid(uuid).tid != UUID(tid)
            for uuid, tid in uuid_tid)
        if any(mismatching):
            raise HTTPPreconditionFailed("The resource has changed.")
        return view_callable(context, request)

    return wrapped


def load_db(context, request):
    result = {}

    frame = request.params.get('frame', 'columns')

    limit = request.params.get('limit', 25)
    if limit in ('', 'all'):
        limit = None
    if limit is not None:
        try:
            limit = int(limit)
        except ValueError:
            limit = 25

    items = (
        item for item in itervalues(context)
        if request.has_permission('view', item)
    )

    if limit is not None:
        items = islice(items, limit)

    result['@graph'] = [
        request.embed(request.resource_path(item, '@@' + frame))
        for item in items
    ]

    if limit is not None and len(result['@graph']) == limit:
        params = [(k, v) for k, v in request.params.items() if k != 'limit']
        params.append(('limit', 'all'))
        result['all'] = '%s?%s' % (request.resource_path(context), urlencode(params))

    return result


def load_es(context, request):
    from .views.search import search
    result = search(context, request, context.item_type)

    if len(result['@graph']) < result['total']:
        params = [(k, v) for k, v in request.params.items() if k != 'limit']
        params.append(('limit', 'all'))
        result['all'] = '%s?%s' % (request.resource_path(context), urlencode(params))

    return result


@view_config(context=Collection, permission='list', request_method='GET',
             name='object')
def collection_view_object(context, request):
    uri = request.resource_path(context)
    properties = context.__json__(request)
    properties.update({
        '@id': uri,
        '@type': [
            '{item_type}_collection'.format(item_type=context.item_type),
            'collection',
        ],
    })
    return properties


@view_config(context=Collection, permission='list', request_method='GET')
def collection_list(context, request):
    path = request.resource_path(context)
    properties = request.embed(path, '@@object')

    actions = request.embed(path, '@@actions', as_user=True)['actions']
    if actions:
        properties['actions'] = actions

    if request.query_string:
        properties['@id'] += '?' + request.query_string

    root = find_root(context)
    if context.__name__ in root['pages']:
        properties['default_page'] = embed(
            request, '/pages/%s/@@page' % context.__name__, as_user=True)

    datastore = request.params.get('datastore', None)
    if datastore is None:
        datastore = request.registry.settings.get('collection_datastore', 'database')
    # Switch to change summary page loading options: load_db, load_es
    if datastore == 'elasticsearch':
        result = load_es(context, request)
    else:
        result = load_db(context, request)

    result.update(properties)
    return result


def split_child_props(registry, cls, properties):
    calculated_properties = registry['calculated_properties']
    schema_rev_links = calculated_properties.schema_rev_links_for(cls)
    propname_children = {}
    if schema_rev_links:
        properties = properties.copy()
        for key, spec in schema_rev_links.items():
            if key in properties:
                propname_children[key] = properties.pop(key)
    return properties, propname_children


def update_children(context, request, propname_children):
    registry = request.registry
    root = request.root
    calculated_properties = registry['calculated_properties']
    schema_rev_links = calculated_properties.schema_rev_links_for(type(context))

    for propname, children in propname_children.items():
        link_type, link_attr = spec = schema_rev_links[propname]
        child_collection = root.by_item_type[link_type]
        found = set()

        # Add or update children included in properties
        for i, child_props in enumerate(children):
            if isinstance(child_props, basestring):  # IRI of (existing) child
                child = find_resource(child_collection, child_props)
            else:
                child_props = child_props.copy()
                child_props[link_attr] = str(context.uuid)
                if 'uuid' in child_props:  # update existing child
                    child_id = child_props.pop('uuid')
                    child = root.get_by_uuid(child_id)
                    if not request.has_permission('edit', child):
                        msg = u'edit forbidden to %s' % request.resource_path(child)
                        raise ValidationFailure('body', [propname, i], msg)
                    try:
                        update_item(child, request, child_props)
                    except ValidationFailure as e:
                        e.location = [propname, i] + e.location
                        raise
                else:  # add new child
                    if not request.has_permission('add', child_collection):
                        msg = u'edit forbidden to %s' % request.resource_path(child)
                        raise ValidationFailure('body', [propname, i], msg)
                    child = create_item(child_collection.Item, request, child_props)
            found.add(child.uuid)

        # Remove existing children that are not in properties
        for link in context.model.revs:
            if (link.source.item_type, link.rel) != spec:
                continue
            if link.source_rid in found:
                continue
            child = root.get_by_uuid(link.source_rid)
            if not request.has_permission('edit', child):
                msg = u'edit forbidden to %s' % request.resource_path(child)
                raise ValidationFailure('body', [propname, i], msg)
            child_props = child.properties.copy()
            child_props['status'] = 'deleted'
            try:
                update_item(child, request, child_props)
            except ValidationFailure as e:
                e.location = [propname, i] + e.location
                raise


def create_item(cls, request, properties, sheets=None):
    registry = request.registry
    item_properties, propname_children = split_child_props(
        registry, cls, properties)

    item = cls.create(registry, item_properties, sheets)
    registry.notify(Created(item, request))

    if propname_children:
        update_children(item, request, propname_children)
    return item


def update_item(context, request, properties, sheets=None):
    registry = request.registry
    item_properties, propname_children = split_child_props(
        registry, type(context), properties)

    registry.notify(BeforeModified(context, request))
    context.update(item_properties, sheets)
    registry.notify(AfterModified(context, request))

    if propname_children:
        update_children(context, request, propname_children)


@view_config(context=Collection, permission='add', request_method='POST',
             validators=[validate_item_content_post])
@view_config(context=Collection, permission='add_unvalidated', request_method='POST',
             validators=[no_validate_item_content_post],
             request_param=['validate=false'])
def collection_add(context, request, render=None):
    if render is None:
        render = request.params.get('render', True)

    item = create_item(context.Item, request, request.validated)

    if render == 'uuid':
        item_uri = '/%s/' % item.uuid
    else:
        item_uri = request.resource_path(item)
    if asbool(render) is True:
        rendered = embed(request, join(item_uri, '@@details'), as_user=True)
    else:
        rendered = item_uri
    request.response.status = 201
    request.response.location = item_uri
    result = {
        'status': 'success',
        '@type': ['result'],
        '@graph': [rendered],
    }
    return result


@view_config(context=Item, permission='view', request_method='GET')
def item_view(context, request):
    frame = request.params.get('frame', 'page')
    if getattr(request, '__parent__', None) is None:
        # We need the response headers from non subrequests
        try:
            return render_view_to_response(context, request, name=frame)
        except PredicateMismatch:
            # Avoid this view emitting PredicateMismatch
            exc_class, exc, tb = sys.exc_info()
            exc.__class__ = HTTPNotFound
            raise_with_traceback(exc, tb)
    path = request.resource_path(context, '@@' + frame)
    if request.query_string:

        path += '?' + request.query_string
    return embed(request, path, as_user=True)


def item_links(context, request):
    # This works from the schema rather than the links table
    # so that upgrade on GET can work.
    properties = context.__json__(request)
    root = request.root
    for name in context.schema_links:
        value = properties.get(name, None)
        if value is None:
            continue
        if isinstance(value, list):
            properties[name] = [
                request.resource_path(root.get_by_uuid(v))
                for v in value
            ]
        else:
            properties[name] = request.resource_path(root.get_by_uuid(value))
    return properties


@view_config(context=Item, permission='view', request_method='GET',
             name='object')
@view_config(context=Item, permission='view', request_method='GET',
             name='details')
def item_view_object(context, request):
    """ Render json structure

    1. Fetch stored properties, possibly upgrading.
    2. Link canonicalization (overwriting uuids.)
    3. Calculated properties (including reverse links.)
    """
    properties = item_links(context, request)
    calculated = calculate_properties(context, request, properties)
    properties.update(calculated)
    return properties


@view_config(context=Item, permission='view', request_method='GET',
             name='embedded')
def item_view_embedded(context, request):
    item_path = request.resource_path(context)
    properties = request.embed(item_path, '@@object')
    for path in context.embedded:
        expand_path(request, properties, path)
    return properties


@view_config(context=Item, permission='view', request_method='GET',
             name='actions')
@view_config(context=Collection, permission='list', request_method='GET',
             name='actions')
def item_actions(context, request):
    ns = {
        'has_permission': request.has_permission,
        'item_uri': request.resource_path(context),
        'item_type': context.item_type,
    }
    actions = calculate_properties(context, request, ns, category='action')
    return {
        'actions': list(actions.values()),
    }


@view_config(context=Item, permission='view', request_method='GET',
             name='page')
def item_view_page(context, request):
    item_path = request.resource_path(context)
    properties = request.embed(item_path, '@@embedded')
    actions = request.embed(item_path, '@@actions', as_user=True)['actions']
    if actions:
        properties['actions'] = actions
    if request.has_permission('audit', context):
        properties['audit'] = request.embed(item_path, '@@audit')['audit']
    # XXX Move to view when views on ES results implemented.
    properties = context.expand_page(request, properties)
    return properties


@view_config(context=Item, permission='expand', request_method='GET',
             name='expand')
def item_view_expand(context, request):
    path = request.resource_path(context)
    properties = request.embed(path, '@@object')
    for path in request.params.getall('expand'):
        expand_path(request, properties, path)
    return properties


def expand_column(request, obj, subset, path):
    if isinstance(path, basestring):
        path = path.split('.')
    if not path:
        return
    name = path[0]
    remaining = path[1:]
    value = obj.get(name, None)
    if value is None:
        return
    if not remaining:
        subset[name] = value
        return
    if isinstance(value, list):
        if name not in subset:
            subset[name] = [{} for i in range(len(value))]
        for index, member in enumerate(value):
            if not isinstance(member, dict):
                member = request.embed(member, '@@object')
            expand_column(request, member, subset[name][index], remaining)
    else:
        if name not in subset:
            subset[name] = {}
        if not isinstance(value, dict):
            value = request.embed(value, '@@object')
        expand_column(request, value, subset[name], remaining)


@view_config(context=Item, permission='view', request_method='GET',
             name='columns')
def item_view_columns(context, request):
    path = request.resource_path(context)
    properties = request.embed(path, '@@object')
    if context.schema is None or 'columns' not in context.schema:
        return properties

    subset = {
        '@id': properties['@id'],
        '@type': properties['@type'],
    }

    for column in context.schema['columns']:
        path = column.split('.')
        if path[-1] == 'length':
            path.pop()
        if path:
            expand_column(request, properties, subset, path)

    return subset


@view_config(context=Item, permission='audit', request_method='GET',
             name='audit-self')
def item_view_audit_self(context, request):
    path = request.resource_path(context)
    types = [context.item_type] + context.base_types
    return {
        '@id': path,
        'audit': request.audit(types=types, path=path),
    }


@view_config(context=Item, permission='audit', request_method='GET',
             name='audit')
def item_view_audit(context, request):
    path = request.resource_path(context)
    properties = request.embed(path, '@@object')
    audit = inherit_audits(request, properties, context.audit_inherit or context.embedded)
    return {
        '@id': path,
        'audit': audit,
    }


@view_config(context=Item, permission='view_raw', request_method='GET',
             name='raw')
def item_view_raw(context, request):
    if asbool(request.params.get('upgrade', True)):
        return context.upgrade_properties()
    return context.properties


@view_config(context=Item, permission='edit', request_method='GET',
             name='edit', decorator=etag_tid)
def item_view_edit(context, request):
    properties = item_links(context, request)
    calculated = calculate_properties(context, request, properties)
    calculated_properties = request.registry['calculated_properties']
    schema_rev_links = calculated_properties.schema_rev_links_for(type(context))
    for key, value in calculated.items():
        if key in schema_rev_links:
            properties[key] = value
    return properties


@view_config(context=Item, permission='edit', request_method='PUT',
             validators=[validate_item_content_put], decorator=if_match_tid)
@view_config(context=Item, permission='edit', request_method='PATCH',
             validators=[validate_item_content_patch], decorator=if_match_tid)
@view_config(context=Item, permission='edit_unvalidated', request_method='PUT',
             validators=[no_validate_item_content_put],
             request_param=['validate=false'], decorator=if_match_tid)
@view_config(context=Item, permission='edit_unvalidated', request_method='PATCH',
             validators=[no_validate_item_content_patch],
             request_param=['validate=false'], decorator=if_match_tid)
def item_edit(context, request, render=None):
    """ This handles both PUT and PATCH, difference is the validator

    PUT - replaces the current properties with the new body
    PATCH - updates the current properties with those supplied.
    """
    if render is None:
        render = request.params.get('render', True)

    # This *sets* the property sheet
    update_item(context, request, request.validated)

    if render == 'uuid':
        item_uri = '/%s' % context.uuid
    else:
        item_uri = request.resource_path(context)
    if asbool(render) is True:
        rendered = embed(request, join(item_uri, '@@object'), as_user=True)
    else:
        rendered = item_uri
    request.response.status = 200
    result = {
        'status': 'success',
        '@type': ['result'],
        '@graph': [rendered],
    }
    return result


class Created(object):
    def __init__(self, object, request):
        self.object = object
        self.request = request


class BeforeModified(object):
    def __init__(self, object, request):
        self.object = object
        self.request = request


class AfterModified(object):
    def __init__(self, object, request):
        self.object = object
        self.request = request


def path_ids(request, obj, path):
    if isinstance(path, basestring):
        path = path.split('.')
    if not path:
        yield obj if isinstance(obj, basestring) else obj['@id']
        return
    name = path[0]
    remaining = path[1:]
    value = obj.get(name, None)
    if value is None:
        return
    if isinstance(value, list):
        for member in value:
            if remaining and isinstance(member, basestring):
                member = embed(request, join(member, '@@object'))
            for item_uri in path_ids(request, member, remaining):
                yield item_uri
    else:
        if remaining and isinstance(value, basestring):
            value = embed(request, join(value, '@@object'))
        for item_uri in path_ids(request, value, remaining):
            yield item_uri


def inherit_audits(request, embedded, embedded_paths):
    audit_paths = {embedded['@id']}
    for embedded_path in embedded_paths:
        audit_paths.update(path_ids(request, embedded, embedded_path))

    audits = {}
    for audit_path in audit_paths:
        result = embed(request, join(audit_path, '@@audit-self'))
        for audit in result['audit']:
            if audit['level_name'] in audits:
                audits[audit['level_name']].append(audit)
            else:
                audits[audit['level_name']] = [audit]
    return audits


@view_config(context=Item, name='index-data', permission='index', request_method='GET')
def item_index_data(context, request):
    uuid = str(context.uuid)
    properties = context.upgrade_properties(finalize=False)
    links = context.links(properties)
    unique_keys = context.unique_keys(properties)

    principals_allowed = {}
    for permission in ('view', 'edit', 'audit'):
        p = principals_allowed_by_permission(context, permission)
        if p is Everyone:
            p = [Everyone]
        principals_allowed[permission] = sorted(p)

    path = resource_path(context)
    paths = {path}
    collection = context.collection

    if collection.unique_key in unique_keys:
        paths.update(
            resource_path(collection, key)
            for key in unique_keys[collection.unique_key])

    for base in (collection, request.root):
        for key_name in ('accession', 'alias'):
            if key_name not in unique_keys:
                continue
            paths.add(resource_path(base, uuid))
            paths.update(
                resource_path(base, key)
                for key in unique_keys[key_name])

    path = path + '/'
    embedded = request.embed(path, '@@embedded')
    audit = request.embed(path, '@@audit')['audit']

    document = {
        'uuid': uuid,
        'item_type': context.item_type,
        'embedded': embedded,
        'object': embed(request, join(path, '@@object')),
        'links': links,
        'unique_keys': unique_keys,
        'principals_allowed': principals_allowed,
        'paths': sorted(paths),
        'audit': audit,
        'embedded_uuids': sorted(request._embedded_uuids),
        'linked_uuids': sorted(request._linked_uuids),
    }

    return document
