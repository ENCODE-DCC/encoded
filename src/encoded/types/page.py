from ..schema_utils import (
    load_schema,
    lookup_resource,
    VALIDATOR_REGISTRY,
)
from ..contentbase import (
    location,
)
from .base import (
    ADD_ACTION,
    ALLOW_EVERYONE_VIEW,
    Collection,
    EDIT_ACTION,
    ONLY_ADMIN_VIEW,
)
from pyramid.threadlocal import get_current_request
from pyramid.traversal import (
    find_root,
)


@location('pages')
class Page(Collection):
    item_type = 'page'
    properties = {
        'title': 'Pages',
        'description': 'Portal pages',
    }
    schema = load_schema('page.json')
    unique_key = 'page:location'
    template = {
        'actions': [ADD_ACTION],
    }

    class Item(Collection.Item):
        name_key = 'name'
        keys = [
            {'name': 'page:location', 'value': '{name}', '$templated': True,
             '$condition': lambda parent=None: parent is None},
            {'name': 'page:location', 'value': '{parent}:{name}', '$templated': True,
             '$condition': 'parent', '$templated': True},
        ]

        template = Collection.Item.template.copy()
        template['canonical_uri'] = {
            '$value': lambda name: '/%s/' % name if name != 'homepage' else '/',
            '$condition': lambda collection_uri=None: collection_uri == '/pages/',
            '$templated': True
        }

        actions = [EDIT_ACTION]

        STATUS_ACL = {
            'in progress': [],
            'released': ALLOW_EVERYONE_VIEW,
            'deleted': ONLY_ADMIN_VIEW,
        }

        @property
        def __parent__(self):
            parent_uuid = self.properties.get('parent')
            name = self.__name__
            root = find_root(self.collection)
            if parent_uuid:  # explicit parent
                return root.get_by_uuid(parent_uuid)
            elif name in root.collections or name == 'homepage':
                # collection default page; use pages collection as canonical parent
                return self.collection
            else:  # top level
                return root

        def is_default_page(self):
            name = self.__name__
            root = find_root(self.collection)
            if self.properties.get('parent'):
                return False
            return name in root.collections or name == 'homepage'

        # Handle traversal to nested pages

        def __getitem__(self, name):
            resource = self.get(name)
            if resource is None:
                raise KeyError(name)
            return resource

        def __contains__(self, name):
            return self.get(name, None) is not None

        def get(self, name, default=None):
            root = find_root(self)
            location = str(self.uuid) + ':' + name
            resource = root.get_by_unique_key('page:location', location)
            if resource is not None:
                return resource
            return default


def isNotCollectionDefaultPage(value, schema):
    if value:
        request = get_current_request()
        page = lookup_resource(request.root, request.root, value.encode('utf-8'))
        if page.is_default_page():
            return 'You may not place pages inside an object collection.'

VALIDATOR_REGISTRY['isNotCollectionDefaultPage'] = isNotCollectionDefaultPage
