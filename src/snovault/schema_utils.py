from pyramid.path import (
    AssetResolver,
    caller_package,
)
from pyramid.security import has_permission
from pyramid.threadlocal import get_current_request
from pyramid.traversal import find_resource
import json
import codecs
import collections
import copy
from jsonschema_serialize_fork import (
    Draft4Validator,
    FormatChecker,
    RefResolver,
)
from jsonschema_serialize_fork.exceptions import ValidationError
from uuid import UUID
from .util import ensurelist


SERVER_DEFAULTS = {}


def server_default(func):
    SERVER_DEFAULTS[func.__name__] = func


class NoRemoteResolver(RefResolver):
    def resolve_remote(self, uri):
        raise ValueError('Resolution disallowed for: %s' % uri)


def mixinProperties(schema, resolver):
    mixins = schema.get('mixinProperties')
    if mixins is None:
        return schema
    properties = collections.OrderedDict()
    bases = []
    for mixin in reversed(mixins):
        ref = mixin.get('$ref')
        if ref is not None:
            with resolver.resolving(ref) as resolved:
                mixin = resolved
        bases.append(mixin)
    for base in bases:
        for name, base_prop in base.items():
            prop = properties.setdefault(name, {})
            for k, v in base_prop.items():
                if k not in prop:
                    prop[k] = v
                    continue
                if prop[k] == v:
                    continue
                raise ValueError('Schema mixin conflict for %s/%s' % (name, k))
    # Allow schema properties to override
    base = schema.get('properties', {})
    for name, base_prop in base.items():
        prop = properties.setdefault(name, {})
        for k, v in base_prop.items():
            prop[k] = v
    schema['properties'] = properties
    return schema


def linkTo(validator, linkTo, instance, schema):
    # avoid circular import
    from snovault import Item, COLLECTIONS

    if not validator.is_type(instance, "string"):
        return

    request = get_current_request()
    collections = request.registry[COLLECTIONS]
    if validator.is_type(linkTo, "string"):
        base = collections.get(linkTo, request.root)
        linkTo = [linkTo] if linkTo else []
    elif validator.is_type(linkTo, "array"):
        base = request.root
    else:
        raise Exception("Bad schema")  # raise some sort of schema error
    try:
        item = find_resource(base, instance.replace(':', '%3A'))
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
    if linkTo and not set([item.type_info.name] + item.base_types).intersection(set(linkTo)):
        reprs = (repr(it) for it in linkTo)
        error = "%r is not of type %s" % (instance, ", ".join(reprs))
        yield ValidationError(error)
        return

    linkEnum = schema.get('linkEnum')
    if linkEnum is not None:
        if not validator.is_type(linkEnum, "array"):
            raise Exception("Bad schema")
        if not any(UUID(enum_uuid) == item.uuid for enum_uuid in linkEnum):
            reprs = ', '.join(repr(it) for it in linkTo)
            error = "%r is not one of %s" % (instance, reprs)
            yield ValidationError(error)
            return

    if schema.get('linkSubmitsFor'):
        userid = None
        for principal in request.effective_principals:
            if principal.startswith('userid.'):
                userid = principal[len('userid.'):]
                break
        if userid is not None:
            user = request.root[userid]
            submits_for = user.upgrade_properties().get('submits_for')
            if (submits_for is not None and
                    not any(UUID(uuid) == item.uuid for uuid in submits_for) and
                    not request.has_permission('submit_for_any')):
                error = "%r is not in user submits_for" % instance
                yield ValidationError(error)
                return

    # And normalize the value to a uuid
    if validator._serialize:
        validator._validated[-1] = str(item.uuid)


def linkFrom(validator, linkFrom, instance, schema):
    # avoid circular import
    from snovault import Item, TYPES, COLLECTIONS
    request = get_current_request()
    collections = request.registry[COLLECTIONS]

    linkType, linkProp = linkFrom.split('.')
    if validator.is_type(instance, "string"):
        base = collections[linkType]
        try:
            item = find_resource(base, instance.replace(':', '%3A'))
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
        if linkType not in set([item.type_info.name] + item.type_info.base_types):
            error = "%r is not of type %s" % (instance, repr(linkType))
            yield ValidationError(error)
            return
        pass
    else:
        path = instance.get('@id')
        if validator._serialize:
            lv = len(validator._validated)
        if '@id' in instance:
            del instance['@id']

        # treat the link property as not required
        # because it will be filled in when the child is created/updated
        subschema = request.registry[TYPES][linkType].schema
        subschema = copy.deepcopy(subschema)
        if linkProp in subschema['required']:
            subschema['required'].remove(linkProp)

        for error in validator.descend(instance, subschema):
            yield error

        if validator._serialize:
            validated_instance = validator._validated[lv]
            del validator._validated[lv:]
            if path is not None:
                item = find_resource(request.root, path.replace(':', '%3A'))
                validated_instance['uuid'] = str(item.uuid)
            elif 'uuid' in validated_instance:  # where does this come from?
                del validated_instance['uuid']
            validator._validated[-1] = validated_instance


