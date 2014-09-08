from ..auditor import (
    AuditFailure,
    audit_checker,
)
from ..schema_utils import validate


@audit_checker('item')
def audit_item_schema(value, system):
    context = system['context']
    registry = system['registry']
    if not context.schema:
        return

    properties = context.properties.copy()
    current_version = properties.get('schema_version', '')
    target_version = context.schema_version
    if target_version is not None and current_version != target_version:
        migrator = registry['migrator']
        try:
            properties = migrator.upgrade(
                context.item_type, properties, current_version, target_version,
                finalize=False, context=context, registry=registry)
        except RuntimeError:
            raise
        except Exception as e:
            detail = '%r upgrading from %r to %r' % (e, current_version, target_version)
            yield AuditFailure('upgrade failure', detail, level='ERROR')
            return

        properties['schema_version'] = target_version

    properties['uuid'] = str(context.uuid)
    validated, errors = validate(context.schema, properties, properties)
    for error in errors:
        category = 'validation error'
        path = list(error.path)
        if path:
            category += ': ' + '/'.join(path)
        yield AuditFailure(category, error.message, level='ERROR')
