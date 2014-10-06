# See http://docs.pylonsproject.org/projects/pyramid/en/latest/narr/resources.html
import logging
import venusian
from abc import ABCMeta
from collections import Mapping
from copy import deepcopy
from itertools import islice
from pyramid.events import (
    ContextFound,
    subscriber,
)
from pyramid.httpexceptions import (
    HTTPConflict,
    HTTPForbidden,
    HTTPInternalServerError,
    HTTPPreconditionFailed,
)
from pyramid.interfaces import (
    PHASE2_CONFIG,
)
from pyramid.location import lineage
from pyramid.security import (
    ALL_PERMISSIONS,
    Allow,
    Authenticated,
    Deny,
    Everyone,
    has_permission,
    principals_allowed_by_permission,
)
from pyramid.settings import asbool
from pyramid.traversal import (
    find_root,
    resource_path,
)
from pyramid.view import view_config
from sqlalchemy import (
    orm,
)
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import FlushError
from urllib import urlencode
from uuid import (
    UUID,
    uuid4,
)
from .cache import ManagerLRUCache
from .objtemplate import ObjectTemplate
from .renderers import embed
from .schema_formats import is_accession
from .schema_utils import validate_request
from .storage import (
    DBSession,
    CurrentPropertySheet,
    Resource,
    Key,
    Link,
)
from collections import (
    OrderedDict,
    defaultdict,
)
from .validation import ValidationFailure

PHASE1_5_CONFIG = -15


LOCATION_ROOT = __name__ + ':location_root'
_marker = object()

logger = logging.getLogger(__name__)


def includeme(config):
    config.scan(__name__)
    config.set_root_factory(root_factory)


def root_factory(request):
    return request.registry[LOCATION_ROOT]


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
    schema = context.schema
    if schema is None:
        request.validated.update(data)
        return
    validate_request(schema, request, data)


def validate_item_content_put(context, request):
    data = request.json
    schema = context.schema
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
    schema = context.schema
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
        root = factory(config.registry, acl)
        config.registry[LOCATION_ROOT] = root

    def callback(scanner, factory_name, factory):
        scanner.config.action(('location_root',), set_root,
                              args=(scanner.config, factory),
                              order=PHASE1_5_CONFIG)
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
    builtin_acl = [
        (Allow, 'remoteuser.INDEXER', ('view', 'list', 'traverse', 'index')),
        (Allow, 'remoteuser.EMBED', ('view', 'traverse')),
    ]

    def __init__(self, registry, acl=None):
        self.registry = registry
        if acl is None:
            acl = []
        self.__acl__ = acl + self.builtin_acl
        self.collections = {}
        self.by_item_type = {}
        self.item_cache = ManagerLRUCache('encoded_item_cache', 1000)
        self.unique_key_cache = ManagerLRUCache('encoded_key_cache', 1000)
        self.all_merged_rev = set()

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
        resource = self.by_item_type.get(name, None)
        if resource is not None:
            return resource
        resource = self.get_by_uuid(name, None)
        if resource is not None:
            return resource
        resource = self.get_by_unique_key('page:location', name)
        if resource is not None:
            return resource
        if is_accession(name):
            resource = self.get_by_unique_key('accession', name)
            if resource is not None:
                return resource
        if ':' in name:
            resource = self.get_by_unique_key('alias', name)
            if resource is not None:
                return resource
        return default

    def __setitem__(self, name, value):
        self.collections[name] = value
        self.by_item_type[value.item_type] = value

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

        session = DBSession()
        model = session.query(Resource).get(uuid)
        if model is None:
            return default
        collection = self.by_item_type[model.item_type]
        item = collection.Item(collection, model)
        self.item_cache[uuid] = item
        return item

    def get_by_unique_key(self, unique_key, name, default=None):
        pkey = (unique_key, name)

        cached = self.unique_key_cache.get(pkey)
        if cached is not None:
            return self.get_by_uuid(cached)

        session = DBSession()
        key = session.query(Key).options(
            orm.joinedload_all(
                Key.resource,
                Resource.data,
                CurrentPropertySheet.propsheet,
                innerjoin=True,
            ),
        ).get(pkey)
        if key is None:
            return default
        model = key.resource

        uuid = model.rid
        self.unique_key_cache[pkey] = uuid
        cached = self.item_cache.get(uuid)
        if cached is not None:
            return cached

        collection = self.by_item_type[model.item_type]
        item = collection.Item(collection, model)
        self.item_cache[uuid] = item
        return item

    def attach(self, name, factory):
        value = factory(self, name)
        self[name] = value
        self.all_merged_rev.update(value.Item.merged_rev.values())

    def __json__(self, request=None):
        return self.properties.copy()


