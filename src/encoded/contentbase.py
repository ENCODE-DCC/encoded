# See http://docs.pylonsproject.org/projects/pyramid/en/latest/narr/resources.html


import logging
import venusian
from abc import ABCMeta
from collections import Mapping
from copy import deepcopy
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
from pyramid.traversal import find_root
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
from .schema_formats import is_accession
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

PHASE1_5_CONFIG = -15


LOCATION_ROOT = __name__ + ':location_root'
_marker = object()

logger = logging.getLogger(__name__)


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
        embedded[path] = deepcopy(result)
        return result
    result = embedded.get(path, None)
    if result is not None:
        return deepcopy(result)
    subreq = make_subrequest(request, path)
    subreq.override_renderer = 'null_renderer'
    try:
        result = request.invoke_subrequest(subreq)
    except HTTPNotFound:
        raise KeyError(path)
    if embedded is not None:
        embedded[path] = deepcopy(result)
    return result


def maybe_include_embedded(request, result):
    if len(manager.stack) != 1:
        return
    embedded = manager.stack[0].get('encoded_embedded', None)
    if embedded:
        result['_embedded'] = {'resources': embedded}


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
    current = context.properties.copy()
    current['uuid'] = str(context.uuid)
    validate_request(schema, request, data, current)


def validate_item_content_patch(context, request):
    data = context.upgrade_properties(request)
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
    current = context.properties.copy()
    current['uuid'] = str(context.uuid)
    validate_request(schema, request, data, current)


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

    def __init__(self, acl=None):
        if acl is not None:
            self.__acl__ = acl
        self.collections = {}
        self.by_item_type = {}

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
        session = DBSession()
        model = session.query(Resource).get(uuid)
        if model is None:
            return default
        collection = self.by_item_type[model.item_type]
        return collection.Item(collection, model)

    def get_by_unique_key(self, unique_key, name, default=None):
        pkey = (unique_key, name)
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
        collection = self.by_item_type[model.item_type]
        return collection.Item(collection, model)

    def attach(self, name, factory):
        value = factory(self, name)
        self[name] = value

    def __json__(self, request=None):
        return self.properties.copy()


class MergedTemplateMeta(type):
    """ Merge the template from the subclass with its bases
    """
    def __init__(self, name, bases, attrs):
        super(MergedTemplateMeta, self).__init__(name, bases, attrs)

        self.merged_template = {}
        for cls in reversed(self.mro()):
            template = vars(cls).get('template', None)
            if template is not None:
                self.merged_template.update(template)


class MergedKeysMeta(MergedTemplateMeta):
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
    base_types = ['item']
    keys = []
    name_key = None
    rev = None
    embedded = ()
    template = {
        '@id': {'$value': '{item_uri}', '$templated': True},
        # 'collection': '{collection_uri}',
        '@type': [
            {'$value': '{item_type}', '$templated': True},
            {'$value': '{base}', '$repeat': 'base base_types', '$templated': True},
        ],
        'uuid': {'$value': '{uuid}', '$templated': True},
    }

    def __init__(self, collection, model):
        self.__parent__ = collection
        self.model = model

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
        return self.__parent__.schema

    @property
    def schema_version(self):
        return self.__parent__.schema_version

    @property
    def properties(self):
        return self.model['']

    @property
    def uuid(self):
        return self.model.rid

    @property
    def schema_links(self):
        return self.__parent__.schema_links

    @property
    def links(self):
        if self.schema is None:
            return {}
        root = find_root(self)
        links = {}
        properties = self.properties
        for name in self.schema_links:
            value = properties.get(name, None)
            if value is None:
                continue
            if isinstance(value, list):
                links[name] = [root.get_by_uuid(v) for v in value]
            else:
                links[name] = root.get_by_uuid(value)
        return links

    @property
    def rev_links(self):
        if self.rev is None:
            return {}
        root = find_root(self)
        links = {}
        for name, spec in self.rev.iteritems():
            item_types, rel = spec
            if isinstance(item_types, basestring):
                item_types = [item_types]
            links[name] = value = []
            for link in self.model.revs:
                if rel == link.rel and link.source.item_type in item_types:
                    item = root.get_by_uuid(link.source_rid)
                    value.append(item)
        return links

    def upgrade_properties(self, request):
        properties = self.properties.copy()
        current_version = properties.get('schema_version', '')
        target_version = self.schema_version
        if target_version is not None and current_version != target_version:
            try:
                properties = request.upgrade(
                    self.item_type, properties, current_version, target_version,
                    context=self)
            except Exception:
                logger.warning('Unable to upgrade %s%s from %r to %r',
                    request.resource_path(self.__parent__), self.uuid,
                    current_version, target_version, exc_info=True)
        return properties

    def __json__(self, request):
        properties = self.upgrade_properties(request)
        templated = self.expand_template(properties, request)
        properties.update(templated)
        for name, value in self.links.iteritems():
            # XXXX Should this be {'@id': url, '@type': [...]} instead?
            if isinstance(value, list):
                properties[name] = [request.resource_path(item) for item in value]
            else:
                properties[name] = request.resource_path(value)
        for name, value in self.rev_links.iteritems():
            properties[name] = [request.resource_path(item) for item in value]
        return properties

    def template_namespace(self, properties, request=None):
        ns = properties.copy()
        ns['item_type'] = self.item_type
        ns['base_types'] = self.base_types
        ns['uuid'] = self.uuid
        # When called by update_keys() there is no request.
        if request is not None:
            ns['collection_uri'] = request.resource_path(self.__parent__)
            ns['item_uri'] = request.resource_path(self)
            ns['permission'] = permission_checker(self, request)
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
                targets = [targets]
            for target in targets:
                _rels.append((name, UUID(target)))

        rels = set(_rels)
        if len(rels) != len(_rels):
            msg = "Duplicate links: %r" % _rels
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

        return to_add, to_remove


