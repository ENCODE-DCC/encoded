from collections import OrderedDict
from pkg_resources import resource_stream
import json
from jsonschema import (
    FormatChecker,
    Draft4Validator
)
import uuid
import re


class SchemaValidator(Draft4Validator):
    pass


def load_schema(filename):
    schema = json.load(resource_stream(__name__, 'schemas/' + filename))
    return SchemaValidator(schema, serialize=True)


def validate_request(schema, request, data=None):
    if data is None:
        data = request.json
    validated, errors = schema.serialize(data)
    for error in errors:
        request.errors.add('body', list(error.path), error.message)
    if not errors:
        request.validated.update(validated)


def schema_validator(filename):
    schema = load_schema(filename)

    def validator(request):
        return validate_request(schema, request)

    return validator


def basic_schema(value, null_type='string', template=None, nullable=all,
                 _key=None):

    # recursing paramaters
    params = locals().copy()
    del params['value']
    del params['_key']

    if template is None:
        template = OrderedDict([
            ('title', ''),
            ('description', ''),
            ('default', None),
        ])

    def templated(data):
        out = template.copy()
        out.update(data)
        if nullable is all or _key in nullable:
            if isinstance(out['type'], basestring):
                out['type'] = [out['type']]
            if 'null' not in out['type']:
                out['type'].append('null')
        return out

    if value is None:
        return templated({'type': null_type})
    elif isinstance(value, basestring):
        return templated({'type': 'string'})
    elif isinstance(value, bool):
        return templated({'type': 'boolean'})
    elif isinstance(value, int):
        return templated({'type': 'integer'})
    elif isinstance(value, float):
        return templated({'type': 'number'})
    elif isinstance(value, dict):
        key_prefix = _key + '.' if _key else ''
        properties = OrderedDict(
            (k, basic_schema(v, _key=(key_prefix + k), **params))
            for k, v in sorted(value.items()))
        return templated({
            'type': 'object',
            'properties': properties,
        })
    elif isinstance(value, list):
        _key = _key + '[]' if _key else '[]'
        if value:
            item = value[0]
        else:
            item = None
        return templated({
            'type': 'array',
            'items': basic_schema(item, _key=_key, **params),
        })
    else:
        raise ValueError(value)


@FormatChecker.cls_checks("uuid")
def is_uuid(instance):
    try:
        value = uuid.UUID(instance)
    except:
        return False
    return True


@FormatChecker.cls_checks("accession")
def is_accession(instance):
    acc_regex = re.compile('^ENC(BS|DO|LB|DS|AB)[0-9][0-9][0-9][A-Z][A-Z][A-Z]$')
    if acc_regex.match(instance):
        return True
    return False
