from ..migrator import (
    upgrade_step,
    upgrade_finalizer,
)

def includeme(config):
    config.scan(__name__)
    config.add_upgrade('testing_migrator', '3')


@upgrade_step('testing_migrator', '', '2')
def step1(value, system):
    value['step1'] = True
    return value


@upgrade_step('testing_migrator', '2', '3')
def step2(value, system):
    value['step2'] = True
    return value


@upgrade_finalizer('testing_migrator')
def finalizer(value, system, version):
    value['schema_version'] = version
    return value