class MergedDictsMeta(type):
    """ Merge dicts on the subclass with its bases
    """
    def __init__(self, name, bases, attrs):
        super(MergedDictsMeta, self).__init__(name, bases, attrs)
        for attr in self.__merged_dicts__:
            merged = {}
            setattr(self, 'merged_%s' % attr, merged)

            for cls in reversed(self.mro()):
                value = vars(cls).get(attr, None)
                if value is not None:
                    merged.update(value)


class MergedKeysMeta(MergedDictsMeta):
    """ Merge the keys from the subclass with its bases
    """
    def __init__(self, name, bases, attrs):
        super(MergedKeysMeta, self).__init__(name, bases, attrs)

        self.merged_keys = []
        for cls in reversed(self.mro()):
            for key in vars(cls).get('keys', []):
                if isinstance(key, basestring):
                    key = {'name': '{item_type}:' + key,
                           'value': '{%s}' % key, '$templated': True}
                self.merged_keys.append(key)


class Item(object):
    __metaclass__ = MergedKeysMeta
    __merged_dicts__ = [
        'template',
        'rev',
        'namespace_from_path',
    ]
    base_types = ['item']
    keys = []
    name_key = None
    rev = None
    embedded = ()
    namespace_from_path = {}
    template = {
        '@id': {'$value': '{item_uri}', '$templated': True},
        # 'collection': '{collection_uri}',
        '@type': [
            {'$value': '{item_type}', '$templated': True},
            {'$value': '{base}', '$repeat': 'base base_types', '$templated': True},
        ],
        'uuid': {'$value': '{uuid}', '$templated': True},
    }
    actions = []

    def __init__(self, collection, model):
        self.collection = collection
        self.model = model

    def __repr__(self):
        return '<%s at %s>' % (type(self).__name__, resource_path(self))

    @property
    def __parent__(self):
        return self.collection

    @property
    def __name__(self):
        if self.name_key is None:
            return self.uuid
        return self.properties.get(self.name_key, None) or self.uuid

    @property
    def item_type(self):
        return self.model.item_type

    @property
    def schema(self):
        return self.collection.schema

    @property
    def schema_version(self):
        return self.collection.schema_version

    @property
    def properties(self):
        return self.model['']

    @property
    def propsheets(self):
        return self.model

    @property
    def uuid(self):
        return self.model.rid

    @property
    def schema_links(self):
        return self.collection.schema_links

    def links(self, properties):
        # This works from the schema rather than the links table
        # so that upgrade on GET can work.
        if self.schema is None:
            return {}
        root = find_root(self)
        links = {}
        for name in self.schema_links:
            value = properties.get(name, None)
            if value is None:
                continue
            if isinstance(value, list):
                links[name] = [root.get_by_uuid(v) for v in value]
            else:
                links[name] = root.get_by_uuid(value)
        return links

    def rev_links(self):
        root = find_root(self)
        links = {}
        for name, spec in self.merged_rev.iteritems():
            links[name] = value = []
            for link in self.model.revs:
                if (link.source.item_type, link.rel) == spec:
                    item = root.get_by_uuid(link.source_rid)
                    value.append(item)
        return links

    def upgrade_properties(self, finalize=True):
        properties = self.properties.copy()
        current_version = properties.get('schema_version', '')
        target_version = self.schema_version
        if target_version is not None and current_version != target_version:
            root = find_root(self)
            migrator = root.registry['migrator']
            try:
                properties = migrator.upgrade(
                    self.item_type, properties, current_version, target_version,
                    finalize=finalize, context=self, registry=root.registry)
            except RuntimeError:
                raise
            except Exception:
                logger.warning(
                    'Unable to upgrade %s from %r to %r',
                    resource_path(self.__parent__, self.uuid),
                    current_version, target_version, exc_info=True)
        return properties

    def __json__(self, request):
        """ Render json structure

        1. Fetch stored properties, possibly upgrading.
        2. Link canonicalization (overwriting uuids).
        3. Fill reverse links (Item.rev)
        4. Templated properties

        Embedding is the responsibility of the view.
        """
        properties = self.upgrade_properties()

        for name, value in self.links(properties).iteritems():
            # XXXX Should this be {'@id': url, '@type': [...]} instead?
            if isinstance(value, list):
                properties[name] = [request.resource_path(item) for item in value]
            else:
                properties[name] = request.resource_path(value)

        templated = self.expand_template(properties, request)
        properties.update(templated)

        return properties

    def template_namespace(self, properties, request=None):
        ns = properties.copy()
        ns['properties'] = properties
        ns['item_type'] = self.item_type
        ns['base_types'] = self.base_types
        ns['uuid'] = self.uuid
        ns['root'] = root = find_root(self)
        ns['context'] = self
        ns['registry'] = root.registry
        ns['collection_uri'] = resource_path(self.__parent__, '')
        ns['item_uri'] = resource_path(self, '')

        # When called by update_keys() there is no request.
        if request is not None:
            ns['request'] = request
            ns['permission'] = permission_checker(self, request)

        for name, value in self.rev_links().iteritems():
            ns[name] = [resource_path(item, '') for item in value]

        if self.merged_namespace_from_path:
            root = find_root(self)
            for name, paths in self.merged_namespace_from_path.items():
                # Treat a list of paths as a search path for the value
                if isinstance(paths, basestring):
                    paths = [paths]
                for path in paths:
                    path = path.split('.')
                    last = path[-1]
                    obj = self
                    obj_props = obj.upgrade_properties(finalize=False)
                    for n in path[:-1]:
                        if n not in obj_props:
                            break
                        obj = root.get_by_uuid(obj_props[n])
                        obj_props = obj.upgrade_properties(finalize=False)
                    else:
                        if last in obj_props:
                            ns[name] = deepcopy(obj_props[last])
                            break

        return ns

    def expand_template(self, properties, request):
        ns = self.template_namespace(properties, request)
        compiled = ObjectTemplate(self.merged_template)
        return compiled(ns)

    def expand_embedded(self, request, properties):
        if self.schema is None:
            return
        paths = [p.split('.') for p in self.embedded]
        for path in paths:
            expand_path(request, properties, path)

    @classmethod
    def expand_page(cls, request, properties):
        return properties

    def add_actions(self, request, properties):
        if request.has_permission('edit', self):
            properties['actions'] = getattr(self, 'actions', [])
        else:
            properties['actions'] = []

    @classmethod
    def create(cls, parent, uuid, properties, sheets=None):
        item_type = parent.item_type
        session = DBSession()
        sp = session.begin_nested()
        resource = Resource(item_type, rid=uuid)
        cls.update_properties(resource, properties, sheets)
        session.add(resource)
        self = cls(parent, resource)
        keys_add, keys_remove = self.update_keys()
        self.update_rels()
        try:
            sp.commit()
        except (IntegrityError, FlushError):
            sp.rollback()
        else:
            return self

        # Try again more carefully
        cls.update_properties(resource, properties, sheets)
        session.add(resource)
        self = cls(parent, resource)
        try:
            session.flush()
        except (IntegrityError, FlushError):
            msg = 'UUID conflict'
            raise HTTPConflict(msg)
        conflicts = self.check_duplicate_keys(keys_add)
        self.update_properties(properties, sheets)
        assert conflicts
        msg = 'Keys conflict: %r' % conflicts
        raise HTTPConflict(msg)

    @classmethod
    def update_properties(cls, model, properties, sheets=None):
        if properties is not None:
            if 'uuid' in properties:
                properties = properties.copy()
                del properties['uuid']
            model[''] = properties
        if sheets is not None:
            for key, value in sheets.items():
                model[key] = value

    def update(self, properties, sheets=None):
        session = DBSession()
        sp = session.begin_nested()
        self.update_properties(self.model, properties, sheets)
        keys_add, keys_remove = self.update_keys()
        self.update_rels()
        try:
            sp.commit()
        except (IntegrityError, FlushError):
            sp.rollback()
        else:
            return

        # Try again more carefully
        self.update_properties(self.model, properties, sheets)
        try:
            session.flush()
        except (IntegrityError, FlushError):
            msg = 'Properties conflict'
            raise HTTPConflict(msg)
        conflicts = self.check_duplicate_keys(keys_add)
        self.update_properties(self.model, properties, sheets)
        assert conflicts
        msg = 'Keys conflict: %r' % conflicts
        raise HTTPConflict(msg)

    def update_keys(self):
        session = DBSession()
        ns = self.template_namespace(self.properties)
        compiled = ObjectTemplate(self.merged_keys)
        _keys = [(key['name'], key['value']) for key in compiled(ns)]
        keys = set(_keys)

        if len(keys) != len(_keys):
            msg = "Duplicate keys: %r" % _keys
            raise ValidationFailure('body', [], msg)

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

        return to_add, to_remove

    def check_duplicate_keys(self, keys):
        session = DBSession()
        return [pk for pk in keys if session.query(Key).get(pk) is not None]

    def update_rels(self):
        if self.schema is None:
            return
        session = DBSession()
        properties = self.properties
        source = self.uuid
        _rels = []

        for name in self.schema_links:
            targets = properties.get(name, [])
            if not isinstance(targets, list):
                targets = [targets] if targets else []
            for target in targets:
                _rels.append((name, UUID(target)))

        rels = set(_rels)
        if len(rels) != len(_rels):
            msg = "Duplicate links: %r" % _rels
            raise ValidationFailure('body', [], msg)

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

        return to_add, to_remove


