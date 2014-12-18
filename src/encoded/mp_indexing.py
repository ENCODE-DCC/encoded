import multiprocessing
from multiprocessing.pool import (
    RUN,
    cpu_count,
    debug,
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
import transaction
import time
import Queue
from contextlib import contextmanager
from .embedding import embed
import logging

log = logging.getLogger(__name__)

ELASTIC_SEARCH = 'encoded:elasticsearch'
INDEXING_POOL = 'encoded:indexing_pool'
INDEX = 'encoded'


current_snapshot_id = None
app = None


def includeme(config):
    config.registry[INDEXING_POOL] = make_pool(config.registry.settings)


def initializer(settings):
    import signal
    signal.signal(signal.SIGINT, signal.SIG_IGN)

    # Close any pre-fork connections
    from .storage import DBSession
    # print 'has session: %s' % DBSession.registry.has()
    DBSession.remove()
    # if 'bind' in DBSession.session_factory.kw:
    #     DBSession.session_factory.kw['bind'].dispose()

    from . import main
    global app
    global snapshot_lock
    atexit.register(clear_snapshot)
    app = main(settings, indexer=False, create_tables=False)
    signal.signal(signal.SIGALRM, clear_snapshot)


def set_snapshot(snapshot_id):
    global current_snapshot_id
    if current_snapshot_id == snapshot_id:
        return
    clear_snapshot()
    current_snapshot_id = snapshot_id
    txn = transaction.begin()
    txn.doom()
    txn.setExtendedInfo('snapshot_id', snapshot_id)
    root = app.root_factory(app)
    registry = app.registry
    request = app.request_factory.blank('/_indexing_pool')
    extensions = app.request_extensions
    if extensions is not None:
        request._set_extensions(extensions)
    request.invoke_subrequest = app.invoke_subrequest
    request.root = root
    request.registry = registry
    request._stats = {}
    manager.push({'request': request, 'registry': registry})


def clear_snapshot(signum=None, frame=None):
    global current_snapshot_id
    if current_snapshot_id is None:
        return
    transaction.abort()
    manager.pop()
    current_snapshot_id = None


@contextmanager
def snapshot(snapshot_id):
    import signal
    signal.alarm(0)
    set_snapshot(snapshot_id)
    yield
    signal.alarm(5)


def es_update_object(args):
    snapshot_id, uuid, xmin = args
    with snapshot(snapshot_id):
        request = get_current_request()
        result = embed(request, '/%s/@@index-data' % uuid, as_user='INDEXER')
        doctype = result['object']['@type'][0]
        es = request.registry[ELASTIC_SEARCH]
        es.index(
            index=INDEX, doc_type=doctype, body=result,
            id=str(uuid), version=xmin, version_type='external',
        )
        return result['object']['@id']


def make_pool(settings):
    return IndexingPool(
        initializer=initializer,
        initargs=(settings, )
    )


def handle_results(request, value_holder):
    es = request.registry[ELASTIC_SEARCH]
    value_holder[0] = i = 0
    while True:
        success, value, orig_args = yield
        snapshot_id, uuid, xmin = orig_args[0]
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
            es.indices.flush(index=INDEX)
        i += 1
        value_holder[0] = i


def pool_update_objects(request, uuids, xmin, snapshot_id, pool):
    tasks = ((snapshot_id, uuid, xmin) for uuid in uuids)
    value_holder = [0]
    result_handler = handle_results(request, value_holder)
    next(result_handler)
    pool.run_tasks(es_update_object, tasks, callback=result_handler.send)
    result_handler.close()
    return value_holder[0]


class IndexingPool(object):
    Process = multiprocessing.Process

    def __init__(self, processes=None, initializer=None, initargs=(),
                 maxtasksperchild=None):
        self._setup_queues()
        self._taskqueue = Queue.Queue()
        self._cache = {}
        self._state = RUN
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
        atexit.register(IndexingPool._terminate_pool, self._inqueue, self._pool)

    def _join_exited_workers(self):
        """Cleanup after any worker processes which have exited due to reaching
        their specified lifetime.  Returns True if any workers were cleaned up.
        """
        cleaned = False
        for i in reversed(range(len(self._pool))):
            worker = self._pool[i]
            if worker.exitcode is not None:
                # worker exited
                debug('cleaning up worker %d' % i)
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
            debug('added worker')

    def _maintain_pool(self):
        """Clean up any exited workers and start replacements for them.
        """
        if self._join_exited_workers():
            self._repopulate_pool()

    def _setup_queues(self):
        from multiprocessing.queues import SimpleQueue
        self._inqueue = SimpleQueue()
        self._outqueue = SimpleQueue()
        self._quick_put = self._inqueue._writer.send
        self._quick_get = self._outqueue._reader.recv

    @staticmethod
    def _help_stuff_finish(inqueue):
        # task_handler may be blocked trying to put items on inqueue
        debug('removing tasks from inqueue until task handler finished')
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
    def _terminate_pool(cls, inqueue, pool):
        # this is guaranteed to only be called once
        debug('finalizing pool')

        debug('helping task handler/workers to finish')
        cls._help_stuff_finish(inqueue)

        # tell workers there is no more work
        debug('task handler sending sentinel to workers')
        for p in pool:
            inqueue._writer.send(None)

        # Terminate workers which haven't already finished.
        if pool and hasattr(pool[0], 'terminate'):
            debug('terminating workers')
            for p in pool:
                if p.exitcode is None:
                    p.terminate()

        if pool and hasattr(pool[0], 'terminate'):
            debug('joining pool workers')
            for p in pool:
                if p.is_alive():
                    # worker has not yet exited
                    debug('cleaning up worker %d' % p.pid)
                    p.join()

    def enqueue_task(self, func, args=(), kw={}):
        job = job_counter.next()
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

        while (cache or iterable) and self._state == RUN:
            while iterable and len(cache) < threshold:
                try:
                    args = next(iterable)
                except StopIteration:
                    iterable = None
                    break
                self.enqueue_task(func, [args])

            self._maintain_pool()
            if not poll(0.1):
                continue
            try:
                task = get()
            except (IOError, EOFError):
                debug('result handler got EOFError/IOError -- exiting')
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
