import itertools
from datetime import datetime
from functools import lru_cache
import logging
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
    resource_path
)
from pyramid.view import (
    view_config
)
from pyramid.settings import asbool
import snovault
from snovault.validation import ValidationFailure
from snovault.schema_utils import validate_request
from snovault.auditor import traversed_path_ids
from snovault import (
    AfterModified,
    BeforeModified
)


@lru_cache()
def _award_viewing_groups(award_uuid, root):
    award = root.get_by_uuid(award_uuid)
    return award.upgrade_properties().get('viewing_groups')


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
    (Allow, Authenticated, 'view')
] + ONLY_ADMIN_VIEW

DELETED = [
    (Deny, Everyone, 'visible_for_edit')
] + ONLY_ADMIN_VIEW


# Collection acls

ALLOW_SUBMITTER_ADD = [
    (Allow, 'group.submitter', ['add']),
]

# Key is new status. Value is list of current statuses that can transition to the new status.
# For example, a released, in progress, or submitted experiment can transition to released.
# Transitioning to the same status (released -> released) allows for the child objects to be crawled
# without actually making a patch if the new and current statuses are the same.
STATUS_TRANSITION_TABLE = {
    'released': ['released', 'in progress', 'submitted'],
    'in progress': ['in progress'],
    'deleted': ['deleted', 'in progress', 'current', 'submitted'],
    'revoked': ['revoked', 'released', 'archived'],
    'archived': ['archived', 'released'],
    'submitted': ['submitted', 'in progress'],
    'replaced': [],
    'disabled': ['disabled', 'current'],
    'current': ['current'],
    'uploading': ['uploading', 'upload failed', 'content error'],
    'content error': ['uploading'],
    'upload failed': ['uploading'],
}

