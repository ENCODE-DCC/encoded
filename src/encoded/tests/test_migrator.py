import pytest

def step1(value, system):
    value['step1'] = True
    return value


def step2(value, system):
    value['step2'] = True
    return value


def finalizer(value, system, version):
    value['schema_version'] = version
    return value


@pytest.fixture
def schema_migrator():
    from ..migrator import SchemaMigrator
    schema_migrator = SchemaMigrator('test', '3')
    schema_migrator.add_upgrade_step(step1, dest='2')
    schema_migrator.add_upgrade_step(step2, source='2', dest='3')
    return schema_migrator


def test_upgrade(schema_migrator):
    value = schema_migrator.upgrade({}, '')
    assert value['step1']
    assert value['step2']


def test_finalizer(schema_migrator):
    schema_migrator.finalizer = finalizer
    value = schema_migrator.upgrade({})
    assert value['schema_version'] == '3'


def test_declarative_config():
    from pyramid.config import Configurator
    config = Configurator()
    config.include('..migrator')
    config.include('.testing_migrator')
    config.commit()

    migrator = config.registry['migrator']
    value = migrator.upgrade('testing_migrator', {}, '')
    assert value['step1']
    assert value['step2']
    assert value['schema_version'] == '3'
