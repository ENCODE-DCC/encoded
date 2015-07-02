from uuid import UUID
from .schema_utils import validate_request
from .validation import ValidationFailure


# No-validation validators


def no_validate_item_content_post(context, request):
    data = request.json
    request.validated.update(data)


def no_validate_item_content_put(context, request):
    data = request.json
    if 'uuid' in data:
        if UUID(data['uuid']) != context.uuid:
            msg = 'uuid may not be changed'
            raise ValidationFailure('body', ['uuid'], msg)
    request.validated.update(data)


def no_validate_item_content_patch(context, request):
    data = context.properties.copy()
    data.update(request.json)
    if 'uuid' in data:
        if UUID(data['uuid']) != context.uuid:
            msg = 'uuid may not be changed'
            raise ValidationFailure('body', ['uuid'], msg)
    request.validated.update(data)


# Schema checking validators


def validate_item_content_post(context, request):
    data = request.json
    validate_request(context.type_info.schema, request, data)


def validate_item_content_put(context, request):
    data = request.json
    schema = context.type_info.schema
    if 'uuid' in data and UUID(data['uuid']) != context.uuid:
        msg = 'uuid may not be changed'
        raise ValidationFailure('body', ['uuid'], msg)
    current = context.upgrade_properties().copy()
    current['uuid'] = str(context.uuid)
    validate_request(schema, request, data, current)


def validate_item_content_patch(context, request):
    data = context.upgrade_properties().copy()
    if 'schema_version' in data:
        del data['schema_version']
    data.update(request.json)
    schema = context.type_info.schema
    if 'uuid' in data and UUID(data['uuid']) != context.uuid:
        msg = 'uuid may not be changed'
        raise ValidationFailure('body', ['uuid'], msg)
    current = context.upgrade_properties().copy()
    current['uuid'] = str(context.uuid)
    validate_request(schema, request, data, current)
