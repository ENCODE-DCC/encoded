from snovault import (
    Item,
    collection,
)
from snovault.upgrader import (
    upgrade_step,
    upgrade_finalizer,
)


def includeme(config):
    config.scan(__name__)
    config.add_upgrade('testing_upgrader', '3')


@collection('testing-upgrader')
class TestingUpgrader(Item):
    item_type = 'testing_upgrader'


@upgrade_step('testing_upgrader', '', '2')
def step1(value, system):
    value['step1'] = True
    return value


@upgrade_step('testing_upgrader', '2', '3')
def step2(value, system):
    value['step2'] = True
    return value


@upgrade_finalizer('testing_upgrader')
def finalizer(value, system, version):
    value['schema_version'] = version
    return value
