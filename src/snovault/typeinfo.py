from collections import defaultdict
from functools import reduce
from pyramid.decorator import reify
from .interfaces import (
    CALCULATED_PROPERTIES,
    TYPES,
)
from .schema_utils import combine_schemas


def includeme(config):
    registry = config.registry
    registry[TYPES] = TypesTool(registry)


def extract_schema_links(schema):
    if not schema:
        return
    for key, prop in schema['properties'].items():
        if 'items' in prop:
            prop = prop['items']
        if 'properties' in prop:
            for path in extract_schema_links(prop):
                yield (key,) + path
        elif 'linkTo' in prop:
            yield (key,)


class AbstractTypeInfo(object):
    factory = None

    def __init__(self, registry, name):
        self.types = registry[TYPES]
        self.name = name

    @reify
    def subtypes(self):
        return [
            ti.name for ti in self.types.by_item_type.values()
            if self.name in ([ti.name] + ti.base_types)
        ]

    @reify
    def schema(self):
        subschemas = (self.types[name].schema for name in self.subtypes)
        return reduce(combine_schemas, subschemas)


class TypeInfo(AbstractTypeInfo):
    def __init__(self, registry, item_type, factory):
        super(TypeInfo, self).__init__(registry, factory.__name__)
        self.registry = registry
        self.item_type = item_type
        self.factory = factory
        self.base_types = factory.base_types
        self.embedded = factory.embedded

    @reify
    def calculated_properties(self):
        return self.registry[CALCULATED_PROPERTIES]

    @reify
    def schema_version(self):
        try:
            return self.factory.schema['properties']['schema_version']['default']
        except (KeyError, TypeError):
            return None

    @reify
    def schema_links(self):
        return sorted('.'.join(path) for path in extract_schema_links(self.factory.schema))

    @reify
    def schema_keys(self):
        if not self.factory.schema:
            return ()
        keys = defaultdict(list)
        for key, prop in self.factory.schema['properties'].items():
            uniqueKey = prop.get('items', prop).get('uniqueKey')
            if uniqueKey is True:
                uniqueKey = '%s:%s' % (self.factory.item_type, key)
            if uniqueKey is not None:
                keys[uniqueKey].append(key)
        return keys

    @reify
    def merged_back_rev(self):
        merged = {}
        types = [self.name] + self.base_types
        for name in reversed(types):
            back_rev = self.types.type_back_rev.get(name, ())
            merged.update(back_rev)
        return merged

    @reify
    def schema(self):
        props = self.calculated_properties.props_for(self.factory)
        schema = self.factory.schema or {'type': 'object', 'properties': {}}
        schema = schema.copy()
        schema['properties'] = schema['properties'].copy()
        for name, prop in props.items():
            if prop.schema is not None:
                schema['properties'][name] = prop.schema
        return schema

    @reify
    def schema_rev_links(self):
        revs = {}
        for key, prop in self.schema['properties'].items():
            linkFrom = prop.get('linkFrom', prop.get('items', {}).get('linkFrom'))
            if linkFrom is None:
                continue
            linkType, linkProp = linkFrom.split('.')
            revs[key] = linkType, linkProp
        return revs


class TypesTool(object):
    def __init__(self, registry):
        self.registry = registry
        self.by_item_type = {}
        self.abstract = {}
        self.type_back_rev = {}
        self.all = {}

    def register(self, factory):
        name = factory.__name__
        item_type = factory.item_type or name
        ti = TypeInfo(self.registry, item_type, factory)
        self.all[ti.item_type] = self.by_item_type[ti.item_type] = ti
        self.all[ti.name] = self.abstract[ti.name] = ti
        self.all[ti.factory] = ti
        for base in ti.base_types:
            self.register_abstract(base)

        # Calculate the reverse rev map
        for prop_name, spec in factory.rev.items():
            rev_type_name, rel = spec
            back = self.type_back_rev.setdefault(rev_type_name, {}).setdefault(rel, set())
            back.add((ti.name, prop_name))

        return ti

    def register_abstract(self, name):
        ti = self.abstract.get(name)
        if ti is None:
            ti = AbstractTypeInfo(self.registry, name)
            self.all[name] = self.abstract[name] = ti
        return ti

    def __contains__(self, name):
        return name in self.all

    def __getitem__(self, name):
        return self.all[name]