class CustomItemMeta(MergedDictsMeta, ABCMeta):
    """ Give each collection its own Item class to enable
        specific view registration.
    """
    def __init__(self, name, bases, attrs):
        super(CustomItemMeta, self).__init__(name, bases, attrs)

        # XXX Remove this, too magical.
        if self.item_type is None and 'item_type' not in attrs:
            self.item_type = uncamel(self.__name__)

        NAMES_TO_TRANSFER = [
            'template',
            'embedded',
            'keys',
            'rev',
            'name_key',
            'namespace_from_path',
            'actions',
        ]

        if 'Item' in attrs:
            for name in NAMES_TO_TRANSFER:
                assert 'item_' + name not in attrs
            return
        item_bases = tuple(base.Item for base in bases
                           if issubclass(base, Collection))
        item_attrs = {'__module__': self.__module__}
        for name in NAMES_TO_TRANSFER:
            if 'item_' + name in attrs:
                item_attrs[name] = attrs['item_' + name]
        self.Item = type('Item', item_bases, item_attrs)


class Collection(Mapping):
    __metaclass__ = CustomItemMeta
    __merged_dicts__ = [
        'template',
    ]
    Item = Item
    schema = None
    schema_version = None
    properties = OrderedDict()
    item_type = None
    unique_key = None
    columns = {}
    template = {
        '@id': {'$value': '{collection_uri}', '$templated': True},
        '@type': [
            {'$value': '{item_type}_collection', '$templated': True},
            'collection',
        ],
    }

    def __init__(self, parent, name):
        self.__name__ = name
        self.__parent__ = parent

        self.embedded_paths = set()
        if self.schema is not None and 'columns' in self.schema:
            for column in self.schema['columns']:
                path = tuple(
                    name for name in column.split('.')[:-1]
                    if name not in ('length', '0')
                )
                if path:
                    self.embedded_paths.add(path)

        if self.schema is not None:
            properties = self.schema['properties']
            self.schema_links = [
                key for key, prop in properties.iteritems()
                if 'linkTo' in prop or 'linkTo' in prop.get('items', ())
            ]
            self.schema_version = properties.get('schema_version', {}).get('default')

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
        session = DBSession()
        query = session.query(Resource.rid).filter(
            Resource.item_type == self.item_type
        ).order_by(Resource.rid)

        for rid, in query.yield_per(batchsize):
            yield rid

    def __len__(self):
        session = DBSession()
        query = session.query(Resource.rid).filter(
            Resource.item_type == self.item_type
        )
        return query.count()

    def get(self, name, default=None):
        root = find_root(self)
        resource = root.get_by_uuid(name, None)
        if resource is not None:
            if resource.collection is not self and resource.__parent__ is not self:
                return default
            return resource
        if is_accession(name):
            resource = root.get_by_unique_key('accession', name)
            if resource is not None:
                if resource.collection is not self and resource.__parent__ is not self:
                    return default
                return resource
        if ':' in name:
            resource = root.get_by_unique_key('alias', name)
            if resource is not None:
                if resource.collection is not self and resource.__parent__ is not self:
                    return default
                return resource
        if self.unique_key is not None:
            resource = root.get_by_unique_key(self.unique_key, name)
            if resource is not None:
                if resource.collection is not self and resource.__parent__ is not self:
                    return default
                return resource
        return default

    def add(self, properties):
        uuid = properties.get('uuid', _marker)
        if uuid is _marker:
            uuid = uuid4()
        else:
            uuid = UUID(uuid)
        item = self.Item.create(self, uuid, properties)
        self.after_add(item)
        return item

    def after_add(self, item):
        '''Hook for subclasses'''

    def load_db(self, request):
        result = {}

        frame = request.params.get('frame', 'columns')
        if frame == 'columns':
            if self.schema is not None and 'columns' in self.schema:
                result['columns'] = self.schema['columns']
            else:
                frame = 'object'

        limit = request.params.get('limit', 25)
        if limit in ('', 'all'):
            limit = None
        if limit is not None:
            try:
                limit = int(limit)
            except ValueError:
                limit = 25

        items = (
            item for item in self.itervalues()
            if request.has_permission('view', item)
        )

        if limit is not None:
            items = islice(items, limit)

        result['@graph'] = [self._render_item(request, item, frame) for item in items]

        if limit is not None and len(result['@graph']) == limit:
            params = [(k, v) for k, v in request.params.items() if k != 'limit']
            params.append(('limit', 'all'))
            result['all'] = '%s?%s' % (request.resource_path(self), urlencode(params))

        return result

    def _render_item(self, request, item, frame):
        item_uri = request.resource_path(item)

        if frame != 'embedded':
            item_uri += '?frame=object'

        rendered = embed(request, item_uri)

        if frame != 'columns':
            return rendered

        for path in self.embedded_paths:
            expand_path(request, rendered, path)

        subset = {
            '@id': rendered['@id'],
            '@type': rendered['@type'],
        }
        for column in self.schema['columns']:
            subset[column] = column_value(rendered, column)

        return subset

    def load_es(self, request):
        from .views.search import search
        result = search(self, request, self.item_type)

        if len(result['@graph']) < result['total']:
            params = [(k, v) for k, v in request.params.items() if k != 'limit']
            params.append(('limit', 'all'))
            result['all'] = '%s?%s' % (request.resource_path(self), urlencode(params))

        return result

    def template_namespace(self, properties, request=None):
        ns = properties.copy()
        ns['properties'] = properties
        ns['collection_uri'] = resource_path(self, '')
        ns['item_type'] = self.item_type
        ns['context'] = self
        ns['root'] = root = find_root(self)
        ns['registry'] = root.registry
        if request is not None:
            ns['permission'] = permission_checker(self, request)
            ns['request'] = request
        return ns

    def __json__(self, request):
        properties = self.properties.copy()
        ns = self.template_namespace(properties, request)
        compiled = ObjectTemplate(self.merged_template)
        templated = compiled(ns)
        properties.update(templated)

        uri = ns['collection_uri']
        if request.query_string:
            uri += '?' + request.query_string
        properties['@id'] = uri

        datastore = request.params.get('datastore', None)
        if datastore is None:
            datastore = request.registry.settings.get('collection_datastore', 'database')
        # Switch to change summary page loading options: load_db, load_es
        if datastore == 'elasticsearch':
            result = self.load_es(request)
        else:
            result = self.load_db(request)

        result.update(properties)
        return result

    def expand_embedded(self, request, properties):
        pass

    @classmethod
    def expand_page(cls, request, properties):
        return properties

    def add_actions(self, request, properties):
        pass

    def add_default_page(self, request, properties):
        root = find_root(self)
        default_page = root['pages'].get(self.__name__)
        if default_page is not None:
            properties['default_page'] = item_view(default_page, request)