class IgnoreUnchanged(ValidationError):
    pass


def requestMethod(validator, requestMethod, instance, schema):
    if validator.is_type(requestMethod, "string"):
        requestMethod = [requestMethod]
    elif not validator.is_type(requestMethod, "array"):
        raise Exception("Bad schema")  # raise some sort of schema error

    request = get_current_request()
    if request.method not in requestMethod:
        reprs = ', '.join(repr(it) for it in requestMethod)
        error = "request method %r is not one of %s" % (request.method, reprs)
        yield IgnoreUnchanged(error)


def permission(validator, permission, instance, schema):
    if not validator.is_type(permission, "string"):
        raise Exception("Bad schema")  # raise some sort of schema error

    request = get_current_request()
    context = request.context
    if not has_permission(permission, context, request):
        error = "permission %r required" % permission
        yield IgnoreUnchanged(error)


VALIDATOR_REGISTRY = {}


def validators(validator, validators, instance, schema):
    if not validator.is_type(validators, "array"):
        raise Exception("Bad schema")  # raise some sort of schema error

    for validator_name in validators:
        validate = VALIDATOR_REGISTRY.get(validator_name)
        if validate is None:
            raise Exception('Validator %s not found' % validator_name)
        error = validate(instance, schema)
        if error:
            yield ValidationError(error)


def calculatedProperty(validator, linkTo, instance, schema):
    yield ValidationError('submission of calculatedProperty disallowed')


class SchemaValidator(Draft4Validator):
    VALIDATORS = Draft4Validator.VALIDATORS.copy()
    VALIDATORS['calculatedProperty'] = calculatedProperty
    VALIDATORS['linkTo'] = linkTo
    VALIDATORS['linkFrom'] = linkFrom
    VALIDATORS['permission'] = permission
    VALIDATORS['requestMethod'] = requestMethod
    VALIDATORS['validators'] = validators
    SERVER_DEFAULTS = SERVER_DEFAULTS


format_checker = FormatChecker()


def load_schema(filename):
    if isinstance(filename, dict):
        schema = filename
        resolver = NoRemoteResolver.from_schema(schema)
    else:
        utf8 = codecs.getreader("utf-8")
        asset = AssetResolver(caller_package()).resolve(filename)
        schema = json.load(utf8(asset.stream()),
                           object_pairs_hook=collections.OrderedDict)
        resolver = RefResolver('file://' + asset.abspath(), schema)
    schema = mixinProperties(schema, resolver)

    # SchemaValidator is not thread safe for now
    SchemaValidator(schema, resolver=resolver, serialize=True)
    return schema


def validate(schema, data, current=None):
    resolver = NoRemoteResolver.from_schema(schema)
    sv = SchemaValidator(schema, resolver=resolver, serialize=True, format_checker=format_checker)
    validated, errors = sv.serialize(data)

    filtered_errors = []
    for error in errors:
        # Possibly ignore validation if it results in no change to data
        if current is not None and isinstance(error, IgnoreUnchanged):
            current_value = current
            try:
                for key in error.path:
                    current_value = current_value[key]
            except Exception:
                pass
            else:
                validated_value = validated
                for key in error.path:
                    validated_value = validated_value[key]
                if validated_value == current_value:
                    continue
        filtered_errors.append(error)

    return validated, filtered_errors


def validate_request(schema, request, data=None, current=None):
    if data is None:
        data = request.json

    validated, errors = validate(schema, data, current)
    for error in errors:
        request.errors.add('body', list(error.path), error.message)

    if not errors:
        request.validated.update(validated)


def schema_validator(filename):
    schema = load_schema(filename)

    def validator(request):
        return validate_request(schema, request)

    return validator


def combine_schemas(a, b):
    if a == b:
        return a
    if not a:
        return b
    if not b:
        return a
    combined = {}
    for name in set(a.keys()).intersection(b.keys()):
        if a[name] == b[name]:
            combined[name] = a[name]
        elif name == 'type':
            combined[name] = sorted(set(ensurelist(a[name]) + ensurelist(b[name])))
        elif name == 'properties':
            combined[name] = {}
            for k in set(a[name].keys()).intersection(b[name].keys()):
                combined[name][k] = combine_schemas(a[name][k], b[name][k])
            for k in set(a[name].keys()).difference(b[name].keys()):
                combined[name][k] = a[name][k]
            for k in set(b[name].keys()).difference(a[name].keys()):
                combined[name][k] = b[name][k]
        elif name == 'items':
            combined[name] = combine_schemas(a[name], b[name])
        elif name in ('boost_values', 'columns'):
            combined[name] = {}
            combined[name].update(a[name])
            combined[name].update(b[name])
    for name in set(a.keys()).difference(b.keys(), ['facets']):
        combined[name] = a[name]
    for name in set(b.keys()).difference(a.keys(), ['facets']):
        combined[name] = b[name]
    return combined
