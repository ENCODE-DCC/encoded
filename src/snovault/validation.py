from pyramid.config.views import DefaultViewMapper
from pyramid.httpexceptions import (
    HTTPError,
    HTTPBadRequest,
    HTTPForbidden,
    HTTPPreconditionFailed,
    HTTPServiceUnavailable,
    HTTPUnprocessableEntity,
)
from past.builtins import basestring
from pyramid.util import LAST
from sqlalchemy.exc import InternalError
import simplejson as json


def includeme(config):
    config.add_request_method(lambda request: {}, 'validated', reify=True)
    config.add_request_method(lambda request: Errors(), 'errors', reify=True)
    config.add_view(view=failed_validation, context=ValidationFailure)
    config.add_view(view=http_error, context=HTTPError)
    config.add_view(view=database_is_read_only, context=InternalError)
    config.add_view(view=refresh_session, context=CSRFTokenError)
    config.add_view(view=refresh_session, context=HTTPForbidden)
    config.add_view(view=refresh_session, context=HTTPPreconditionFailed)
    config.add_view(view=jsondecode_error, context=json.JSONDecodeError)
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
            if name is None:
                name = []
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
        '@type': [type(exc).__name__, 'Error'],
        'status': 'error',
        'code': exc.code,
        'title': exc.title,
        'description': exc.explanation,
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
    request.response.headerlist.extend(exc.headerlist)
    result = {
        '@type': [type(exc).__name__, 'Error'],
        'status': 'error',
        'code': exc.code,
        'title': exc.title,
        'description': exc.explanation,
    }
    if exc.detail is not None:
        result['detail'] = exc.detail
    if exc.comment is not None:
        result['comment'] = exc.comment
    return result


def database_is_read_only(exc, request):
    if 'read-only transaction' not in str(exc):
        raise exc
    return http_error(HTTPServiceUnavailable(), request)


def jsondecode_error(exc, request):
    try:
        request.json
    except ValueError as e:
        return http_error(HTTPBadRequest(str(e)), request)
    else:
        raise exc


class CSRFTokenError(HTTPBadRequest):
    pass


def refresh_session(exc, request):
    request.session.get_csrf_token()
    request.session.changed()
    return http_error(exc, request)


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
