# See http://docs.pylonsproject.org/projects/pyramid/en/latest/narr/resources.html
import logging
from collections import Mapping
from copy import deepcopy
from pyramid.decorator import reify
from pyramid.httpexceptions import HTTPInternalServerError
from pyramid.security import (
    Allow,
    Everyone,
)
from pyramid.traversal import resource_path
from .calculated import (
    calculate_properties,
    calculated_property,
)
from .interfaces import (
    COLLECTIONS,
    CONNECTION,
    ROOT,
    TYPES,
    UPGRADER,
)
from .validation import ValidationFailure
from .util import (
    ensurelist,
    simple_path_ids,
)

logger = logging.getLogger(__name__)


def includeme(config):
    config.scan(__name__)


class Resource(object):

    @calculated_property(name='@id', schema={
        "title": "ID",
        "type": "string",
    })
    def jsonld_id(self, request):
        return request.resource_path(self)

    @calculated_property(name='@context', category='page')
    def jsonld_context(self, request):
        return request.route_path('jsonld_context')

    @calculated_property(category='page')
    def actions(self, request):
        actions = calculate_properties(self, request, category='action')
        if actions:
            return list(actions.values())


class Root(Resource):
    __name__ = ''
    __parent__ = None
    __acl__ = [
        (Allow, 'remoteuser.INDEXER', ['view', 'list', 'index']),
        (Allow, 'remoteuser.EMBED', ['view', 'expand', 'audit']),
        (Allow, Everyone, ['visible_for_edit']),
    ]

    def __init__(self, registry):
        self.registry = registry

    @reify
    def connection(self):
        return self.registry[CONNECTION]

    @reify
    def collections(self):
        return self.registry[COLLECTIONS]

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

    @calculated_property(name='@type', schema={
        "title": "Type",
        "type": "array",
        "items": {
            "type": "string",
        },
    })
    def jsonld_type(self):
        return ['Portal']


class AbstractCollection(Resource, Mapping):
    properties = {}
    unique_key = None

    def __init__(self, registry, name, type_info, properties=None, acl=None, unique_key=None):
        self.registry = registry
        self.__name__ = name
        self.type_info = type_info
        if properties is not None:
            self.properties = properties
        if acl is not None:
            self.__acl__ = acl
        if unique_key is not None:
            self.unique_key = unique_key

    @reify
    def connection(self):
        return self.registry[CONNECTION]

    @reify
    def __parent__(self):
        return self.registry[ROOT]

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
        for uuid in self.connection.__iter__(*self.type_info.subtypes):
            yield uuid

    def __len__(self):
        return self.connection.__len__(*self.type_info.subtypes)

    def __hash__(self):
        return object.__hash__(self)

    def __eq__(self, other):
        return self is other

    def _allow_contained(self, resource):
        return resource.__parent__ is self or \
            resource.type_info.name in resource.type_info.subtypes

    def get(self, name, default=None):
        resource = self.connection.get_by_uuid(name, None)
        if resource is not None:
            if not self._allow_contained(resource):
                return default
            return resource
        if self.unique_key is not None:
            resource = self.connection.get_by_unique_key(self.unique_key, name)
            if resource is not None:
                if not self._allow_contained(resource):
                    return default
                return resource
        return default

    def __json__(self, request):
        return self.properties.copy()

    @calculated_property(name='@type', schema={
        "title": "Type",
        "type": "array",
        "items": {
            "type": "string",
        },
    })
    def jsonld_type(self):
        return [
            '{type_name}Collection'.format(type_name=self.type_info.name),
            'Collection',
        ]


class Collection(AbstractCollection):
    ''' Separate class so add views do not apply to AbstractCollection '''


class Item(Resource):
    item_type = None
    base_types = ['Item']
    name_key = None
    rev = {}
    embedded = ()
    audit_inherit = None
    schema = None
    AbstractCollection = AbstractCollection
    Collection = Collection

    def __init__(self, registry, model):
        self.registry = registry
        self.model = model

    def __repr__(self):
        return '<%s at %s>' % (type(self).__name__, resource_path(self))

    @reify
    def type_info(self):
        return self.registry[TYPES][type(self)]

    @reify
    def collection(self):
        collections = self.registry[COLLECTIONS]
        return collections[self.type_info.name]

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
        types = self.registry[TYPES]
        type_name, rel = self.rev[name]
        types = types[type_name].subtypes
        return self.registry[CONNECTION].get_rev_links(self.model, rel, *types)

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
                    self.type_info.name, properties, current_version, target_version,
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
        model = registry[CONNECTION].create(cls.__name__, uuid)
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

    @calculated_property(name='@type', schema={
        "title": "Type",
        "type": "array",
        "items": {
            "type": "string",
        },
    })
    def jsonld_type(self):
        return [self.type_info.name] + self.base_types

    @calculated_property(name='uuid')
    def prop_uuid(self):
        return str(self.uuid)
