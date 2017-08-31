from elasticsearch.exceptions import (
    ConflictError,
    ConnectionError,
    NotFoundError,
    TransportError,
)
from pyramid.view import view_config
from sqlalchemy.exc import StatementError

from urllib3.exceptions import ReadTimeoutError
from snovault.elasticsearch.interfaces import (
    ELASTIC_SEARCH,
    INDEXER,
)
import datetime
import logging
import pytz
import time
import copy
import json
from pkg_resources import resource_filename
from redis import Redis
from snovault.elasticsearch.indexer import (
    IndexerState,
    Indexer
)

from .visualization import object_is_visualizable

log = logging.getLogger(__name__)
SEARCH_MAX = 99999  # OutOfMemoryError if too high


def includeme(config):
    config.add_route('index_secondary', '/index_secondary')
    config.scan(__name__)
    registry = config.registry
    registry['secondary'+INDEXER] = SecondaryIndexer(registry)

class SecondState(IndexerState):
    def __init__(self, redis_client=None,accounting=True):
        super(SecondState, self).__init__(redis_client,accounting)
        self.persistent_key  = 'secondary-state'        # State of the current or last cycle
        self.todo_set        = 'secondary-todo'         # one cycle of uuids, sent to the Secondary Indexer
        self.in_progress_set = 'secondary-in-progress'
        self.failed_set      = 'secondary-failed'
        self.done_set        = 'secondary-done'         # Trying to get all uuids from 'todo' to this set
        self.troubled_set    = 'secondary-troubled'     # uuids that failed to index in any cycle
        self.last_set        = 'secondary-last-cycle'   # uuids in the most recent finished cycle
        self.followup_prep_list = None                  # No followup to secondary indexer
        self.staged_cycles_list = self.followup_ready_list  # inherited from primary IndexerState
        #self.audited_set     = 'secondary-audited'
        self.viscached_set   = 'secondary-viscached'
        # DO NOT INHERIT! All keys that are cleaned up at the start and fully finished end of indexing
        self.cleanup_keys      = [self.todo_set,self.in_progress_set,self.failed_set,self.done_set]
        self.cleanup_last_keys = [self.last_set,self.viscached_set]  # ,self.audited_set] cleaned up only when new indexing occurs

    #def audited_uuid(self, uuid):
    #    self.redis_pipe.sadd(self.audited_set, uuid).execute()

    def viscached_uuid(self, uuid):
        self.redis_pipe.sadd(self.viscached_set, uuid).execute()

    def successes_this_cycle(self):
        # Overwritten: secondary_indexer counts a success as an actual object added to viscache!
        return self.redis_client.scard(self.viscached_set)

    def get_one_cycle(self, xmin):
        uuids = set()
        next_xmin = None
        while True:
            val = self.redis_client.lpop(self.staged_cycles_list)
            if val is None or len(val) == 0:
                break
            if val.startswith("xmin:"):
                if xmin is None:
                    #assert(len(uuids) == 0)  # This is expected but is it assertable?  Shouldn't bet on it
                    xmin = val[5:]
                    #result['xmin'] = xmin
                    #state.set(result)
                    continue
                else:
                    next_xmin = val[5:]
                    if next_xmin == xmin:
                        next_xmin = None
                        continue
                    self.redis_pipe.lpush(self.staged_cycles_list,val).execute()  # Push back for start of next uuid cycle
                    break   # got all the uuids for the current xmin
            else:
                uuids.add(val)
        return (xmin, next_xmin, uuids)



