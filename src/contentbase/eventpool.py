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
import queue
import time


class EventPool(object):
    """ multiprocessing.Pool without the threads for easier reasoning.
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
