from collections import defaultdict
from pyramid.decorator import reify
from .interfaces import (
    CALCULATED_PROPERTIES,
    TYPES,
)


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
    def __init__(self, registry, item_type):
        self.types = registry[TYPES]
        self.item_type = item_type

    @reify
    def subtypes(self):
        return [
            k for k, v in self.types.types.items()
            if self.item_type in ([v.item_type] + v.base_types)
        ]


class TypeInfo(AbstractTypeInfo):
    def __init__(self, registry, item_type, factory):
        super(TypeInfo, self).__init__(registry, item_type)
        self.calculated_properties = registry[CALCULATED_PROPERTIES]
        self.factory = factory
        self.base_types = factory.base_types
        self.embedded = factory.embedded

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
        types = [self.item_type] + self.base_types
        for item_type in reversed(types):
            back_rev = self.types.type_back_rev.get(item_type, ())
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
        self.types = {}
        self.abstract = {}
        self.type_back_rev = {}

    def register(self, item_type, factory):
        ti = TypeInfo(self.registry, item_type, factory)
        self.types[item_type] = self.abstract[item_type] = ti
        for base in ti.base_types:
            if base not in self.abstract:
                self.abstract[base] = AbstractTypeInfo(self.registry, base)

        # Calculate the reverse rev map
        for prop_name, spec in factory.rev.items():
            rev_item_type, rel = spec
            back = self.type_back_rev.setdefault(rev_item_type, {}).setdefault(rel, set())
            back.add((item_type, prop_name))

    def __getitem__(self, name):
        return self.types[name]