class CustomItemMeta(MergedTemplateMeta, ABCMeta):
    """ Give each collection its own Item class to enable
        specific view registration.
    """
    def __init__(self, name, bases, attrs):
        super(CustomItemMeta, self).__init__(name, bases, attrs)

        # XXX Remove this, too magical.
        if self.item_type is None and 'item_type' not in attrs:
            self.item_type = uncamel(self.__name__)

        NAMES_TO_TRANSFER = ['template', 'embedded', 'keys', 'rev', 'name_key']

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
            if path:
                self.embedded_paths.add(path)

        if self.schema is not None:
            properties = self.schema['properties']
            self.schema_links = [
                name for name, prop in properties.iteritems()
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

    def __iter__(self, limit=None):
        session = DBSession()
        query = session.query(Resource.rid).filter(
            Resource.item_type == self.item_type
        )
        for rid, in query.limit(limit):
            yield rid

    def __len__(self):
        session = DBSession()
        query = session.query(Resource.rid).filter(
            Resource.item_type == self.item_type
        )
        return query.count()

    def get(self, name, default=None):
        resource = self.get_by_uuid(name, None)
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
        if self.unique_key is not None:
            resource = self.get_by_unique_key(self.unique_key, name)
            if resource is not None:
                return resource
        return default

    def get_by_uuid(self, uuid, default=None):
        if isinstance(uuid, basestring):
            try:
                uuid = UUID(uuid)
            except ValueError:
                return default
        session = DBSession()
        #if (Resource, (uuid,)) not in session.identity_map:
        #    print 'Uncached %s/%s' % (self.item_type, uuid)
        model = session.query(Resource).get(uuid)
        if model is None:
            return default
        if model.item_type != self.item_type:
            return default
        return self.Item(self, model)

    def get_by_unique_key(self, unique_key, name, default=None):
        pkey = (unique_key, name)
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
        if model.item_type != self.item_type:
            return default
        return self.Item(self, model)

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

    def load_db(self, request, limit=None):
        session = DBSession()
        query = session.query(Resource).filter(
            Resource.item_type == self.item_type
        )

        query = query.options(
            orm.joinedload_all(
                Resource.rels,
                Link.target,
                Resource.data,
                CurrentPropertySheet.propsheet,
            ),
        )
        items = []
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

        return items

    def load_es(self, request):
        columns = ['@id', '@type']
        lengthColumns = []
        for column in self.columns:
            if 'length' in column:
                columns.append(column.split('.')[0])
                lengthColumns.append(column.split('.')[0])
            else:
                columns.append(column)
        # Hack to check if the views have columns for the collection.
        if len(columns) > 2:
            query = {'query': {'match_all': {}}, 'fields': columns}
        else:
            query = {'query': {'match_all': {}}}

        items = []
        from .indexing import ELASTIC_SEARCH
        es = request.registry[ELASTIC_SEARCH]
        results = es.search(query, index=self.item_type, size=99999)
        for model in results['hits']['hits']:
            # Dealing with columns which have length attribute to the array
            for c in lengthColumns:
                model['fields'][c + '.length'] = len(model['fields'][c])
                del model['fields'][c]

            if len(columns) > 2:
                items.append(model['fields'])
            else:
                items.append(model['_source'])
        return items

    def __json__(self, request):
        properties = self.properties.copy()
        ns = properties.copy()
        ns['collection_uri'] = request.resource_path(self)
        ns['item_type'] = self.item_type
        ns['permission'] = permission_checker(self, request)
        compiled = ObjectTemplate(self.merged_template)
        links = compiled(ns)
        properties.update(links)
        properties['columns'] = self.columns
        collection_source = request.params.get('collection_source', None)
        if collection_source is None:
            collection_source = request.registry.settings.get('collection_source', 'database')
        # Switch to change summary page loading options: load_db, load_es
        if collection_source == 'elasticsearch':
            properties['@graph'] = self.load_es(request)
        else:
            limit = request.params.get('limit', 30)
            if limit in ('', 'all'):
                limit = None
            if limit is not None:
                try:
                    limit = int(limit)
                except ValueError:
                    limit = 30
            properties['@graph'] = self.load_db(request, limit)
            if limit is not None:
                properties['all'] = "{collection_uri}?limit=all&collection_source=database".format(**ns)
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
    value = obj.get(name, None)
    if value is None:
        return
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
        rendered = embed(request, item_uri + '?embed=false')
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


@view_config(context=Item, permission='view', request_method='GET',
             decorator=etag_conditional)
def item_view(context, request):
    properties = context.__json__(request)
    if asbool(request.params.get('embed', True)):
        context.expand_embedded(request, properties)
    return properties


@view_config(context=Item, permission='view', request_method='GET',
             request_param=['raw'], additional_permission='view_raw')
def item_view_raw(context, request):
    if asbool(request.params.get('upgrade', True)):
        return context.upgrade_properties(request)
    return context.properties


@view_config(context=Item, permission='edit', request_method='PUT',
             validators=[validate_item_content_put])
@view_config(context=Item, permission='edit', request_method='PATCH',
             validators=[validate_item_content_patch])
@view_config(context=Item, permission='edit_unvalidated', request_method='PUT',
             validators=[no_validate_item_content_put],
             request_param=['validate=false'])
@view_config(context=Item, permission='edit_unvalidated', request_method='PATCH',
             validators=[no_validate_item_content_patch],
             request_param=['validate=false'])
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
        rendered = embed(request, item_uri + '?embed=false')
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
