from functools import lru_cache
from pyramid.security import (
    ALL_PERMISSIONS,
    Allow,
    Authenticated,
    Deny,
    DENY_ALL,
    Everyone,
)
from pyramid.traversal import (
    find_root,
    traverse,
)
from pyramid.view import (
    view_config
)
import snovault
from snovault.validators import validate_item_content_patch


@lru_cache()
def _award_viewing_group(award_uuid, root):
    award = root.get_by_uuid(award_uuid)
    return award.upgrade_properties().get('viewing_group')


# Item acls
ONLY_ADMIN_VIEW = [
    (Allow, 'group.admin', ['view', 'edit']),
    (Allow, 'group.read-only-admin', ['view']),
    (Allow, 'remoteuser.INDEXER', ['view']),
    (Allow, 'remoteuser.EMBED', ['view']),
    (Deny, Everyone, ['view', 'edit']),
]

ALLOW_EVERYONE_VIEW = [
    (Allow, Everyone, 'view'),
] + ONLY_ADMIN_VIEW


ALLOW_VIEWING_GROUP_VIEW = [
    (Allow, 'role.viewing_group_member', 'view'),
] + ONLY_ADMIN_VIEW

ALLOW_LAB_SUBMITTER_EDIT = [
    (Allow, 'role.viewing_group_member', 'view'),
    (Allow, 'role.lab_submitter', 'edit'),
] + ONLY_ADMIN_VIEW

ALLOW_CURRENT_AND_SUBMITTER_EDIT = [
    (Allow, Everyone, 'view'),
    (Allow, 'role.lab_submitter', 'edit'),
] + ONLY_ADMIN_VIEW

ALLOW_CURRENT = [
    (Allow, Everyone, 'view'),
] + ONLY_ADMIN_VIEW

DELETED = [
    (Deny, Everyone, 'visible_for_edit')
] + ONLY_ADMIN_VIEW


# Collection acls

ALLOW_SUBMITTER_ADD = [
    (Allow, 'group.submitter', ['add']),
]

# New status must contain current status in list to be valid transition.
STATUS_TRANSITION_TABLE = {
    'released': ['in progress'],
    'in progress': ['released', 'archived', 'deleted', 'revoked']
}


def paths_filtered_by_status(request, paths, exclude=('deleted', 'replaced'), include=None):
    if include is not None:
        return [
            path for path in paths
            if traverse(request.root, path)['context'].__json__(request).get('status') in include
        ]
    else:
        return [
            path for path in paths
            if traverse(request.root, path)['context'].__json__(request).get('status') not in exclude
        ]


class AbstractCollection(snovault.AbstractCollection):
    def get(self, name, default=None):
        resource = super(AbstractCollection, self).get(name, None)
        if resource is not None:
            return resource
        if ':' in name:
            resource = self.connection.get_by_unique_key('alias', name)
            if resource is not None:
                if not self._allow_contained(resource):
                    return default
                return resource
        return default


class Collection(snovault.Collection, AbstractCollection):
    def __init__(self, *args, **kw):
        super(Collection, self).__init__(*args, **kw)
        if hasattr(self, '__acl__'):
            return
        # XXX collections should be setup after all types are registered.
        # Don't access type_info.schema here as that precaches calculated schema too early.
        if 'lab' in self.type_info.factory.schema['properties']:
            self.__acl__ = ALLOW_SUBMITTER_ADD


class Item(snovault.Item):
    AbstractCollection = AbstractCollection
    Collection = Collection
    STATUS_ACL = {
        # standard_status
        'released': ALLOW_CURRENT,
        'deleted': DELETED,
        'replaced': DELETED,

        # shared_status
        'current': ALLOW_CURRENT,
        'disabled': ONLY_ADMIN_VIEW,

        # antibody_characterization
        'compliant': ALLOW_CURRENT,
        'not compliant': ALLOW_CURRENT,
        'not reviewed': ALLOW_CURRENT,
        'not submitted for review by lab': ALLOW_CURRENT,
        'exempt from standards': ALLOW_CURRENT,

        # antibody_lot
        'not pursued': ALLOW_CURRENT,

        # dataset / experiment
        'revoked': ALLOW_CURRENT,

        'archived': ALLOW_CURRENT,
    }

    @property
    def __name__(self):
        if self.name_key is None:
            return self.uuid
        properties = self.upgrade_properties()
        if properties.get('status') == 'replaced':
            return self.uuid
        return properties.get(self.name_key, None) or self.uuid

    def __acl__(self):
        # Don't finalize to avoid validation here.
        properties = self.upgrade_properties().copy()
        status = properties.get('status')
        return self.STATUS_ACL.get(status, ALLOW_LAB_SUBMITTER_EDIT)

    def __ac_local_roles__(self):
        roles = {}
        properties = self.upgrade_properties().copy()
        if 'lab' in properties:
            lab_submitters = 'submits_for.%s' % properties['lab']
            roles[lab_submitters] = 'role.lab_submitter'
        if 'award' in properties:
            viewing_group = _award_viewing_group(properties['award'], find_root(self))
            if viewing_group is not None:
                viewing_group_members = 'viewing_group.%s' % viewing_group
                roles[viewing_group_members] = 'role.viewing_group_member'
        return roles

    def unique_keys(self, properties):
        keys = super(Item, self).unique_keys(properties)
        if 'accession' not in self.schema['properties']:
            return keys
        keys.setdefault('accession', []).extend(properties.get('alternate_accessions', []))
        if properties.get('status') != 'replaced' and 'accession' in properties:
            keys['accession'].append(properties['accession'])
        return keys

    def set_status(self, new_status, request, parent=True):
        # Not implemented by default.
        pass


class SharedItem(Item):
    ''' An Item visible to all authenticated users while "in progress".
    '''
    def __ac_local_roles__(self):
        roles = {}
        properties = self.upgrade_properties().copy()
        if 'lab' in properties:
            lab_submitters = 'submits_for.%s' % properties['lab']
            roles[lab_submitters] = 'role.lab_submitter'
        roles[Authenticated] = 'role.viewing_group_member'
        return roles


@snovault.calculated_property(context=Item.Collection, category='action')
def add(context, request):
    if request.has_permission('add'):
        return {
            'name': 'add',
            'title': 'Add',
            'profile': '/profiles/{ti.name}.json'.format(ti=context.type_info),
            'href': '{item_uri}#!add'.format(item_uri=request.resource_path(context)),
        }


@snovault.calculated_property(context=Item, category='action')
def edit(context, request):
    if request.has_permission('edit'):
        return {
            'name': 'edit',
            'title': 'Edit',
            'profile': '/profiles/{ti.name}.json'.format(ti=context.type_info),
            'href': '{item_uri}#!edit'.format(item_uri=request.resource_path(context)),
        }


@snovault.calculated_property(context=Item, category='action')
def edit_json(context, request):
    if request.has_permission('edit'):
        return {
            'name': 'edit-json',
            'title': 'Edit JSON',
            'profile': '/profiles/{ti.name}.json'.format(ti=context.type_info),
            'href': '{item_uri}#!edit-json'.format(item_uri=request.resource_path(context)),
        }


@view_config(context=Item, permission='edit_unvalidated', request_method='PATCH',
             name='release', validators=[validate_item_content_patch])
def item_release(context, request):
    new_status = 'released'
    context.set_status(new_status, request)


@view_config(context=Item, permission='edit_unvalidated', request_method='PATCH',
             name='unrelease', validators=[validate_item_content_patch])
def item_unrelease(context, request):
    new_status = 'in progress'
    context.set_status(new_status, request)
