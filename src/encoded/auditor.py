""" Cross-object data auditing

Schema validation allows for checking values within a single object.
We also need to perform higher order checking between linked objects.
"""

import logging
import venusian

logger = logging.getLogger(__name__)


def includeme(config):
    config.registry['auditor'] = Auditor()
    config.add_directive('add_audit_checker', add_audit_checker)
    config.add_request_method(audit, 'audit')


# Same as logging
_levelNames = {
    0: 'NOTSET',
    10: 'DEBUG',
    20: 'INFO',
    30: 'DCC_ACTION',
    40: 'WARNING',
    50: 'STANDARDS_FAILURE',
    60: 'ERROR',
    'DEBUG': 10,
    'ERROR': 60,
    'INFO': 20,
    'NOTSET': 0,
    'WARNING': 40,
    'STANDARDS_FAILURE': 50,
    'DCC_ACTION': 30,
}


class AuditFailure(Exception):
    def __init__(self, category, detail=None, level=0):
        super(AuditFailure, self)
        self.category = category
        self.detail = detail
        if not isinstance(level, int):
            level = _levelNames[level]
        self.level = level

    def __json__(self, request=None):
        return {
            'category': self.category,
            'detail': self.detail,
            'level': self.level,
            'level_name': _levelNames[self.level],
        }


class Auditor(object):
    """ Data audit manager
    """
    _order = 0

    def __init__(self):
        self.type_checkers = {}

    def add_audit_checker(self, checker, item_type, condition=None):
        checkers = self.type_checkers.setdefault(item_type, [])
        self._order += 1  # consistent execution ordering
        checkers.append((self._order, checker, condition))

    def audit(self, value, item_type, path=None, **kw):
        if isinstance(item_type, basestring):
            item_type = [item_type]
        checkers = set()
        checkers.update(*(self.type_checkers.get(name, ()) for name in item_type))
        errors = []
        system = {}
        system.update(kw)
        for order, checker, condition in sorted(checkers):
            if condition is not None:
                try:
                    if not condition(value, system):
                        continue
                except Exception as e:
                    detail = '%s: %r' % (checker.__name__, e)
                    errors.append(AuditFailure('audit condition error', detail, 'ERROR'))
                    logger.warning('audit condition error auditing %s', path, exc_info=True)
                    continue
            try:
                try:
                    result = checker(value, system)
                except AuditFailure as e:
                    errors.append(e)
                    continue
                if result is None:
                    continue
                if isinstance(result, AuditFailure):
                    result = [result]
                for item in result:
                    if isinstance(item, AuditFailure):
                        errors.append(item)
                        continue
                    raise ValueError(item)
            except Exception as e:
                detail = '%s: %r' % (checker.__name__, e)
                errors.append(AuditFailure('audit script error', detail, 'ERROR'))
                logger.warning('audit script error auditing %s', path, exc_info=True)
                continue
        return errors


# Imperative configuration
def add_audit_checker(config, checker, item_type, condition=None):
    auditor = config.registry['auditor']
    config.action(None, auditor.add_audit_checker,
                  (checker, item_type, condition))


# Declarative configuration
def audit_checker(item_type, condition=None):
    """ Register an audit checker
    """

    def decorate(checker):
        def callback(scanner, factory_name, factory):
            scanner.config.add_audit_checker(
                checker, item_type, condition)

        venusian.attach(checker, callback, category='auditor')
        return checker

    return decorate


def audit(request, value, item_type, path=None, context=None, **kw):
    auditor = request.registry['auditor']
    if path is None:
        path = request.path
    if context is None:
        context = request.context
    return auditor.audit(
        value, item_type, path=path, root=request.root, context=context,
        registry=request.registry, **kw)