@view_config(route_name='index_secondary', request_method='POST', permission="index")
def index_secondary(request):
    INDEX = request.registry.settings['snovault.elasticsearch.index']
    # Setting request.datastore here only works because routed views are not traversed.
    #request.datastore = 'database'
    # Secondary_indexer works off of already indexed elasticsearch objects!
    request.datastore = 'elasticsearch'

    record = request.json.get('record', False)
    dry_run = request.json.get('dry_run', False)
    recovery = request.json.get('recovery', False)
    es = request.registry[ELASTIC_SEARCH]
    indexer = request.registry['secondary'+INDEXER]
    secondary_accounting = False

    # TODO: Do we need worker pool?  It solves memory overload issues
    # TODO: problem at startup when old list exists but elastcsearch is empty!
    # TODO: figure out if snovault base.ini, development.ini, cloud-config.yml need updating

    # Consider using... (from https://pypi.python.org/pypi/redis find pubsub)
    # p = r.pubsub()
    # p.subscribe('secondary-indexer')
    # In indexer.py r.publish('secondary-indexer', 'wake up!')
    # for message in p.listen():
    #     Now this process doesn't need to be woken by es_index_listener.py

    # Useful redis commands:  https://redis-py.readthedocs.io/en/latest/index.html
    # redis-cli keys '*'
    # redis-cli lrange secondary-waiting 0 -1
    # redis-cli smembers indexed
    # redis-cli del primary-finished
    # redis-cli flushall  # Deletes all keys!!!

    # keep track of state with redis
    state = SecondState(accounting=secondary_accounting)

    last_xmin = None
    result = state.get()
    last_xmin = result.get('xmin')
    next_xmin = None
    xmin = None  # Should be at the beginning of the queue
    result.update(
        last_xmin=last_xmin,
        xmin=xmin
    )

    uuid_count = 0
    indexing_errors = []
    first_txn = datetime.datetime.now(pytz.utc)

    while True:  # Cycles on xmin grouped indexer cycles
        (xmin, next_xmin, uuids) = state.get_one_cycle(xmin)

        if secondary_accounting:
            uuids = state.add_undone_uuids(uuids) # Adds undone from last cycle

        if len(uuids) == 0:  # No more uuids in the queue
            break

        log.info("Secondary indexing begins...")
        uuid_count += len(uuids)

        if xmin is None:  # could happen if first cycle did not start with xmin
            xmin = last_xmin
            last_xmin = 0
            assert(xmin is not None)

        # Starts one cycle of uuids to secondarily index
        result.update(
            last_xmin=last_xmin,
            xmin=xmin,
            batch_size=indexer.batch_size,
        )
        result = state.start_cycle(uuids,result)

        #snapshot_id = None  # Not sure why this will be needed.  The xmin should be all that is needed.

        # Make no effort to incrementally index... all in
        if secondary_accounting:
            errors = indexer.update_in_batches(request, uuids, xmin)  # , snapshot_id)
        else:
            errors = indexer.update_objects(request, uuids, xmin)     # , snapshot_id)

        indexing_errors.extend(errors)  # ignore errors?
        result['errors'] = indexing_errors

        result = state.finish_cycle(result)
        #if record:
        #    result['lag'] = str(datetime.datetime.now(pytz.utc) - first_txn)
        #    try:
        #        es.index(index=INDEX, doc_type='meta', body=result, id='secondary_indexing')
        #    except:
        #        error_messages = copy.deepcopy(result['errors'])
        #        del result['errors']
        #        es.index(index=INDEX, doc_type='meta', body=result, id='secondary_indexing')
        #        for item in error_messages:
        #            if 'error_message' in item:
        #                log.error('Indexing error for {}, error message: {}'.format(item['uuid'], item['error_message']))
        #                item['error_message'] = "Error occured during indexing, check the logs"
        #        result['errors'] = error_messages
        #
        #    if es.indices.get_settings(index=INDEX)[INDEX]['settings']['index'].get('refresh_interval', '') != '1s':
        #        interval_settings = {"index": {"refresh_interval": "1s"}}
        #        es.indices.put_settings(index=INDEX, body=interval_settings)
        #
        #es.indices.refresh(index=INDEX)
        #
        #if flush:
        #    try:
        #        es.indices.flush_synced(index=INDEX)  # Faster recovery on ES restart
        #    except ConflictError:
        #        pass


        if next_xmin is not None:
            last_xmin = xmin
            xmin = None  # already pushed next_xmin back onto queue
            next_xmin = None
            result['status'] = 'cycling'
            state.set(result)
        else:
            break

    if uuid_count > 0:
        result.update(
            status='done',
            lag=str(datetime.datetime.now(pytz.utc) - first_txn)
        )
        state.set(result)
        log.info("Secondary indexer handled %d uuids" % uuid_count)
    else:
        result['indexed'] = 0

    return result


