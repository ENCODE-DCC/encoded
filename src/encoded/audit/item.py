from snovault import (
    AuditFailure,
    audit_checker,
)
from snovault import (
    UPGRADER,
)
from snovault.schema_utils import validate
from snovault.util import simple_path_ids
import re

@audit_checker('Item', frame='object')
def audit_item_schema(value, system):
    context = system['context']
    registry = system['registry']
    if not context.schema:
        return

    properties = context.properties.copy()
    current_version = properties.get('schema_version', '')
    target_version = context.type_info.schema_version
    if target_version is not None and current_version != target_version:
        upgrader = registry[UPGRADER]
        try:
            properties = upgrader.upgrade(
                context.type_info.name, properties, current_version, target_version,
                finalize=False, context=context, registry=registry)
        except RuntimeError:
            raise
        except Exception as e:
            detail = '%r upgrading from %r to %r' % (e, current_version, target_version)
            yield AuditFailure('upgrade failure', detail, level='INTERNAL_ACTION')
            return

        properties['schema_version'] = target_version

    properties['uuid'] = str(context.uuid)
    validated, errors = validate(context.schema, properties, properties)
    for error in errors:
        category = 'validation error'
        path = list(error.path)
        if path:
            category += ': ' + '/'.join(str(elem) for elem in path)
        detail = 'Object {} has schema error {}'.format(value['@id'], error.message)
        yield AuditFailure(category, detail, level='INTERNAL_ACTION')


STATUS_LEVEL = {
    # public statuses
    'released': 100,
    'current': 100,
    'published': 100,
    'compliant': 100,
    'not compliant': 100,
    'not reviewed': 100,
    'not submitted for review by lab': 100,
    'exempt from standards': 100,
    'eligible for new data': 100,
    'not eligible for new data': 100,
    'not pursued': 100,

    # 'discouraged for use' public statuses
    'archived': 40,
    'revoked': 30,

    # private statuses (visible for consortium members only)
    'in progress': 50,
    'pending dcc review': 50,
    'proposed': 50,
    'started': 50,
    'submitted': 50,
    'ready for review': 50,
    'uploading': 50,
    'upload failed': 50,
    'pending dcc review': 50,
    'awaiting lab characterization': 50,

    # invisible statuses (visible for admins only)
    'deleted': 0,
    'replaced': 0,
    'disabled': 0
    }


@audit_checker('Item', frame='object')
def audit_item_relations_status(value, system):
    if 'status' not in value:
        return

    level = STATUS_LEVEL.get(value['status'], 50)

    context = system['context']
    request = system['request']

    for schema_path in context.type_info.schema_links:
        if schema_path in ['supersedes']:
            for path in simple_path_ids(value, schema_path):
                linked_value = request.embed(path + '@@object')
                if 'status' not in linked_value:
                    continue
                else:
                    linked_level = STATUS_LEVEL.get(
                        linked_value['status'], 50)
                    detail = \
                        '{} with status \'{}\' supersedes {} with status \'{}\''.format(
                            value['@id'],
                            value['status'],
                            linked_value['@id'],
                            linked_value['status']
                            )
                    if level == 100 and linked_level in [0, 50, 100]:
                        yield AuditFailure(
                            'mismatched status',
                            detail,
                            level='INTERNAL_ACTION')
                    elif level == 50 and linked_level in [0, 50]:
                        yield AuditFailure(
                            'mismatched status',
                            detail,
                            level='INTERNAL_ACTION')
                    elif level in [30, 40] and linked_level in [0, 50, 100]:
                        yield AuditFailure(
                            'mismatched status',
                            detail,
                            level='INTERNAL_ACTION')

        elif schema_path in ['derived_from',
                             'controlled_by',
                             'possible_controls']:
            message = 'has a possible control'
            if schema_path == 'derived_from':
                message = 'is derived from'
            elif schema_path == 'controlled_by':
                message = 'is controlled by'
            for path in simple_path_ids(value, schema_path):
                linked_value = request.embed(path + '@@object')
                if 'status' not in linked_value:
                    continue
                else:
                    linked_level = STATUS_LEVEL.get(
                        linked_value['status'], 50)
                    if level > linked_level:
                        detail = \
                            '{} with status \'{}\' {} {} with status \'{}\''.format(
                                value['@id'],
                                value['status'],
                                message,
                                linked_value['@id'],
                                linked_value['status']
                                )
                        yield AuditFailure(
                            'mismatched status',
                            detail,
                            level='INTERNAL_ACTION')


@audit_checker('Item', frame='object')
def audit_item_aliases(value, system):
    aliases = value.get('aliases')
    if aliases:
        alias_pattern = re.compile('^([a-zA-Z\d-]+:[\sa-zA-Z\d_.+!\*\(\)\'-]+)$')
        for a in aliases:
            if alias_pattern.match(a) is None:
                detail = 'Found \"bad\" alias: {}.'.format(a)
                yield AuditFailure('inconsistent alias', detail, level='INTERNAL_ACTION')


@audit_checker('Item', frame='object')
def audit_item_status(value, system):
    if 'status' not in value:
        return

    level = STATUS_LEVEL.get(value['status'], 50)

    if level == 0:
        return

    if value['status'] in ['revoked', 'archived']:
        level += 50

    context = system['context']
    request = system['request']
    linked = set()

    for schema_path in context.type_info.schema_links:
        if schema_path in ['supersedes',
                           'step_run',
                           'derived_from',
                           'controlled_by',
                           'possible_controls']:
            continue
        else:
            linked.update(simple_path_ids(value, schema_path))

    for path in linked:
        linked_value = request.embed(path + '@@object')
        if 'status' not in linked_value:
            continue
        if linked_value['status'] == 'disabled':
            continue
        if (  # Special case: A revoked file can have a deleted replicate ticket #2938
            'File' in value['@type'] and
            value['status'] == 'revoked' and
            'Replicate' in linked_value['@type'] and
            linked_value['status'] == 'deleted'
        ):
            continue
        linked_level = STATUS_LEVEL.get(linked_value['status'], 50)
        if linked_value['status'] in ['revoked', 'archived']:
            linked_level += 50
        if linked_level == 0:
            detail = '{} {} has {} subobject {}'.format(
                value['status'], value['@id'], linked_value['status'], linked_value['@id'])
            yield AuditFailure('mismatched status', detail, level='INTERNAL_ACTION')
        elif linked_level < level:
            detail = '{} {} has {} subobject {}'.format(
                value['status'], value['@id'], linked_value['status'], linked_value['@id'])
            yield AuditFailure('mismatched status', detail, level='INTERNAL_ACTION')
