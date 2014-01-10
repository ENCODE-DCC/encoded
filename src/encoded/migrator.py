from pkg_resources import parse_version
from pyramid.interfaces import PHASE1_CONFIG
import venusian


def includeme(config):
    config.registry['migrator'] = Migrator(config)


class ConfigurationError(Exception):
    pass


class UpgradeError(Exception):
    pass


class NoUpgradePath(UpgradeError):
    def __str__(self):
        return "%r from %r to %r (at %r)" % self.args


class VersionTooHigh(UpgradeError):
    pass


class Migrator(dict):
    """ Migration manager
    """
    def __init__(self, config):
        # Pyramid config used for the phased configuration
        self.config = config

    def add_schema(self, schema_name, version='', finalizer=None):
        if finalizer is not None:
            self.set_finalizer(schema_name, finalizer)

        def callback():
            self[schema_name] = SchemaMigrator(schema_name, version)

        self.config.action(
            ('migrator:add_schema', schema_name),
            callback, order=PHASE1_CONFIG)

    def add_step(self, schema_name, step, source='', dest=''):

        def callback():
            self[schema_name].add_step(step, source, dest)

        self.config.action(
            ('migrator:add_step', schema_name, parse_version(source)),
            callback)

    def set_finalizer(self, schema_name, finalizer):

        def callback():
            self[schema_name].finalizer = finalizer

        self.config.action(
            ('migrator:set_finalizer', schema_name),
            callback)

    def upgrade(self, schema_name, value, current_version='', target_version=None):
        return self[schema_name].upgrade(value, current_version, target_version)

    def __repr__(self):
        return object.__repr__(self)


class SchemaMigrator(object):
    """ Manages upgrade steps
    """
    def __init__(self, name, version='', finalizer=None):
        self.__name__ = name
        self.version = version
        self.upgrade_steps = {}
        self.finalizer = finalizer

    def add_step(self, step, source='', dest=''):
        if parse_version(dest) <= parse_version(source):
            raise ValueError("dest is less than source", dest, source)
        if parse_version(source) in self.upgrade_steps:
            raise ConfigurationError('duplicate step for source', source)
        self.upgrade_steps[parse_version(source)] = UpgradeStep(step, source, dest)

    def upgrade(self, value, current_version='', target_version=None):
        if target_version is None:
            target_version = self.version

        if parse_version(current_version) > parse_version(target_version):
            raise VersionTooHigh(self.__name__, current_version, target_version)

        # If no entry exists for the current_version, fallback to ''
        version = current_version
        if parse_version(version) not in self.upgrade_steps:
            version = ''

        # Try to find a path from current to target versions
        steps = []
        while parse_version(version) < parse_version(target_version):
            try:
                step = self.upgrade_steps[parse_version(version)]
            except KeyError:
                break
            steps.append(step)
            version = step.dest

        if version != target_version:
            raise NoUpgradePath(self.__name__, current_version, target_version, version)

        system = {}

        for step in steps:
            value = step(value, system)

        if self.finalizer is not None:
            value = self.finalizer(value, system, version)

        return value


class UpgradeStep(object):
    def __init__(self, step, source, dest):
        self.step = step
        self.source = source
        self.dest = dest

    def __call__(self, value, system):
        return self.step(value, system)


def step_config(schema_name, source='', dest=''):
    """ Register an upgrade step
    """

    def decorate(step):
        def callback(scanner, factory_name, factory):
            migrator = scanner.config.registry['migrator']
            migrator.add_step(schema_name, step, source, dest)

        venusian.attach(step, callback, category='migrator')
        return step

    return decorate


def finalizer_config(schema_name):
    """ Register a finalizer
    """

    def decorate(finalizer):
        def callback(scanner, factory_name, factory):
            migrator = scanner.config.registry['migrator']
            migrator.set_finalizer(schema_name, finalizer)

        venusian.attach(finalizer, callback, category='migrator')
        return finalizer

    return decorate
