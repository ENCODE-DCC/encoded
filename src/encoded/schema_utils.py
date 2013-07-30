from collections import OrderedDict
from pkg_resources import resource_stream
from pyramid.security import has_permission
from pyramid.threadlocal import get_current_request
from pyramid.traversal import find_resource
import json
from jsonschema import (
    Draft4Validator,
    FormatChecker,
    RefResolver,
)
from jsonschema.exceptions import ValidationError
from uuid import UUID

import posixpath

from .schema_formats import is_accession


def local_handler(uri):
    base, filename = posixpath.split(uri)
    if base != '/profiles':
        raise KeyError(uri)
    schema = json.load(resource_stream(__name__, 'schemas/' + filename))
    return schema


def mixinProperties(schema, resolver):
    mixins = schema.get('mixinProperties')
    if mixins is None:
        return schema
    properties = {}
    bases = []
    for mixin in reversed(mixins):
        ref = mixin.get('$ref')
        if ref is not None:
            with resolver.resolving(ref) as resolved:
                mixin = resolved
        bases.append(mixin)
    bases.append(schema.get('properties', {}))
    for base in bases:
        for name, base_prop in base.iteritems():
            prop = properties.setdefault(name, {})
            for k, v in base_prop.iteritems():
                if k not in prop:
                    prop[k] = v
                    continue
                if prop[k] == v:
                    continue
                raise ValueError('Schema mixin conflict for %s/%s' % (name, k))
    schema['properties'] = properties
    return schema


def lookup_resource(root, base, path):
    try:
        UUID(path)
    except ValueError:
        pass
    else:
        item = root.get_by_uuid(path)
        if item is None:
            raise KeyError(path)
        return item
    if is_accession(path):
        item = root.get_by_unique_key('accession', path)
        if item is None:
            raise KeyError(path)
        return item
    if ':' in path:
        item = root.get_by_unique_key('alias', path)
        if item is None:
            raise KeyError(path)
        return item
    return find_resource(base, path)


def linkTo(validator, linkTo, instance, schema):
    # avoid circular import
    from .contentbase import Item

    if not validator.is_type(instance, "string"):
        return

    request = get_current_request()
    if validator.is_type(linkTo, "string"):
        base = request.root.by_item_type.get(linkTo, request.context)
        linkTo = [linkTo]
    elif validator.is_type(linkTo, "array"):
        base = request.context  # XXX
    else:
        raise Exception("Bad schema")  # raise some sort of schema error
    try:
        item = lookup_resource(request.root, base, instance.encode('utf-8'))
        if item is None:
            raise KeyError()
    except KeyError:
        error = "%r not found" % instance
        yield ValidationError(error)
        return
    if not isinstance(item, Item):
        error = "%r is not a linkable resource" % instance
        yield ValidationError(error)
        return
    if not set([item.item_type] + item.base_types).intersection(set(linkTo)):
        reprs = (repr(it) for it in linkTo)
        error = "%r is not of type %s" % (instance, ", ".join(reprs))
        yield ValidationError(error)
        return

    linkEnum = schema.get('linkEnum')
    if linkEnum is not None:
        if not validator.is_type(linkEnum, "array"):
            raise Exception("Bad schema")
        if not any(UUID(enum_uuid) == item.uuid for enum_uuid in linkEnum):
            reprs = (repr(it) for it in linkTo)
            error = "%r is not one of %s" % (instance, ", ".join(reprs))
            yield ValidationError(error)
            return

    # And normalize the value to a uuid
    if validator._serialize:
        validator._validated[-1] = str(item.uuid)


def permission(validator, permission, instance, schema):
    if not validator.is_type(permission, "string"):
        raise Exception("Bad schema")  # raise some sort of schema error

    request = get_current_request()
    context = request.context
    has_permission(permission, context, request)


class SchemaValidator(Draft4Validator):
    VALIDATORS = Draft4Validator.VALIDATORS.copy()
    VALIDATORS['linkTo'] = linkTo
    VALIDATORS['permission'] = permission


format_checker = FormatChecker()

def load_schema(filename):
    schema = json.load(resource_stream(__name__, 'schemas/' + filename))
    resolver = RefResolver.from_schema(schema, handlers={'': local_handler})
    schema = mixinProperties(schema, resolver)

    # SchemaValidator is not thread safe for now
    SchemaValidator(schema, resolver=resolver, serialize=True)
    return schema


def validate_request(schema, request, data=None):
    resolver = RefResolver.from_schema(schema, handlers={'': local_handler})
    sv = SchemaValidator(schema, resolver=resolver, serialize=True, format_checker=format_checker)
    if data is None:
        data = request.json
    validated, errors = sv.serialize(data)
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