def column_value(obj, column):
    path = column.split('.')
    value = obj
    for name in path:
        # Hardcoding few lines here should be gone with ES
        if name == 'length':
            return len(value)
        else:
            if isinstance(value, list):
                new_values = []
                for v in value:
                    if name in v:
                        new_values.append(v[name])
                value = new_values
            else:
                value = value.get(name, None)
            if value is None:
                return ''
    if isinstance(value, list):
        value = list(set(value))
    return value


def expand_path(request, obj, path):
    if not path:
        return
    name = path[0]
    remaining = path[1:]
    value = obj.get(name, None)
    if value is None:
        return
    if isinstance(value, list):
        for index, member in enumerate(value):
            if not isinstance(member, dict):
                member = value[index] = embed(request, member + '?frame=object')
            expand_path(request, member, remaining)
    else:
        if not isinstance(value, dict):
            value = obj[name] = embed(request, value + '?frame=object')
        expand_path(request, value, remaining)


def if_match_tid(view_callable):
    """ ETag conditional PUT/PATCH support

    Returns 412 Precondition Failed when etag does not match.
    """
    def wrapped(context, request):
        etag = 'tid:%s' % context.model.data[''].propsheet.tid
        if etag not in request.if_match:
            raise HTTPPreconditionFailed("The resource has changed.")
        return view_callable(context, request)

    return wrapped


