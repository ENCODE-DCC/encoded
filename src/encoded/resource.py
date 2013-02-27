"""This module is heavily inspired by the resource functionality in cornice_.

It is largely reimplemented using more recent Pyramid functionality, though a
small amount of code is directly copied.

With this module, a resource class is both a factory and a view, allowing
the `__acl__` attribute to be set on the resource class.

.. _cornice: http://cornice.readthedocs.org
"""

import inspect
import venusian

from pyramid.config.views import DefaultViewMapper
from pyramid.events import NewRequest
from pyramid.httpexceptions import HTTPUnprocessableEntity
from pyramid.view import view_config


def includeme(config):
    config.add_subscriber(wrap_request, NewRequest)
    config.add_view(view=failed_validation, context=ValidationFailure)


class ContextViewMapper(object):
    """Look up view as an attribute on the context.

    Expects a combined view / factory class
    """
    def __init__(self, **kw):
        self.attr = kw.get('attr')

    def __call__(self, view=None):
        if view is not None and not inspect.isclass(view):
            raise ValueError('Expected a class', view)
        attr = self.attr

        def mapped_view(context, request):
            request.__view__ = context
            if attr is None:
                response = context()
            else:
                response = getattr(context, attr)()
            return response

        #mapped_view.__text__ = 'method %s of %s' % (
        #    self.attr or '__call__', object_description(view))
        return mapped_view


class Errors(list):
    """Holds Request errors
    """

    def add(self, location, name=None, description=None, **kw):
        """Registers a new error."""
        self.append(dict(
            location=location,
            name=name,
            description=description, **kw))

    @classmethod
    def from_list(cls, obj):
        """Transforms a python list into an `Errors` instance"""
        errors = cls()
        for error in obj:
            errors.add(**error)
        return errors


def wrap_request(event):
    """Adds a "validated" dict and a custom "errors" object to
    the request object if they don't already exists
    """
    request = event.request
    if not hasattr(request, 'validated'):
        setattr(request, 'validated', {})

    if not hasattr(request, 'errors'):
        setattr(request, 'errors', Errors())


class ValidationFailure(HTTPUnprocessableEntity):
    """Raise on validation failure
    """
    explanation = 'Failed validation'


def failed_validation(exc, request):
    request.response.status_int = exc.code
    return {
        'status': 'error',
        'errors': list(request.errors),
        }


def prepare_validators(validators, klass):
    """Allow validators to have multiple signatures like views
    """
    prepared = []
    for validator in validators:
        if isinstance(validator, basestring):
            # XXX should support dotted names here
            validator = ContextViewMapper(attr=validator)(klass)
        else:
            validator = DefaultViewMapper()(validator)
        prepared.append(validator)
    return tuple(prepared)


def validation_decorator_factory(**args):
    """Wrap a view with validation checks.
    """
    def wrap_view(view):
        validators = prepare_validators(
            args.get('validators', ()), args.get('klass'))

        def wrapper(context, request):
            # the validators can either be a list of callables or contain some
            # non-callable values. In which case we want to resolve them using
            # the object if any
            for validator in validators:
                validator(context, request)

            # only call the view if we don't have validation errors
            if len(request.errors) == 0:
                response = view(context, request)

            # check for errors and return them if any
            if len(request.errors) > 0:
                # XXX need some rendering support somewhere
                raise ValidationFailure()

            return response

        return wrapper
    return wrap_view


class resource(object):
    """Class decorator to declare resources.

    All the methods of this class named by the name of HTTP resources
    will be used as such. You can also prefix them by "collection_" and they
    will be treated as HTTP methods for the given collection route pattern
    (collection_pattern), if any.

    Here is an example::

        @resource(collection_pattern='/users', pattern='/users/{id}')

    The class is used as the factory.

    """
    http_verbs = ('head', 'get', 'post', 'put', 'delete', 'options', 'patch')
    venusian = venusian

    def __init__(self, **route_settings):
        self.__dict__.update(route_settings)

    def __call__(self, klass):
        settings = self.__dict__.copy()
        depth = settings.pop('_depth', 0)
        default_route_name = settings.pop('name', klass.__name__.lower())
        has_collection = any(key.startswith('collection_') for key in settings)

        if has_collection:
            prefixes = ('collection_', '')
        else:
            prefixes = ('',)

        # First register the routes
        routes = {}
        for prefix in prefixes:
            # get clean route arguments
            route_args = routes[prefix] = {}
            for k, v in list(settings.items()):
                if k.startswith('collection_'):
                    if prefix == 'collection_':
                        route_args[k[len(prefix):]] = v
                elif k not in route_args:
                    route_args[k] = v

            # Set the factory to the klass
            if 'factory' in route_args:
                factory = route_args['factory']
                if isinstance(factory, basestring) and '.' not in factory:
                    route_args['factory'] = getattr(klass, factory)
            else:
                route_args['factory'] = klass

            route_name = route_args.setdefault('name',
                    prefix + default_route_name)

            # Set __route__ and __collection_route__ on the klass
            setattr(klass, '__%sroute__' % prefix, route_name)

        def callback(context, name, ob):
            config = context.config.with_package(info.module)
            for route_args in routes.values():
                config.add_route(**route_args)

        info = self.venusian.attach(klass, callback, category='pyramid',
                                    depth=depth + 1)

        for prefix in prefixes:
            route_name = routes[prefix]['name']

            # initialize views
            for verb in self.http_verbs:

                view_attr = prefix + verb
                meth = getattr(klass, view_attr, None)
                if meth is None:
                    continue

                # if the method has a __views__ arguments, then it had
                # been decorated by a @view decorator. get back the name of
                # the decorated method so we can register it properly
                views = getattr(meth, '__views__', [])
                if views:
                    for view_args in views:
                        view_args = view_args.copy()
                        validators = view_args.pop('validators', ())
                        validate_view = validation_decorator_factory(
                            validators=validators, klass=klass)
                        view_config(
                            route_name=route_name,
                            request_method=verb.upper(),
                            attr=view_attr,
                            mapper=ContextViewMapper,
                            decorator=(validate_view,),
                            _depth=depth + 1,
                            **view_args)(klass)
                else:
                    validate_view = validation_decorator_factory(
                        validators=(), klass=klass)
                    view_config(
                        route_name=route_name,
                        request_method=verb.upper(),
                        attr=view_attr,
                        mapper=ContextViewMapper,
                        decorator=(validate_view,),
                        _depth=depth + 1,
                        )(klass)

        return klass


def view(**kw):
    """Method decorator to store view arguments when defining a resource with
    the @resource class decorator
    """
    def wrapper(func):
        # store view argument to use them later in @resource
        views = getattr(func, '__views__', None)
        if views is None:
            views = []
            setattr(func, '__views__', views)
        views.append(kw)
        return func
    return wrapper
