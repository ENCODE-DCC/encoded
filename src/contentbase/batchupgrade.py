"""\
Also run this when the links or keys are changed in the schema.

Example:

    %(prog)s production.ini --app-name app

"""
import logging
import transaction
from copy import deepcopy
from contentbase.storage import (
    DBSession,
    update_keys,
    update_rels,
)
from pyramid.traversal import resource_path
from pyramid.view import view_config
from pprint import pformat

EPILOG = __doc__
logger = logging.getLogger(__name__)

from .schema_utils import validate
import itertools


def includeme(config):
    config.add_route('batch_upgrade', '/batch_upgrade')
    config.scan(__name__)


def batched(iterable, n=1):
    l = len(iterable)
    for ndx in range(0, l, n):
        yield iterable[ndx:min(ndx+n, l)]


def internal_app(configfile, app_name=None, username=None):
    from webtest import TestApp
    from pyramid import paster
    app = paster.get_app(configfile, app_name)
    if not username:
        username = 'UPGRADE'
    environ = {
        'HTTP_ACCEPT': 'application/json',
        'REMOTE_USER': username,
    }
    return TestApp(app, environ)


# Running in subprocess
testapp = None


def initializer(*args, **kw):
    global testapp
    testapp = internal_app(*args, **kw)


def worker(batch):
    res = testapp.post_json('/batch_upgrade', {'batch': batch})
    return res.json


def update_item(context):
    target_version = context.type_info.schema_version
    current_version = context.properties.get('schema_version', '')
    update = False
    errors = []
    properties = context.properties
    if target_version is None or current_version == target_version:
        unique_keys = context.unique_keys(properties)
        links = context.links(properties)
        keys_add, keys_remove = update_keys(context.model, unique_keys)
        if keys_add or keys_remove:
            update = True
        rels_add, rels_remove = update_rels(context.model, links)
        if rels_add or rels_remove:
            update = True
    else:
        properties = deepcopy(properties)
        migrator = context.registry['migrator']
        properties = migrator.upgrade(
            context.item_type, properties, current_version, target_version,
            context=context, registry=context.registry)
        if 'schema_version' in properties:
            del properties['schema_version']
        schema = context.type_info.schema
        properties['uuid'] = str(context.uuid)
        validated, errors = validate(schema, properties, properties)
        # Do not send modification events to skip indexing
        context.update(validated)
        update = True
    return update, errors


@view_config(route_name='batch_upgrade', request_method='POST', permission='import_items')
def batch_upgrade(request):
    request.datastore = 'database'
    transaction.get().setExtendedInfo('upgrade', True)
    batch = request.json['batch']
    root = request.root
    session = DBSession()
    results = {}
    for uuid in batch:
        item = root[uuid]
        path = resource_path(item)
        item_type = item.item_type
        update = False
        error = False
        sp = session.begin_nested()
        try:
            update, errors = update_item(item)
        except Exception:
            logger.exception('Error updating: %s', path)
            sp.rollback()
            error = True
        else:
            if errors:
                logger.error('Validation failure: %s\n%s', path, pformat(errors))
                sp.rollback()
                error = True
            else:
                sp.commit()
        results[uuid] = (item_type, path, update, error)
    return results


def run(config_uri, app_name=None, username=None, types=None, batch_size=1000, processes=None):
    # Loading app will have configured from config file. Reconfigure here:
    logging.getLogger('contentbase').setLevel(logging.DEBUG)

    testapp = internal_app(config_uri, app_name, username)
    connection = testapp.app.registry['connection']
    uuids = [str(uuid) for uuid in connection]
    transaction.abort()
    logger.info('Total items: %d' % len(uuids))

    from multiprocessing import get_context
    from .eventpool import EventPool
    pool = EventPool(
        processes=processes,
        initializer=initializer,
        initargs=(config_uri, app_name, username),
        context=get_context('forkserver'),
    )

    all_results = []

    def callback(args):
        success, result, orig_args = args
        if success:
            results = list(result.values())
            errors = sum(error for item_type, path, update, error in results)
            updated = sum(update for item_type, path, update, error in results)
            logger.info('Batch: Updated %d of %d (errors %d)' %
                        (updated, len(results), errors))
            all_results.extend(results)
        else:
            logger.error(result)

    tasks = batched(uuids, batch_size)
    pool.run_tasks(worker, tasks, callback=callback)

    for item_type, results in itertools.groupby(sorted(all_results), lambda x: x[0]):
        results = list(results)
        errors = sum(error for item_type, path, update, error in results)
        updated = sum(update for item_type, path, update, error in results)
        logger.info('Collection %s: Updated %d of %d (errors %d)' %
                    (item_type, updated, len(results), errors))


def main():
    import argparse
    parser = argparse.ArgumentParser(
        description="Batch upgrade content items.", epilog=EPILOG,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument('config_uri', help="path to configfile")
    parser.add_argument('--app-name', help="Pyramid app name in configfile")
    parser.add_argument('--item-type', dest='types', action='append')
    parser.add_argument('--batch-size', type=int, default=1000)
    parser.add_argument('--processes', type=int)
    parser.add_argument('--username')
    args = parser.parse_args()
    logging.basicConfig()
    run(**vars(args))


if __name__ == '__main__':
    main()
