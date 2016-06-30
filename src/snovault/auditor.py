""" Cross-object data auditing

Schema validation allows for checking values within a single object.
We also need to perform higher order checking between linked objects.
"""

import logging
import venusian
from past.builtins import basestring
from pyramid.view import view_config
from .calculated import calculated_property
from .interfaces import (
    AUDITOR,
    TYPES,
)
from .resources import Item

logger = logging.getLogger(__name__)


def includeme(config):
    config.include('.calculated')
    config.include('.typeinfo')
    config.scan(__name__)
    config.registry[AUDITOR] = Auditor()
    config.add_directive('add_audit_checker', add_audit_checker)
    config.add_request_method(audit, 'audit')


# Same as logging
_levelNames = {
    0: 'NOTSET',
    10: 'DEBUG',
    20: 'INFO',
    30: 'INTERNAL_ACTION',
    40: 'WARNING',
    50: 'NOT_COMPLIANT',
    60: 'ERROR',
    'DEBUG': 10,
    'ERROR': 60,
    'INFO': 20,
    'NOTSET': 0,
    'WARNING': 40,
    'NOT_COMPLIANT': 50,
    'INTERNAL_ACTION': 30,
}


class AuditFailure(Exception):
    def __init__(self, category, detail=None, level=0, path=None, name=None):
        super(AuditFailure, self)
        self.category = category
        self.detail = detail
        if not isinstance(level, int):
            level = _levelNames[level]
        self.level = level
        self.path = path
        self.name = name

    def __json__(self, request=None):
        return {
            'category': self.category,
            'detail': self.detail,
            'level': self.level,
            'level_name': _levelNames[self.level],
            'path': self.path,
            'name': self.name,
        }


class Auditor(object):
    """ Data audit manager
    """
    _order = 0

    def __init__(self):
        self.type_checkers = {}

    def add_audit_checker(self, checker, item_type, condition=None, frame='embedded'):
        checkers = self.type_checkers.setdefault(item_type, [])
        self._order += 1  # consistent execution ordering
        if isinstance(frame, list):
            frame = tuple(sorted(frame))
        checkers.append((self._order, checker, condition, frame))

    def audit(self, request, types, path, **kw):
        if isinstance(types, basestring):
            types = [types]
        checkers = set()
        checkers.update(*(self.type_checkers.get(item_type, ()) for item_type in types))
        errors = []
        system = {
            'request': request,
            'path': path,
            'types': types,
        }
        system.update(kw)
        for order, checker, condition, frame in sorted(checkers):
            if frame is None:
                uri = path
            elif isinstance(frame, basestring):
                uri = '%s@@%s' % (path, frame)
            else:
                uri = '%s@@expand?expand=%s' % (path, '&expand='.join(frame))
            value = request.embed(uri)

            if condition is not None:
                try:
                    if not condition(value, system):
                        continue
                except Exception as e:
                    detail = '%s: %r' % (checker.__name__, e)
                    failure = AuditFailure(
                        'audit condition error', detail, 'ERROR', path, checker.__name__)
                    errors.append(failure.__json__(request))
                    logger.warning('audit condition error auditing %s', path, exc_info=True)
                    continue
            try:
                try:
                    result = checker(value, system)
                except AuditFailure as e:
                    e = e.__json__(request)
                    if e['path'] is None:
                        e['path'] = path
                    e['name'] = checker.__name__
                    errors.append(e)
                    continue
                if result is None:
                    continue
                if isinstance(result, AuditFailure):
                    result = [result]
                for item in result:
                    if isinstance(item, AuditFailure):
                        item = item.__json__(request)
                        if item['path'] is None:
                            item['path'] = path
                        item['name'] = checker.__name__
                        errors.append(item)
                        continue
                    raise ValueError(item)
            except Exception as e:
                detail = '%s: %r' % (checker.__name__, e)
                failure = AuditFailure(
                    'audit script error', detail, 'ERROR', path, checker.__name__)
                errors.append(failure.__json__(request))
                logger.warning('audit script error auditing %s', path, exc_info=True)
                continue
        return errors


# Imperative configuration
def add_audit_checker(config, checker, type_, condition=None, frame='embedded'):
    def callback():
        types = config.registry[TYPES]
        ti = types[type_]
        auditor = config.registry[AUDITOR]
        auditor.add_audit_checker(checker, ti.name, condition, frame)

    config.action(None, callback)


# Declarative configuration
def audit_checker(type_, condition=None, frame='embedded'):
    """ Register an audit checker
    """

    def decorate(checker):
        def callback(scanner, factory_name, factory):
            scanner.config.add_audit_checker(
                checker, type_, condition, frame)

        venusian.attach(checker, callback, category=AUDITOR)
        return checker

    return decorate


def audit(request, types=None, path=None, context=None, **kw):
    auditor = request.registry[AUDITOR]
    if path is None:
        path = request.path
    if context is None:
        context = request.context
    if types is None:
        types = [context.type_info.name] + context.type_info.base_types
    return auditor.audit(
        request=request, types=types, path=path, root=request.root, context=context,
        registry=request.registry, **kw)


# Views
def traversed_path_ids(request, obj, path):
    if isinstance(path, basestring):
        path = path.split('.')
    if not path:
        yield obj if isinstance(obj, basestring) else obj['@id']
        return
    name = path[0]
    remaining = path[1:]
    value = obj.get(name, None)
    if value is None:
        return
    if not isinstance(value, list):
        value = [value]
    for member in value:
        if remaining and isinstance(member, basestring):
            member = request.embed(member, '@@object')
        for item_uri in traversed_path_ids(request, member, remaining):
            yield item_uri


def inherit_audits(request, embedded, embedded_paths):
    audit_paths = {embedded['@id']}
    for embedded_path in embedded_paths:
        audit_paths.update(traversed_path_ids(request, embedded, embedded_path))

    audits = {}
    for audit_path in audit_paths:
        result = request.embed(audit_path, '@@audit-self')
        for audit in result['audit']:
            if audit['level_name'] in audits:
                audits[audit['level_name']].append(audit)
            else:
                audits[audit['level_name']] = [audit]
    return audits


@view_config(context=Item, permission='audit', request_method='GET',
             name='audit-self')
def item_view_audit_self(context, request):
    path = request.resource_path(context)
    types = [context.type_info.name] + context.type_info.base_types
    return {
        '@id': path,
        'audit': request.audit(types=types, path=path),
    }


@view_config(context=Item, permission='audit', request_method='GET',
             name='audit')
def item_view_audit(context, request):
    path = request.resource_path(context)
    properties = request.embed(path, '@@object')
    audit = inherit_audits(request, properties, context.audit_inherit or context.embedded)
    return {
        '@id': path,
        'audit': audit,
    }


@calculated_property(context=Item, category='page', name='audit',
                     condition=lambda request: request.has_permission('audit'))
def audit_property(context, request):
    path = request.resource_path(context)
    return request.embed(path, '@@audit')['audit']
