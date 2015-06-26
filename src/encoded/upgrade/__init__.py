from pyramid.interfaces import PHASE2_CONFIG
from contentbase import ROOT
from contentbase.upgrader import default_upgrade_finalizer

LATE = 10


def includeme(config):
    config.scan()

    def callback():
        """ add_upgrade for all item types
        """
        migrator = config.registry['migrator']
        root = config.registry[ROOT]
        for item_type, collection in root.by_item_type.items():
            version = collection.type_info.schema_version
            if version is not None:
                migrator.add_upgrade(item_type, version)

    config.action('add_upgrades', callback, order=PHASE2_CONFIG)

    def default_upgrades():
        """ add_upgrade for all item types
        """
        migrator = config.registry['migrator']
        root = config.registry[ROOT]
        for item_type, collection in root.by_item_type.items():
            if item_type not in migrator:
                continue
            if not migrator[item_type].upgrade_steps:
                migrator[item_type].add_upgrade_step(run_finalizer)

    config.action('add_default_upgrades', default_upgrades, order=LATE)


@default_upgrade_finalizer
def finalizer(value, system, version):
    # Update the default properties
    value['schema_version'] = version


def run_finalizer(value, system):
    pass
