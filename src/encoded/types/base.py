import logging
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
    view_config,
)
from snovault.crud_views import (
    update_item,
    item_edit
)
from snovault.interfaces import (
    BeforeModified,
    AfterModified,
)
import snovault


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
        'release ready': ALLOW_VIEWING_GROUP_VIEW,
        'revoked': ALLOW_CURRENT,
        'in review': ALLOW_CURRENT_AND_SUBMITTER_EDIT,

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

    def set_property(self, field, value):
        import logging
        logging.warn('Setting prop')
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

from snovault.schema_utils import schema_validator
from snovault.validators import validate_item_content_patch
@view_config(context=Item, permission='edit', request_method='PATCH',
             name='release', validators=[validate_item_content_patch])
def item_release_object(context, request):
    logging.warn('releasing object {}'.format(str(context.uuid)))
    #props = context.properties.copy()
    #props['status'] = 'released'
    #request.registry.notify(BeforeModified(context, request))
    #context.update(props)
    #request.registry.notify(AfterModified(context, request))
    ##rendered = context.upgrade_properties()
    #logging.warn(request.validated)
    if not context.properties.get('status'):
        from snovault.validation import ValidationFailure
        raise ValidationFailure('status', [context.item_type], 'Status property not found')
    res = item_edit(context, request)
    logging.warn(request._linked_uuids)
    related = request._linked_uuids.union(request._embedded_uuids)
    logging.warn(related)
    uuids_to_release = []
    ignore_assembly = True
    if request.params.get('assembly'):
        ignore_assembly = False
    for uuid in related:
        logging.warn(uuid)
        r = request.embed('/{}'.format(uuid), '@@page', as_user=True)
        if ((r.get('status') == 'in progress' and (ignore_assembly or r.get('assembly') == request.params.get('assembly', False))) or (r.get('status') == 'in progress' and r.get('output_type') == 'reads')):
            uuids_to_release.append(r.get('@id'))
    related = set(
        [(str(x), request.registry['storage'].write.get_by_uuid(x).item_type) for x in request._linked_uuids] +
        [(str(x), request.registry['storage'].write.get_by_uuid(x).item_type) for x in request._embedded_uuids]
    )
    related.discard(context.uuid)
    logging.warn(related)
    for uuid, name in related:
        logging.warn(uuid)
        r = request.embed('/{}'.format(uuid), '@@page', as_user=True)
        logging.warn('{}, {}'.format(name, r.get('status')))
        if ((r.get('status') == 'in progress' and (ignore_assembly or r.get('assembly') == request.params.get('assembly', False))) or (r.get('status') == 'in progress' and r.get('output_type') == 'reads')):
            uuids_to_release.append(r.get('@id'))
    logging.warn(set(uuids_to_release))
    for uuid in set(uuids_to_release):
        logging.warn('releasing {}'.format(uuid))
        from pyramid.traversal import traverse
        context = traverse(request.registry['root'], uuid)['context']
        props = context.properties.copy()
        props['status'] = 'released'
        request.registry.notify(BeforeModified(context, request))
        context.update(props)
        request.registry.notify(AfterModified(context, request))
    result = {
        'status': 'success',
        '@type': ['result'],
        '@graph': [context.properties],
    }
    return res
