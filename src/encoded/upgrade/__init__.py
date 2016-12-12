from pyramid.interfaces import PHASE2_CONFIG
from snovault import (
    TYPES,
    UPGRADER,
)
from snovault.upgrader import default_upgrade_finalizer

LATE = 10


def includeme(config):
    config.scan()

    def callback():
        """ add_upgrade for all item types
        """
        upgrader = config.registry[UPGRADER]
        types = config.registry[TYPES]
        for type_info in types.by_item_type.values():
            version = type_info.schema_version
            if version is not None:
                upgrader.add_upgrade(type_info.name, version)

    config.action('add_upgrades', callback, order=PHASE2_CONFIG)

    def default_upgrades():
        """ add_upgrade for all item types
        """
        upgrader = config.registry[UPGRADER]
        types = config.registry[TYPES]
        for type_info in types.by_item_type.values():
            if type_info.name not in upgrader:
                continue
            if not upgrader[type_info.name].upgrade_steps:
                upgrader[type_info.name].add_upgrade_step(run_finalizer)

    config.action('add_default_upgrades', default_upgrades, order=LATE)


@default_upgrade_finalizer
def finalizer(value, system, version):
    # Update the default properties
    value['schema_version'] = version


def run_finalizer(value, system):
    pass
