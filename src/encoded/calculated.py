import inspect
import venusian
from pyramid.decorator import reify
from pyramid.traversal import find_root


def includeme(config):
    config.registry['calculated_properties'] = CalculatedProperties()
    config.add_directive('add_calculated_property', add_calculated_property)


class ItemNamespace(object):
    def __init__(self, context, request, **kw):
        self.context = context
        self.request = request
        self.__dict__.update(**kw)

    @reify
    def _properties(self):
        return self.context.__json__(self.request)

    @reify
    def root(self):
        return find_root(self.context)

    def __getattr__(self, name):
        context = self.context
        request = self.request
        if name in self._properties:
            value = self._properties[name]
            if name in context.schema_links:
                if isinstance(value, list):
                    value = [
                        request.resource_path(self.root.get_by_uuid(v))
                        for v in value
                    ]
                else:
                    value = request.resource_path(self.root.get_by_uuid(value))
            setattr(self, name, value)
            return value
        if name in context.rev:
            value = context.get_rev_links(name)
            value = [
                request.resource_path(self.root.get_by_uuid(v))
                for v in value
            ]
            setattr(self, name, value)
            return value
        raise AttributeError(name)

    def __call__(self, fn, args):
        kw = {}
        for name in args:
            try:
                kw[name] = getattr(self, name)
            except AttributeError:
                pass
        return fn(**kw)


class CalculatedProperties(dict):
    def props_for(self, cls):
        props = {}
        for item_type in reversed([cls.item_type] + cls.base_types):
            props.update(self.get(item_type, {}))
        return props

    def register(self, fn, name, item_type, condition=None, schema=None, attr=None):
        if not isinstance(item_type, str):
            item_type = item_type.item_type
        self.setdefault(item_type, {})[name] = CalculatedProperty(fn, name, condition, schema, attr)


class CalculatedProperty(object):
    condition_args = None

    def __init__(self, fn, name, condition=None, schema=None, attr=None):
        self.fn = fn
        self.attr = attr
        self.name = name
        self.condition_fn = condition

        argspec = inspect.getargspec(fn)
        if argspec.keywords is not None:
            raise TypeError('Cannot register calculated property with keyword args')
        if argspec.varargs is not None:
            raise TypeError('Cannot register calculated property with varargs')
        if attr is not None and not isinstance(fn, staticmethod):
            self.args = argspec.args[1:]
        else:
            self.args = argspec.args

        if condition is not None:
            argspec = inspect.getargspec(condition)
            if argspec.keywords is not None:
                raise TypeError('Cannot register calculated property condition with keyword args')
            if argspec.varargs is not None:
                raise TypeError('Cannot register calculated property condition with varargs')
            self.condition_args = argspec.args

        if schema is not None:
            if 'default' in schema:
                raise ValueError('schema may not specify default for calculated property')
            schema = schema.copy()
            schema['calculatedProperty'] = True
        self.schema = schema

    def condition(self, ns):
        if self.condition_fn is None:
            return True
        return ns(self.condition_fn, self.condition_args)

    def __call__(self, ns):
        if self.attr:
            fn = getattr(ns.context, self.attr)
        else:
            fn = self.fn
        return ns(fn, self.args)


# Imperative configuration
def add_calculated_property(config, fn, name, item_type, condition=None, schema=None, attr=None):
    calculated_properties = config.registry['calculated_properties']
    config.action(
        ('calculated_property', item_type, name),
        calculated_properties.register,
        (fn, name, item_type, condition, schema, attr),
    )


# Declarative configuration
def calculated_property(**settings):
    """ Register a calculated property
    """

    def decorate(wrapped):
        def callback(scanner, factory_name, factory):
            if settings.get('item_type') is None:
                settings['item_type'] = factory
            if settings.get('name') is None:
                settings['name'] = factory_name
            scanner.config.add_calculated_property(wrapped, **settings)

        info = venusian.attach(wrapped, callback, category='calculated_property')

        if info.scope == 'class':
            # if the decorator was attached to a method in a class, or
            # otherwise executed at class scope, we need to set an
            # 'attr' into the settings if one isn't already in there
            if settings.get('attr') is None:
                settings['attr'] = wrapped.__name__
            if settings.get('name') is None:
                settings['name'] = wrapped.__name__

        elif settings.get('item_type') is None:
            raise TypeError('must supply item_type for plain function')

        return wrapped

    return decorate


def calculate_properties(context, request, **kw):
    calculated_properties = request.registry['calculated_properties']
    props = calculated_properties.props_for(type(context))
    ns = ItemNamespace(context, request, **kw)
    return {
        name: prop(ns)
        for name, prop in props.items()
        if prop.condition(ns)
    }
