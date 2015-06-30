# See http://docs.pylonsproject.org/projects/pyramid/en/latest/narr/resources.html
import logging
import sys
from collections import Mapping
from copy import deepcopy
from future.utils import (
    raise_with_traceback,
    itervalues,
)
from itertools import islice
from past.builtins import basestring
from pyramid.decorator import reify
from pyramid.exceptions import PredicateMismatch
from pyramid.httpexceptions import (
    HTTPInternalServerError,
    HTTPNotFound,
)
from pyramid.security import (
    Allow,
    Everyone,
    principals_allowed_by_permission,
)
from pyramid.settings import asbool
from pyramid.traversal import (
    resource_path,
)
from pyramid.view import (
    render_view_to_response,
    view_config,
)
from urllib.parse import urlencode
from .calculated import (
    calculate_properties,
    calculated_property,
)
from .embedding import (
    expand_path,
)
from .etag import etag_tid
from .interfaces import (
    COLLECTIONS,
    CONNECTION,
    ROOT,
    TYPES,
    UPGRADER,
)
from .validation import ValidationFailure
from .util import ensurelist


_marker = object()

logger = logging.getLogger(__name__)


def includeme(config):
    config.scan(__name__)


class Root(object):
    __name__ = ''
    __parent__ = None
    __acl__ = [
        (Allow, 'remoteuser.INDEXER', ['view', 'list', 'index']),
        (Allow, 'remoteuser.EMBED', ['view', 'expand', 'audit']),
        (Allow, Everyone, ['visible_for_edit']),
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
    def type_info(self):
        return self.registry[TYPES][self.item_type]

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

    def __iter__(self):
        for uuid in self.connection.__iter__(self.item_type):
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
    def type_info(self):
        return self.registry[TYPES][self.item_type]

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

    def links(self, properties):
        return {
            path: set(simple_path_ids(properties, path))
            for path in self.type_info.schema_links
        }

    def get_rev_links(self, name):
        item_type, rel = self.rev[name]
        item_types = self.registry[TYPES].abstract[item_type].subtypes
        return self.registry[CONNECTION].get_rev_links(self.model, rel, *item_types)

    def unique_keys(self, properties):
        return {
            name: [v for prop in props for v in ensurelist(properties.get(prop, ()))]
            for name, props in self.type_info.schema_keys.items()
        }

    def upgrade_properties(self):
        properties = deepcopy(self.properties)
        current_version = properties.get('schema_version', '')
        target_version = self.type_info.schema_version
        if target_version is not None and current_version != target_version:
            upgrader = self.registry[UPGRADER]
            try:
                properties = upgrader.upgrade(
                    self.item_type, properties, current_version, target_version,
                    context=self, registry=self.registry)
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
    def create(cls, registry, uuid, properties, sheets=None):
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


@view_config(context=Collection, permission='list', request_method='GET',
             name='listing')
def collection_view_listing_db(context, request):
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

    calculated = calculate_properties(context, request, properties, category='page')
    properties.update(calculated)

    result = request.embed(path, '@@listing?' + request.query_string, as_user=True)
    result.update(properties)
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
    return request.embed(path, as_user=True)


def item_links(context, request):
    # This works from the schema rather than the links table
    # so that upgrade on GET can work.
    properties = context.__json__(request)
    for path in context.type_info.schema_links:
        uuid_to_path(request, properties, path)
    return properties


def uuid_to_path(request, obj, path):
    if isinstance(path, basestring):
        path = path.split('.')
    if not path:
        return
    name = path[0]
    remaining = path[1:]
    value = obj.get(name, None)
    if value is None:
        return
    if remaining:
        if isinstance(value, list):
            for v in value:
                uuid_to_path(request, v, remaining)
        else:
            uuid_to_path(request, value, remaining)
        return
    conn = request.registry[CONNECTION]
    if isinstance(value, list):
        obj[name] = [
            request.resource_path(conn[v])
            for v in value
        ]
    else:
        obj[name] = request.resource_path(conn[value])


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
    conn = request.registry[CONNECTION]
    properties = item_links(context, request)
    schema_rev_links = context.type_info.schema_rev_links

    for propname in schema_rev_links:
        properties[propname] = sorted(
            request.resource_path(child)
            for child in (
                conn.get_by_uuid(uuid) for uuid in context.get_rev_links(propname)
            ) if request.has_permission('visible_for_edit', child)
        )

    return properties


def simple_path_ids(obj, path):
    if isinstance(path, basestring):
        path = path.split('.')
    if not path:
        yield obj
        return
    name = path[0]
    remaining = path[1:]
    value = obj.get(name, None)
    if value is None:
        return
    if isinstance(value, list):
        for member in value:
            for result in simple_path_ids(member, remaining):
                yield result
    else:
        for result in simple_path_ids(value, remaining):
            yield result


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
                member = request.embed(member, '@@object')
            for item_uri in path_ids(request, member, remaining):
                yield item_uri
    else:
        if remaining and isinstance(value, basestring):
            value = request.embed(value, '@@object')
        for item_uri in path_ids(request, value, remaining):
            yield item_uri


def inherit_audits(request, embedded, embedded_paths):
    audit_paths = {embedded['@id']}
    for embedded_path in embedded_paths:
        audit_paths.update(path_ids(request, embedded, embedded_path))

    audits = {}
    for audit_path in audit_paths:
        result = request.embed(audit_path, '@@audit-self')
        for audit in result['audit']:
            if audit['level_name'] in audits:
                audits[audit['level_name']].append(audit)
            else:
                audits[audit['level_name']] = [audit]
    return audits


@view_config(context=Item, name='index-data', permission='index', request_method='GET')
def item_index_data(context, request):
    uuid = str(context.uuid)
    properties = context.upgrade_properties()
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
    object = request.embed(path, '@@object')
    audit = request.embed(path, '@@audit')['audit']

    document = {
        'audit': audit,
        'embedded': embedded,
        'embedded_uuids': sorted(request._embedded_uuids),
        'item_type': context.item_type,
        'linked_uuids': sorted(request._linked_uuids),
        'links': links,
        'object': object,
        'paths': sorted(paths),
        'principals_allowed': principals_allowed,
        'properties': properties,
        'propsheets': {
            name: context.propsheets[name]
            for name in context.propsheets.keys() if name != ''
        },
        'tid': context.tid,
        'unique_keys': unique_keys,
        'uuid': uuid,
    }

    return document


@view_config(context=Root, request_method='GET')
def home(context, request):
    properties = context.__json__(request)
    properties.update({
        '@id': request.resource_path(context),
        '@type': ['portal'],
    })
    calculated = calculate_properties(context, request, properties, category='page')
    properties.update(calculated)
    return properties
