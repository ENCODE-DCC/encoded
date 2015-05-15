from contextlib import contextmanager
from elasticsearch.exceptions import (
    ConflictError,
)
from multiprocessing import get_context
from pyramid.request import apply_request_extensions
from pyramid.threadlocal import (
    get_current_request,
    manager,
)
import atexit
import logging
import time
import transaction
from .eventpool import EventPool
from .indexing import (
    INDEXER,
    Indexer,
)

log = logging.getLogger(__name__)


def includeme(config):
    if config.registry.settings.get('indexer_worker'):
        return
    processes = config.registry.settings.get('indexer.processes')
    if processes is not None:
        processes = int(processes)
    config.registry[INDEXER] = MPIndexer(config.registry, processes=processes)


# Running in subprocess

current_xmin_snapshot_id = None
app = None


def initializer(app_factory, settings):
    import signal
    signal.signal(signal.SIGINT, signal.SIG_IGN)

    # There should not be any existing connections.
    from .storage import DBSession
    assert not DBSession.registry.has()
    global app
    atexit.register(clear_snapshot)
    app = app_factory(settings, indexer_worker=True, create_tables=False)
    signal.signal(signal.SIGALRM, clear_snapshot)


def set_snapshot(xmin, snapshot_id):
    from .storage import DBSession
    global current_xmin_snapshot_id
    if current_xmin_snapshot_id == (xmin, snapshot_id):
        return
    clear_snapshot()
    current_xmin_snapshot_id = (xmin, snapshot_id)

    while True:
        txn = transaction.begin()
        txn.doom()
        if snapshot_id is not None:
            txn.setExtendedInfo('snapshot_id', snapshot_id)
        session = DBSession()
        connection = session.connection()
        db_xmin = connection.execute(
            "SELECT txid_snapshot_xmin(txid_current_snapshot());").scalar()
        if db_xmin >= xmin:
            break
        transaction.abort()
        log.info('Waiting for xmin %r to reach %r', db_xmin, xmin)
        time.sleep(0.1)

    registry = app.registry
    request = app.request_factory.blank('/_indexing_pool')
    request.registry = registry
    request.datastore = 'database'
    apply_request_extensions(request)
    request.invoke_subrequest = app.invoke_subrequest
    request.root = app.root_factory(request)
    request._stats = {}
    manager.push({'request': request, 'registry': registry})


def clear_snapshot(signum=None, frame=None):
    global current_xmin_snapshot_id
    if current_xmin_snapshot_id is None:
        return
    transaction.abort()
    manager.pop()
    current_xmin_snapshot_id = None


@contextmanager
def snapshot(xmin, snapshot_id):
    import signal
    signal.alarm(0)
    set_snapshot(xmin, snapshot_id)
    yield
    signal.alarm(5)


def update_object_in_snapshot(args):
    uuid, xmin, snapshot_id = args
    with snapshot(xmin, snapshot_id):
        request = get_current_request()
        indexer = request.registry[INDEXER]
        return indexer.update_object(request, uuid, xmin)


# Running in main process

def handle_results(request, value_holder):
    value_holder[0] = i = 0
    while True:
        success, value, orig_args = yield
        uuid, xmin, snapshot_id = orig_args[0]
        if success:
            path = value
        else:
            path = uuid
            if isinstance(value, ConflictError):
                log.warning('Conflict indexing %s at version %d: %r', uuid, xmin, value)
            else:
                log.warning('Error indexing %s: %r', uuid, value)
        if (i + 1) % 50 == 0:
            log.info('Indexing %s %d', path, i + 1)
        i += 1
        value_holder[0] = i


class MPIndexer(Indexer):
    def __init__(self, registry, processes=None):
        self.pool = EventPool(
            processes=processes,
            initializer=initializer,
            initargs=(registry['app_factory'], registry.settings,),
            context=get_context('forkserver'),
        )
        super(MPIndexer, self).__init__(registry)

    def update_objects(self, request, uuids, xmin, snapshot_id):
        tasks = ((uuid, xmin, snapshot_id) for uuid in uuids)
        value_holder = [0]
        result_handler = handle_results(request, value_holder)
        next(result_handler)
        self.pool.run_tasks(update_object_in_snapshot, tasks, callback=result_handler.send)
        result_handler.close()
        return value_holder[0]

    def shutdown(self):
        self.pool._terminate()