class SecondaryIndexer(Indexer):
    def __init__(self, registry):
        super(SecondaryIndexer, self).__init__(registry)
        self.state = SecondState(self.redis_client)

    def get_from_es(request, comp_id):
        '''Returns composite json blob from elastic-search, or None if not found.'''
        return None

    def update_object(self, request, uuid, xmin):
        #self.state.start_uuid(uuid)

        last_exc = None
        # First get the object currently in es
        try:
            #result = es.get(index=self.index, doc_type=result['item_type'], id=str(uuid))  # FIXME: is doc_type needed?
            doc = request.embed('/%s/@@index-data' % uuid, as_user='INDEXER')
            #result = es.get(index=self.index, id=str(uuid))
            #doc = result['_source']
        except StatementError:
            self.state.failed_uuid(uuid)
            # Can't reconnect until invalid transaction is rolled back
            raise
        except Exception as e:
            log.error("Error can't find %s in %s", uuid, ELASTIC_SEARCH)
            last_exc = repr(e)

        ### # Handle audits:
        ### if last_exc is None:
        ###     # It might be possible to assert that the audit is either empty or stale
        ###     assert(doc['audit_stale'] or doc['audit'] is None)
        ###
        ###     try:
        ###         result = request.embed('/%s/@@index-audits' % uuid, as_user='INDEXER')
        ###         # Should have document with audit only
        ###         assert(result['uuid'] == doc['uuid'])
        ###         doc['audit'] = result['audit']
        ###         doc['audit_stale'] = False
        ###     except StatementError:
        ###         self.state.failed_uuid(uuid)
        ###         # Can't reconnect until invalid transaction is rolled back
        ###         raise
        ###     except Exception as e:
        ###         log.error('Error rendering /%s/@@index-audits', uuid, exc_info=True)
        ###         last_exc = repr(e)
        ###
        ### if last_exc is None:
        ###     for backoff in [0, 10, 20, 40, 80]:
        ###         time.sleep(backoff)
        ###         try:
        ###             self.es.index(
        ###                 index=self.index, doc_type=doc['item_type'], body=doc,
        ###                 id=str(uuid), version=xmin, version_type='external_gte',
        ###                 request_timeout=30,
        ###             )
        ###         except StatementError:
        ###             self.state.failed_uuid(uuid)
        ###             # Can't reconnect until invalid transaction is rolled back
        ###             raise
        ###         except ConflictError:
        ###             #log.warning('Conflict indexing %s at version %d', uuid, xmin)
        ###             # This case occurs when the primary indexer is cycles ahead of the secondary indexer
        ###             # And this uuid will be secondarily indexed again on a second round
        ###             # So no error, pretend it has indexed and move on.
        ###             self.state.indexed_uuid(uuid)
        ###             return  # No use doing any further secondary indexing
        ###         except (ConnectionError, ReadTimeoutError, TransportError) as e:
        ###             log.warning('Retryable error indexing %s: %r', uuid, e)
        ###             last_exc = repr(e)
        ###         except Exception as e:
        ###             log.error('Error indexing %s', uuid, exc_info=True)
        ###             last_exc = repr(e)
        ###             break
        ###         else:
        ###             self.state.audited_uuid(uuid)
        ###             break

        if last_exc is None:
                # Now that the audits have been updated to es, the vis_cache can be updated
            if object_is_visualizable(doc['embedded']):
                try:
                    result = request.embed('/%s/@@index-vis' % uuid, as_user='INDEXER')
                    if len(result):
                        self.state.viscached_uuid(uuid)
                except:
                    pass  # It's only a vis_blob.

        if last_exc is not None:
            self.state.failed_uuid(uuid)
            timestamp = datetime.datetime.now().isoformat()
            return {'error_message': last_exc, 'timestamp': timestamp, 'uuid': str(uuid)}

        #log.info("Secondary indexed %s", uuid)
        #self.state.indexed_uuid(uuid)


    def shutdown(self):
        pass