# Used to calculate whether new_status is more or less than current_status.
STATUS_HIERARCHY = {
    'released': 100,
    'current': 100,
    'in progress': 90,
    'submitted': 80,
    'uploading': 80,
    'archived': 70,
    'revoked': 50,
    'disabled': 10,
    'deleted': 0,
    'replaced': -10,
    'content error': -20,
    'upload failed': -20,
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

    # Empty by default. Children objects to iterate through when changing status
    # of parent object.
    set_status_up = []
    set_status_down = []

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
            viewing_groups = _award_viewing_groups(properties['award'], find_root(self))
            if viewing_groups is not None:
                for group in viewing_groups:
                    viewing_group_members = 'viewing_group.%s' % group
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

    @staticmethod
    def _valid_status(new_status, schema, parent):
        valid_statuses = schema.get('properties', {}).get('status', {}).get('enum', [])
        if new_status not in valid_statuses:
            if parent:
                msg = '{} not one of {}'.format(
                    new_status,
                    valid_statuses
                )
                raise ValidationFailure('body', ['status'], msg)
            else:
                return False
        return True

    @staticmethod
    def _valid_transition(current_status, new_status, parent, force_transition):
        if current_status not in STATUS_TRANSITION_TABLE[new_status] and not force_transition:
            if parent:
                msg = 'Status transition {} to {} not allowed'.format(
                    current_status,
                    new_status
                )
                raise ValidationFailure('body', ['status'], msg)
            else:
                return False
        return True

    @staticmethod
    def _validate_set_status_patch(request, schema, new_properties, current_properties):
        validate_request(schema, request, new_properties, current_properties)
        if any(request.errors):
            raise ValidationFailure(request.errors)

    def _update_status(self, new_status, current_status, current_properties, schema, request, item_id, update, validate=True):
        new_properties = current_properties.copy()
        new_properties['status'] = new_status
        # Some release specific functionality.
        if new_status == 'released':
            # This won't be reassigned if you rerelease something.
            if 'date_released' in schema['properties'] and 'date_released' not in new_properties:
                new_properties['date_released'] = str(datetime.now().date())
        if validate:
            self._validate_set_status_patch(request, schema, new_properties, current_properties)
        # Don't update if update parameter not true.
        if not update:
            return
        # Don't actually patch if the same.
        if new_status == current_status:
            return
        request.registry.notify(BeforeModified(self, request))
        self.update(new_properties)
        request.registry.notify(AfterModified(self, request))
        request._set_status_changed_paths.add((item_id, current_status, new_status))

    def _get_child_paths(self, current_status, new_status, block_children):
        # Do not traverse children if parameter specified.
        if block_children:
            return []
        # Only transition released -> released should trigger up list
        # if new and current statuses the same.
        if all([x == 'released' for x in [current_status, new_status]]):
            return self.set_status_up
        # List of child_paths depends on if status is going up or down.
        if STATUS_HIERARCHY[new_status] > STATUS_HIERARCHY[current_status]:
            child_paths = self.set_status_up
        else:
            child_paths = self.set_status_down
        return child_paths

    @staticmethod
    def _get_related_object(child_paths, embedded_properties, request):
        related_objects = set()
        for path in child_paths:
            for child_id in traversed_path_ids(request, embedded_properties, path):
                related_objects.add(child_id)
        return related_objects

    @staticmethod
    def _block_on_audits(item_id, force_audit, request, parent, new_status):
        if new_status not in ['released', 'submitted']:
            return
        if not parent or force_audit:
            return
        audits = request.embed(item_id, '@@audit')
        errors = audits.get('audit', {}).get('ERROR', [])
        not_compliants = audits.get('audit', {}).get('NOT_COMPLIANT', [])
        details = {
            detail.get('detail')
            for detail in itertools.chain(errors, not_compliants)
            if detail.get('detail')
        }
        if audits and any([errors, not_compliants]):
            raise ValidationFailure(
                'body',
                ['status'],
                'Audit on parent object. Must use ?force_audit=true to change status. {}'.format(list(details))
            )

    @staticmethod
    def _set_status_on_related_objects(new_status, related_objects, root, request):
        for child_id in related_objects:
            # Avoid cycles.
            visited_children = [
                x[0]
                for x in request._set_status_changed_paths.union(
                        request._set_status_considered_paths
                )
            ]
            if child_id in visited_children:
                continue
            else:
                child_uuid = request.embed(child_id).get('uuid')
                encoded_item = root.get_by_uuid(child_uuid)
                encoded_item.set_status(
                    new_status,
                    request,
                    parent=False
                )
        return True

    @staticmethod
    def _calculate_block_children(request, force_transition):
        block_children_param = request.params.get('block_children', None)
        if force_transition:
            return True
        return asbool(block_children_param)

    def set_status(self, new_status, request, parent=True):
        root = find_root(self)
        schema = self.type_info.schema
        properties = self.upgrade_properties()
        item_id = '{}/'.format(resource_path(self))
        current_status = properties.get('status')
        if not current_status:
            raise ValidationFailure('body', ['status'], 'No property status')
        if not self._valid_status(new_status, schema, parent):
            return False
        force_transition = asbool(request.params.get('force_transition'))
        if not self._valid_transition(current_status, new_status, parent, force_transition):
            return False
        force_audit = asbool(request.params.get('force_audit'))
        self._block_on_audits(item_id, force_audit, request, parent, new_status)
        update = asbool(request.params.get('update'))
        validate = asbool(request.params.get('validate', True))
        self._update_status(new_status, current_status, properties, schema, request, item_id, update, validate=validate)
        request._set_status_considered_paths.add((item_id, current_status, new_status))
        logging.warn(
            'Considering {} from status {} to status {}'.format(item_id, current_status, new_status)
        )
        block_children = self._calculate_block_children(request, force_transition)
        child_paths = self._get_child_paths(current_status, new_status, block_children)
        embedded_properties = request.embed(item_id, '@@embedded')
        related_objects = self._get_related_object(child_paths, embedded_properties, request)
        self._set_status_on_related_objects(new_status, related_objects, root, request)
        return True


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
             name='set_status')
def item_set_status(context, request):
    new_status = request.json_body.get('status')
    if not new_status:
        raise ValidationFailure('body', ['status'], 'Status not specified')
    context.set_status(new_status, request)
    # Returns changed and considered lists of tuples: (item, current_status, new_status).
    return {
        'status': 'success',
        '@type': ['result'],
        'changed': request._set_status_changed_paths,
        'considered': request._set_status_considered_paths
    }
