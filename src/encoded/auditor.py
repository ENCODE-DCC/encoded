""" Cross-object data auditing

Schema validation allows for checking values within a single object.
We also need to perform higher order checking between linked objects.
"""

import venusian


def includeme(config):
    config.registry['auditor'] = Auditor()
    config.add_directive('add_audit_checker', add_audit_checker)
    config.add_request_method(audit, 'audit')


# Same as logging
_levelNames = {
    0: 'NOTSET',
    10: 'DEBUG',
    20: 'INFO',
    30: 'WARNING',
    40: 'ERROR',
    50: 'CRITICAL',
    'CRITICAL': 50,
    'DEBUG': 10,
    'ERROR': 40,
    'INFO': 20,
    'NOTSET': 0,
    'WARN': 30,
    'WARNING': 30,
}


class Failure(Exception):
    def __init__(self, category, detail=None, level=0):
        super(Failure, self)
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

    def add_audit_checker(self, checker, item_type, category=None, detail=None, level=0):
        if category is None:
            category = 'check'
        if detail is None:
            detail = ''
        if not isinstance(level, int):
            level = _levelNames[level]
        checkers = self.type_checkers.setdefault(item_type, [])
        self._order += 1  # consistent execution ordering
        checkers.append((self._order, checker, category, detail, level))

    def audit(self, value, item_type, **kw):
        if isinstance(item_type, basestring):
            item_type = [item_type]
        checkers = set()
        checkers.update(*(self.type_checkers.get(name, ()) for name in item_type))
        errors = []
        system = {}
        system.update(kw)
        for order, checker, category, detail, level in sorted(checkers):
            try:
                result = checker(value, system)
            except Failure as e:
                errors.append(e)
                continue
            if not result:
                continue
            if isinstance(result, basestring):
                detail = result
            errors.append(Failure(category, detail, level))
        return errors


# Imperative configuration
def add_audit_checker(config, checker, item_type, category=None, detail=None, level=0):
    auditor = config.registry['auditor']
    config.action(None, auditor.add_audit_checker,
        (checker, item_type, category, detail, level))


# Declarative configuration
def audit_checker(item_type, category=None, detail=None, level=0):
    """ Register an audit checker
    """

    def decorate(checker):
        def callback(scanner, factory_name, factory):
            scanner.config.add_audit_checker(
                checker, item_type, category, detail, level)

        venusian.attach(checker, callback, category='auditor')
        return checker

    return decorate


def audit(request, value, item_type, **kw):
    auditor = request.registry['auditor']
    return auditor.audit(value, item_type, root=request.root, **kw)
