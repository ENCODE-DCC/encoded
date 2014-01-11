from pyramid.interfaces import PHASE2_CONFIG
from ..contentbase import LOCATION_ROOT
from ..migrator import (
    default_upgrade_finalizer,
    upgrade_step,
)


def includeme(config):
    config.scan()

    def callback():
        """ add_upgrade for all item types
        """
        migrator = config.registry['migrator']
        root = config.registry[LOCATION_ROOT]
        for item_type, collection in root.by_item_type.items():
            version = collection.schema_version
            if version is not None:
                migrator.add_upgrade(item_type, version)

    config.action('add_upgrades', callback, order=PHASE2_CONFIG)



@default_upgrade_finalizer
def finalizer(value, system, version):
    value['schema_version'] = version
