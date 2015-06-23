from contentbase.schema_utils import (
    load_schema,
    VALIDATOR_REGISTRY,
)
from contentbase import (
    COLLECTIONS,
    CONNECTION,
    ROOT,
    calculated_property,
    collection,
    item_view_page,
)
from .base import (
    ALLOW_EVERYONE_VIEW,
    Item,
    ONLY_ADMIN_VIEW,
)
from pyramid.location import lineage
from pyramid.threadlocal import get_current_request
from pyramid.traversal import (
    find_resource,
)
from pyramid.view import view_config


@collection(
    name='curator-pages',
    unique_key='curator_page:location',
    properties={
        'title': 'Curator pages',
        'description': 'Pages for the curator action flow',
    })
class CuratorPage(Item):
    item_type = 'curator_page'
    schema = load_schema('clincoded:schemas/curator_page.json')
    name_key = 'name'

    def unique_keys(self, properties):
        keys = super(CuratorPage, self).unique_keys(properties)
        parent = properties.get('parent')
        name = properties['name']
        value = name if parent is None else u'{}:{}'.format(parent, name)
        keys.setdefault('curator_page:location', []).append(value)
        return keys

    @calculated_property(
        condition=lambda context, request: request.resource_path(context.__parent__) == '/curator-pages/',
        schema={
            "title": "Canonical URI",
            "type": "string",
        })
    def canonical_uri(self, name):
        if name == 'homepage':
            return '/'
        return '/%s/' % name

    @property
    def __parent__(self):
        parent_uuid = self.properties.get('parent')
        name = self.__name__
        collections = self.registry[COLLECTIONS]
        connection = self.registry[CONNECTION]
        if parent_uuid:  # explicit parent
            return connection.get_by_uuid(parent_uuid)
        elif name in collections or name == 'homepage':
            # collection default page; use pages collection as canonical parent
            return self.collection
        else:  # top level
            return self.registry[ROOT]