@view_config(context=Collection, permission='list', request_method='GET')
def collection_list(context, request):
    return item_view(context, request)


@view_config(context=Collection, permission='add', request_method='POST',
             validators=[validate_item_content_post])
@view_config(context=Collection, permission='add_unvalidated', request_method='POST',
             validators=[no_validate_item_content_post],
             request_param=['validate=false'])
def collection_add(context, request, render=None):
    if render is None:
        render = request.params.get('render', True)
    properties = request.validated
    item = context.add(properties)
    request.registry.notify(Created(item, request))
    if render == 'uuid':
        item_uri = '/%s' % item.uuid
    else:
        item_uri = request.resource_path(item)
    if asbool(render) is True:
        rendered = embed(request, item_uri + '?frame=object', as_user=True)
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


@view_config(context=Item, permission='view', request_method='GET')
def item_view(context, request):
    properties = context.__json__(request)
    frame = request.params.get('frame', None)

    if frame is None:
        if asbool(request.params.get('embed', True)):
            frame = 'page'
        else:
            frame = 'object'

    if frame == 'object':
        return properties

    context.expand_embedded(request, properties)
    if frame == 'embedded':
        return properties

    properties = context.expand_page(request, properties)
    context.add_actions(request, properties)
    if hasattr(context, 'add_default_page'):
        context.add_default_page(request, properties)
    return properties


