""" Cross-object data auditing

Schema validation allows for checking values within a single object.
We also need to perform higher order checking between linked objects.
"""

from past.builtins import basestring
import logging
import venusian
from .interfaces import AUDITOR

logger = logging.getLogger(__name__)


def includeme(config):
    config.registry[AUDITOR] = Auditor()
    config.add_directive('add_audit_checker', add_audit_checker)
    config.add_request_method(audit, 'audit')


# Same as logging
_levelNames = {
    0: 'NOTSET',
    10: 'DEBUG',
    20: 'INFO',
    30: 'DCC_ACTION',
    40: 'WARNING',
    50: 'NOT_COMPLIANT',
    60: 'ERROR',
    'DEBUG': 10,
    'ERROR': 60,
    'INFO': 20,
    'NOTSET': 0,
    'WARNING': 40,
    'NOT_COMPLIANT': 50,
    'DCC_ACTION': 30,
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
def add_audit_checker(config, checker, item_type, condition=None, frame='embedded'):
    auditor = config.registry[AUDITOR]
    config.action(None, auditor.add_audit_checker,
                  (checker, item_type, condition, frame))


# Declarative configuration
def audit_checker(item_type, condition=None, frame='embedded'):
    """ Register an audit checker
    """

    def decorate(checker):
        def callback(scanner, factory_name, factory):
            scanner.config.add_audit_checker(
                checker, item_type, condition, frame)

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
        types = [context.item_type] + context.base_types
    return auditor.audit(
        request=request, types=types, path=path, root=request.root, context=context,
        registry=request.registry, **kw)
