"""\
Also run this when the links or keys are changed in the schema.

Example:

    %(prog)s production.ini --app-name app

"""
import itertools
import logging
import transaction
from copy import deepcopy
from snovault import (
    CONNECTION,
    STORAGE,
    UPGRADER,
)
from pyramid.view import view_config
from pyramid.traversal import find_resource
from .schema_utils import validate

EPILOG = __doc__
logger = logging.getLogger(__name__)


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


def update_item(storage, context):
    target_version = context.type_info.schema_version
    current_version = context.properties.get('schema_version', '')
    update = False
    errors = []
    properties = context.properties
    if target_version is None or current_version == target_version:
        unique_keys = context.unique_keys(properties)
        links = context.links(properties)
        keys_add, keys_remove = storage._update_keys(context.model, unique_keys)
        if keys_add or keys_remove:
            update = True
        rels_add, rels_remove = storage._update_rels(context.model, links)
        if rels_add or rels_remove:
            update = True
    else:
        properties = deepcopy(properties)
        upgrader = context.registry[UPGRADER]
        properties = upgrader.upgrade(
            context.type_info.name, properties, current_version, target_version,
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
    storage = request.registry[STORAGE].write
    session = storage.DBSession()
    results = []
    for uuid in batch:
        item_type = None
        update = False
        error = False
        sp = session.begin_nested()
        try:
            item = find_resource(root, uuid)
            item_type = item.type_info.item_type
            update, errors = update_item(storage, item)
        except Exception:
            logger.exception('Error updating: /%s/%s', item_type, uuid)
            sp.rollback()
            error = True
        else:
            if errors:
                errortext = [
                    '%s: %s' % ('/'.join(error.path) or '<root>', error.message)
                    for error in errors]
                logger.error(
                    'Validation failure: /%s/%s\n%s', item_type, uuid, '\n'.join(errortext))
                sp.rollback()
                error = True
            else:
                sp.commit()
        results.append((item_type, uuid, update, error))
    return {'results': results}


def run(config_uri, app_name=None, username=None, types=(), batch_size=500, processes=None):
    # multiprocessing.get_context is Python 3 only.
    from multiprocessing import get_context
    from multiprocessing.pool import Pool

    # Loading app will have configured from config file. Reconfigure here:
    logging.getLogger('snovault').setLevel(logging.DEBUG)

    testapp = internal_app(config_uri, app_name, username)
    connection = testapp.app.registry[CONNECTION]
    uuids = [str(uuid) for uuid in connection.__iter__(*types)]
    transaction.abort()
    logger.info('Total items: %d' % len(uuids))

    pool = Pool(
        processes=processes,
        initializer=initializer,
        initargs=(config_uri, app_name, username),
        context=get_context('forkserver'),
    )

    all_results = []
    try:
        for result in pool.imap_unordered(worker, batched(uuids, batch_size), chunksize=1):
            results = result['results']
            errors = sum(error for item_type, path, update, error in results)
            updated = sum(update for item_type, path, update, error in results)
            logger.info('Batch: Updated %d of %d (errors %d)' %
                        (updated, len(results), errors))
            all_results.extend(results)
    finally:
        pool.terminate()
        pool.join()

    def result_item_type(result):
        # Ensure we always return a string
        return result[0] or ''

    for item_type, results in itertools.groupby(
            sorted(all_results, key=result_item_type), key=result_item_type):
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
    parser.add_argument('--item-type', dest='types', action='append', default=[])
    parser.add_argument('--batch-size', type=int, default=1000)
    parser.add_argument('--processes', type=int)
    parser.add_argument('--username')
    args = parser.parse_args()
    logging.basicConfig()
    run(**vars(args))


if __name__ == '__main__':
    main()
