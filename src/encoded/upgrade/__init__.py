from pyramid.interfaces import PHASE2_CONFIG
from ..contentbase import LOCATION_ROOT
from ..migrator import default_upgrade_finalizer
from ..schema_utils import validate

LATE = 10


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

    def default_upgrades():
        """ add_upgrade for all item types
        """
        migrator = config.registry['migrator']
        root = config.registry[LOCATION_ROOT]
        for item_type, collection in root.by_item_type.items():
            if item_type not in migrator:
                continue
            if not migrator[item_type].upgrade_steps:
                migrator[item_type].add_upgrade_step(run_finalizer)

    config.action('add_default_upgrades', default_upgrades, order=LATE)


@default_upgrade_finalizer
def finalizer(value, system, version):
    # Update the default properties
    context = system.get('context')
    if context is None:
        value['schema_version'] = version
        return

    value['uuid'] = str(context.uuid)
    validated, errors = validate(context.schema, value, value)
    del value['uuid']
    if errors:
        raise Exception(errors)

    validated['schema_version'] = version
    return validated


def run_finalizer(value, system):
    pass
