from pyramid.security import (
    ALL_PERMISSIONS,
    Allow,
    Authenticated,
    DENY_ALL,
    Everyone,
)
from .. import contentbase

ALLOW_EVERYONE_VIEW = [
    (Allow, Everyone, 'view'),
]

ALLOW_SUBMITTER_ADD = [
    (Allow, 'group.submitter', 'add')
]

ALLOW_AUTHENTICATED_VIEW = [
    (Allow, Authenticated, 'view'),
]

ALLOW_LAB_SUBMITTER_EDIT = [
    (Allow, Authenticated, 'view'),
    (Allow, 'group.admin', 'edit'),
    (Allow, 'role.lab_submitter', 'edit'),
]

ALLOW_CURRENT = [
    (Allow, Everyone, 'view'),
    (Allow, 'group.admin', 'edit'),
]

ONLY_ADMIN_VIEW = [
    (Allow, 'group.admin', ALL_PERMISSIONS),
    (Allow, 'group.read-only-admin', ['view']),
    (Allow, 'remoteuser.EMBED', ['view', 'expand', 'audit']),
    (Allow, 'remoteuser.INDEXER', ['view', 'index']),
    DENY_ALL,
]


TYPES_WITH_FORMS = [
    'image',
    'page',
]

ADD_ACTION = {
    'name': 'add',
    'title': 'Add',
    'profile': '/profiles/{item_type}.json',
    'href': '{item_uri}#!add',
    'className': 'btn-success',
    '$templated': True,
    '$condition': lambda item_type, permission: item_type in TYPES_WITH_FORMS and permission('add'),
}

EDIT_ACTION = {
    'name': 'edit',
    'title': 'Edit',
    'profile': '/profiles/{item_type}.json',
    'href': lambda item_uri, item_type: item_uri + (
        '#!edit' if item_type in TYPES_WITH_FORMS else '#!edit-json'),
    '$condition': 'permission:edit',
    '$templated': True,
}


def paths_filtered_by_status(request, paths, exclude=('deleted', 'replaced')):
    return [
        path for path in paths
        if request.embed(path, '@@object').get('status') not in exclude
    ]


class Item(contentbase.TemplatedItem):
    STATUS_ACL = {
        # standard_status
        'released': ALLOW_CURRENT,
        'deleted': ONLY_ADMIN_VIEW,
        'replaced': ONLY_ADMIN_VIEW,

        # shared_status
        'current': ALLOW_CURRENT,
        'disabled': ONLY_ADMIN_VIEW,

        # file
        'obsolete': ONLY_ADMIN_VIEW,

        # antibody_characterization
        'compliant': ALLOW_CURRENT,
        'not compliant': ALLOW_CURRENT,
        'not reviewed': ALLOW_CURRENT,
        'not submitted for review by lab': ALLOW_CURRENT,

        # antibody_lot
        'eligible for new data': ALLOW_CURRENT,
        'not eligible for new data': ALLOW_CURRENT,
        'not pursued': ALLOW_CURRENT,

        # dataset / experiment
        'release ready': ALLOW_AUTHENTICATED_VIEW,
        'revoked': ALLOW_CURRENT,

        # publication
        'published': ALLOW_CURRENT,
    }
    actions = [EDIT_ACTION]

    @property
    def __name__(self):
        if self.name_key is None:
            return self.uuid
        properties = self.upgrade_properties(finalize=False)
        if properties.get('status') == 'replaced':
            return self.uuid
        return properties.get(self.name_key, None) or self.uuid

    def __acl__(self):
        # Don't finalize to avoid validation here.
        properties = self.upgrade_properties(finalize=False).copy()
        if 'status' in self.namespace_from_path:
            ns = self.template_namespace(properties)
            properties.update(ns)
        status = properties.get('status')
        return self.STATUS_ACL.get(status, ALLOW_LAB_SUBMITTER_EDIT)

    def __ac_local_roles__(self):
        roles = {}
        properties = self.upgrade_properties(finalize=False).copy()
        if 'lab' in self.namespace_from_path:
            ns = self.template_namespace(properties)
            properties.update(ns)
        if 'lab' in properties:
            lab_submitters = 'submits_for.%s' % properties['lab']
            roles[lab_submitters] = 'role.lab_submitter'
        return roles

    def keys(self):
        keys = super(Item, self).keys()
        if 'accession' not in self.schema['properties']:
            return keys
        properties = self.upgrade_properties(finalize=False)
        keys.setdefault('accession', []).extend(properties.get('alternate_accessions', []))
        if properties.get('status') != 'replaced' and 'accession' in properties:
            keys['accession'].append(properties['accession'])
        return keys

    class Collection(contentbase.Collection):
        actions = [ADD_ACTION]

        def __init__(self, *args, **kw):
            super(Item.Collection, self).__init__(*args, **kw)
            if hasattr(self, '__acl__'):
                return
            if 'lab' in self.Item.schema['properties']:
                self.__acl__ = ALLOW_SUBMITTER_ADD
