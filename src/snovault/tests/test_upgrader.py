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
def schema_upgrader():
    from snovault.upgrader import SchemaUpgrader
    schema_upgrader = SchemaUpgrader('test', '3')
    schema_upgrader.add_upgrade_step(step1, dest='2')
    schema_upgrader.add_upgrade_step(step2, source='2', dest='3')
    return schema_upgrader


def test_upgrade(schema_upgrader):
    value = schema_upgrader.upgrade({}, '')
    assert value['step1']
    assert value['step2']


def test_finalizer(schema_upgrader):
    schema_upgrader.finalizer = finalizer
    value = schema_upgrader.upgrade({})
    assert value['schema_version'] == '3'


def test_declarative_config():
    from pyramid.config import Configurator
    from snovault.interfaces import UPGRADER
    config = Configurator()
    config.include('snovault.config')
    config.include('snovault.upgrader')
    config.include('.testing_upgrader')
    config.commit()

    upgrader = config.registry[UPGRADER]
    value = upgrader.upgrade('testing_upgrader', {}, '')
    assert value['step1']
    assert value['step2']
    assert value['schema_version'] == '3'
