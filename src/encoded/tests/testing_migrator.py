from ..migrator import (
    step_config,
    finalizer_config,
)

def includeme(config):
    config.scan(__name__)
    migrator = config.registry['migrator']
    migrator.add_schema('testing_migrator', '3')


@step_config('testing_migrator', '', '2')
def step1(value, system):
    value['step1'] = True
    return value


@step_config('testing_migrator', '2', '3')
def step2(value, system):
    value['step2'] = True
    return value


@finalizer_config('testing_migrator')
def finalizer(value, system, version):
    value['schema_version'] = version
    return value
