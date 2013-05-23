from pyramid.config.views import DefaultViewMapper
from pyramid.events import NewRequest
from pyramid.httpexceptions import (
    HTTPError,
    HTTPUnprocessableEntity,
)
from pyramid.util import LAST


def includeme(config):
    config.add_subscriber(wrap_request, NewRequest)
    config.add_view(view=failed_validation, context=ValidationFailure)
    config.add_view(view=http_error, context=HTTPError)
    config.add_view_predicate('validators', ValidatorsPredicate, weighs_more_than=LAST)


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

    def __init__(self, location=None, name=None, description=None, **kw):
        HTTPUnprocessableEntity.__init__(self)
        if location is None:
            assert name is None and description is None and not kw
            self.detail = None
        else:
            self.detail = dict(location=location, name=name,
                               description=description, **kw)


def failed_validation(exc, request):
    # Clear any existing response
    if 'response' in vars(request):
        del request.response
    request.response.status = exc.status
    errors = list(request.errors)
    if exc.detail is not None:
        errors.append(exc.detail)
    result = {
        'status': 'error',
        'code': exc.code,
        'title': exc.title,
        'explanation': exc.explanation,
        'errors': errors,
    }
    if exc.comment is not None:
        result['comment'] = exc.comment
    return result


def http_error(exc, request):
    # Clear any existing response
    if 'response' in vars(request):
        del request.response
    request.response.status = exc.status
    result = {
        'status': 'error',
        'code': exc.code,
        'title': exc.title,
        'explanation': exc.explanation,
    }
    if exc.detail is not None:
        result['detail'] = exc.detail
    if exc.comment is not None:
        result['comment'] = exc.comment
    return result


def prepare_validators(validators):
    """Allow validators to have multiple signatures like views
    """
    prepared = []
    mapper = DefaultViewMapper()
    for validator in validators:
        if isinstance(validator, basestring):
            # XXX should support dotted names here
            raise NotImplemented
        validator = mapper(validator)
        prepared.append(validator)
    return tuple(prepared)


class ValidatorsPredicate(object):
    def __init__(self, val, config):
        self.validators = prepare_validators(val)

    def text(self):
        return 'validators = %r' % (self.validators,)

    def phash(self):
        # Return a constant to ensure views discriminated only by validators
        # may not be registered.
        return 'validators'

    def __call__(self, context, request):
        for validator in self.validators:
            validator(context, request)
        if request.errors:
            raise ValidationFailure()
        return True
