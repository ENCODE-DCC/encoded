from snovault import (
    AuditFailure,
    audit_checker,
)
from snovault import (
    UPGRADER,
)
from snovault.schema_utils import validate
from snovault.util import simple_path_ids


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
            yield AuditFailure('upgrade failure', detail, level='DCC_ACTION')
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
        yield AuditFailure(category, detail, level='DCC_ACTION')


STATUS_LEVEL = {
    # standard_status
    'released': 100,
    'deleted': 0,
    'replaced': 0,

    # shared_status
    'current': 100,
    'disabled': 0,

    # file
    'obsolete': 50,

    # antibody_characterization
    'compliant': 100,
    'not compliant': 100,
    'not reviewed': 100,
    'not submitted for review by lab': 100,

    # antibody_lot
    'eligible for new data': 100,
    'not eligible for new data': 100,
    'not pursued': 100,

    # dataset / experiment
    'release ready': 50,
    'revoked': 100,

    # publication
    'published': 100,
}


@audit_checker('Item', frame='object')
def audit_item_status(value, system):
    if 'status' not in value:
        return

    level = STATUS_LEVEL.get(value['status'], 50)
    if level == 0:
        return

    context = system['context']
    request = system['request']
    linked = set()
    for schema_path in context.type_info.schema_links:
        if schema_path in ['supercedes', 'step_run']:
            continue
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
        if linked_level == 0:
            detail = '{} {} has {} subobject {}'.format(
                value['status'], value['@id'], linked_value['status'], linked_value['@id'])
            yield AuditFailure('mismatched status', detail, level='ERROR')
        elif linked_level < level:
            detail = '{} {} has {} subobject {}'.format(
                value['status'], value['@id'], linked_value['status'], linked_value['@id'])
            yield AuditFailure('mismatched status', detail, level='DCC_ACTION')