@view_config(context=Item, permission='view_raw', request_method='GET',
             request_param=['frame=raw'])
def item_view_raw(context, request):
    if asbool(request.params.get('upgrade', True)):
        return context.upgrade_properties()
    return context.properties


@view_config(context=Item, permission='edit', request_method='GET',
             request_param=['frame=edit'])
def item_view_edit(context, request):
    properties = context.upgrade_properties()
    for name, value in context.links(properties).iteritems():
        if isinstance(value, list):
            properties[name] = [request.resource_path(item) for item in value]
        else:
            properties[name] = request.resource_path(value)
    etag = 'tid:%s' % context.model.data[''].propsheet.tid
    request.response.etag = etag
    cache_control = request.response.cache_control
    cache_control.private = True
    cache_control.max_age = 0
    cache_control.must_revalidate = True
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
    properties = request.validated
    # This *sets* the property sheet
    request.registry.notify(BeforeModified(context, request))
    context.update(properties)
    request.registry.notify(AfterModified(context, request))
    if render == 'uuid':
        item_uri = '/%s' % context.uuid
    else:
        item_uri = request.resource_path(context)
    if asbool(render) is True:
        rendered = embed(request, item_uri + '?frame=object', as_user=True)
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


@view_config(context=Item, name='index-data', permission='index', request_method='GET')
def item_index_data(context, request):
    links = defaultdict(list)
    for link in context.model.rels:
        links[link.rel].append(link.target_rid)

    keys = defaultdict(list)
    for key in context.model.unique_keys:
        keys[key.name].append(key.value)

    principals = {}
    for permission in ('view', 'edit'):
        p = principals_allowed_by_permission(context, permission)
        if p is Everyone:
            p = [Everyone]
        principals[permission] = p

    path = resource_path(context)
    paths = {path}
    collection = context.collection

    if collection.unique_key in keys:
        paths.update(
            resource_path(collection, key)
            for key in keys[collection.unique_key])

    for base in (collection, request.root):
        for key_name in ('accession', 'alias'):
            if key_name not in keys:
                continue
            paths.add(resource_path(base, str(context.uuid)))
            paths.update(
                resource_path(base, key)
                for key in keys[key_name])

    embedded = embed(request, path + '/?frame=embedded')
    audit = request.audit(embedded, embedded['@type'], path=path)
    document = {
        'embedded': embedded,
        'object': embed(request, path + '/?frame=object'),
        'links': links,
        'keys': keys,
        'principals_allowed_view': sorted(principals['view']),
        'principals_allowed_edit': sorted(principals['edit']),
        'paths': sorted(paths),
        'audit': audit,
    }

    return document
