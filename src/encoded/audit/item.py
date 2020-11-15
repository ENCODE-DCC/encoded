from snovault import (
    AuditFailure,
    audit_checker,
)
from snovault import (
    UPGRADER,
)
from snovault.schema_utils import validate
from snovault.util import simple_path_ids
from .formatter import (
    audit_link,
    path_to_text,
    space_in_words,
)


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
            detail = '%r upgrading from %r to %r' % (
                e, current_version, target_version)
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
        detail = ('{} {} has schema error {}.'.format(
            space_in_words(value['@type'][0]).capitalize(),
            audit_link(path_to_text(value['@id']), value['@id']),
            error.message
            )
        )
        yield AuditFailure(category, detail, level='INTERNAL_ACTION')


STATUS_LEVEL = {
    # public statuses
    'released': 100,
    'current': 100,

    # 'discouraged for use' public statuses
    'archived': 40,
    'revoked': 30,

    # private statuses (visible for consortium members only)
    'in progress': 50,
    'submitted': 50,
    'content error': 50,

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
                    detail = ('{} {} with status \'{}\' supersedes {} {} with status \'{}\'.'.format(
                        space_in_words(value['@type'][0]).capitalize(),
                        audit_link(path_to_text(value['@id']), value['@id']),
                        value['status'],
                        space_in_words(linked_value['@type'][0]).lower(),
                        audit_link(path_to_text(linked_value['@id']), linked_value['@id']),
                        linked_value['status']
                        )
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

        elif schema_path == 'derived_from':
            message = 'is derived from'
            for path in simple_path_ids(value, schema_path):
                linked_value = request.embed(path + '@@object')
                if 'status' not in linked_value:
                    continue
                else:
                    linked_level = STATUS_LEVEL.get(
                        linked_value['status'], 50)
                    if level > linked_level:
                        detail = ('{} {} with status \'{}\' {} {} {} with status \'{}\'.'.format(
                            space_in_words(value['@type'][0]).capitalize(),
                            audit_link(path_to_text(value['@id']), value['@id']),
                            value['status'],
                            message,
                            space_in_words(linked_value['@type'][0]).lower(),
                            audit_link(path_to_text(linked_value['@id']), linked_value['@id']),
                            linked_value['status']
                            )
                        )
                        yield AuditFailure(
                            'mismatched status',
                            detail,
                            level='INTERNAL_ACTION')


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
                           'derived_from']:
            continue
        else:
            linked.update(simple_path_ids(value, schema_path))

    for path in linked:
        linked_value = request.embed(path + '@@object')
        if 'status' not in linked_value:
            continue
        if linked_value['status'] == 'disabled':
            continue
        linked_level = STATUS_LEVEL.get(linked_value['status'], 50)
        if linked_value['status'] in ['revoked', 'archived']:
            linked_level += 50
        if linked_level == 0:
            detail = ('{} {} {} has {} subobject {} {}'.format(
                value['status'].capitalize(),
                space_in_words(value['@type'][0]).lower(),
                audit_link(path_to_text(value['@id']), value['@id']),
                linked_value['status'],
                space_in_words(linked_value['@type'][0]).lower(),
                audit_link(path_to_text(linked_value['@id']), linked_value['@id'])
                )
            )
            yield AuditFailure('mismatched status', detail, level='INTERNAL_ACTION')
        elif linked_level < level:
            detail = ('{} {} {} has {} subobject {} {}'.format(
                value['status'].capitalize(),
                space_in_words(value['@type'][0]).lower(),
                audit_link(path_to_text(value['@id']), value['@id']),
                linked_value['status'],
                space_in_words(linked_value['@type'][0]).lower(),
                audit_link(path_to_text(linked_value['@id']), linked_value['@id'])
                )
            )
            yield AuditFailure('mismatched status', detail, level='INTERNAL_ACTION')
