from multiprocessing import (
    cpu_count,
    get_context,
    util,
)
from multiprocessing.pool import (
    RUN,
    TERMINATE,
    job_counter,
    worker,
)
from elasticsearch.exceptions import (
    ConflictError,
)
from pyramid.threadlocal import (
    get_current_request,
    manager,
)
import atexit
import queue
import transaction
import time
from contextlib import contextmanager
import logging

log = logging.getLogger(__name__)

from .indexing import (
    INDEXER,
    Indexer,
)


def includeme(config):
    if config.registry.settings.get('indexer_worker'):
        return
    config.registry[INDEXER] = MPIndexer(config.registry)


# Running in subprocess

current_xmin_snapshot_id = None
app = None


def initializer(settings):
    import signal
    signal.signal(signal.SIGINT, signal.SIG_IGN)

    # There should not be any existing connections.
    from .storage import DBSession
    assert not DBSession.registry.has()
    from . import main
    global app
    atexit.register(clear_snapshot)
    app = main(settings, indexer_worker=True, create_tables=False)
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
    request.datastore = 'database'
    extensions = app.request_extensions
    if extensions is not None:
        request._set_extensions(extensions)
    request.invoke_subrequest = app.invoke_subrequest
    request.registry = registry
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
    def __init__(self, registry):
        self.pool = EventLoopPool(
            initializer=initializer,
            initargs=(registry.settings,),
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


class EventLoopPool(object):
    """ multiprocessing.Pool without the threads.
    """

    def Process(self, *args, **kwds):
        return self._ctx.Process(*args, **kwds)

    def __init__(self, processes=None, initializer=None, initargs=(),
                 maxtasksperchild=None, context=None):
        self._ctx = context or get_context()
        self._setup_queues()
        self._taskqueue = queue.Queue()
        self._cache = {}
        self._state = [RUN]
        self._maxtasksperchild = maxtasksperchild
        self._initializer = initializer
        self._initargs = initargs

        if processes is None:
            try:
                processes = cpu_count()
            except NotImplementedError:
                processes = 1
        if processes < 1:
            raise ValueError("Number of processes must be at least 1")

        if initializer is not None and not hasattr(initializer, '__call__'):
            raise TypeError('initializer must be a callable')

        self._processes = processes
        self._pool = []
        self._repopulate_pool()
        self._terminate = util.Finalize(
            self, self._terminate_pool,
            args=(self._inqueue, self._pool, self._state),
            exitpriority=15,
        )

    def _join_exited_workers(self):
        """Cleanup after any worker processes which have exited due to reaching
        their specified lifetime.  Returns True if any workers were cleaned up.
        """
        cleaned = False
        for i in reversed(range(len(self._pool))):
            worker = self._pool[i]
            if worker.exitcode is not None:
                # worker exited
                util.debug('cleaning up worker %d' % i)
                worker.join()
                cleaned = True
                del self._pool[i]
        return cleaned

    def _repopulate_pool(self):
        """Bring the number of pool processes up to the specified number,
        for use after reaping workers which have exited.
        """
        for i in range(self._processes - len(self._pool)):
            w = self.Process(target=worker,
                             args=(self._inqueue, self._outqueue,
                                   self._initializer,
                                   self._initargs, self._maxtasksperchild)
                             )
            self._pool.append(w)
            w.name = w.name.replace('Process', 'PoolWorker')
            w.daemon = True
            w.start()
            util.debug('added worker')

    def _maintain_pool(self):
        """Clean up any exited workers and start replacements for them.
        """
        if self._join_exited_workers():
            self._repopulate_pool()

    def _setup_queues(self):
        self._inqueue = self._ctx.SimpleQueue()
        self._outqueue = self._ctx.SimpleQueue()
        self._quick_put = self._inqueue._writer.send
        self._quick_get = self._outqueue._reader.recv

    @staticmethod
    def _help_stuff_finish(inqueue):
        # task_handler may be blocked trying to put items on inqueue
        util.debug('removing tasks from inqueue until task handler finished')
        if not inqueue._reader.poll():
            return
        inqueue._rlock.acquire()
        try:
            while inqueue._reader.poll():
                inqueue._reader.recv()
                time.sleep(0)
        finally:
            inqueue._rlock.release()

    @classmethod
    def _terminate_pool(cls, inqueue, pool, _state):
        _state[0] = TERMINATE
        # this is guaranteed to only be called once
        util.debug('finalizing pool')

        util.debug('helping task handler/workers to finish')
        cls._help_stuff_finish(inqueue)

        # tell workers there is no more work
        util.debug('task handler sending sentinel to workers')
        for p in pool:
            inqueue._writer.send(None)

        # Terminate workers which haven't already finished.
        if pool and hasattr(pool[0], 'terminate'):
            util.debug('terminating workers')
            for p in pool:
                if p.exitcode is None:
                    p.terminate()

        if pool and hasattr(pool[0], 'terminate'):
            util.debug('joining pool workers')
            for p in pool:
                if p.is_alive():
                    # worker has not yet exited
                    util.debug('cleaning up worker %d' % p.pid)
                    p.join()

    def enqueue_task(self, func, args=(), kw={}):
        job = next(job_counter)
        self._cache[job] = args
        task = (job, None, func, args, kw)
        self._quick_put(task)
        return job

    def run_tasks(self, func, iterable, callback=None, threshold=None):
        cache = self._cache
        poll = self._outqueue._reader.poll
        get = self._quick_get
        if threshold is None:
            threshold = self._processes * 2

        while (cache or iterable):
            while iterable and len(cache) < threshold and self._state[0] == RUN:
                try:
                    args = next(iterable)
                except StopIteration:
                    iterable = None
                    break
                self.enqueue_task(func, [args])

            if self._state[0] != RUN:
                raise Exception('Shutdown')

            self._maintain_pool()
            if not poll(0.1):
                continue
            try:
                task = get()
            except (IOError, EOFError):
                util.debug('result handler got EOFError/IOError -- exiting')
                return

            job, i, obj = task
            success, value = obj
            try:
                orig_args = cache.pop(job)
            except KeyError:
                pass
            else:
                if callback:
                    callback((success, value, orig_args))
