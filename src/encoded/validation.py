from pyramid.config.views import DefaultViewMapper
from pyramid.events import NewRequest
from pyramid.httpexceptions import HTTPUnprocessableEntity


def includeme(config):
    config.add_subscriber(wrap_request, NewRequest)
    config.add_view(view=failed_validation, context=ValidationFailure)
    config.add_view_predicate('validators', ValidatorsPredicate)


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
        return 'validators = %r' % self.validators

    phash = text

    def __call__(self, context, request):
        for validator in self.validators:
            validator(context, request)
        if request.errors:
            raise ValidationFailure()
        return True
