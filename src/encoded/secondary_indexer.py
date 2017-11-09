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
from snovault.elasticsearch.indexer import (
    SEARCH_MAX,
    IndexerState,
    Indexer,
    get_current_xmin,
    all_uuids
)

from .visualization import (
    VISIBLE_DATASET_TYPES_LC,
    object_is_visualizable,
    vis_cache_add
)

log = logging.getLogger(__name__)
SEARCH_MAX = 99999  # OutOfMemoryError if too high


def includeme(config):
    config.add_route('index_secondary', '/index_secondary')
    config.scan(__name__)
    registry = config.registry
    registry['secondary'+INDEXER] = SecondaryIndexer(registry)

class SecondState(IndexerState):
    # Accepts handoff of uuids from primary indexer. Keeps track of uuids and secondary_indexer state by cycle.
    def __init__(self, es, index):
        super(SecondState, self).__init__(es, index, title='secondary')
        self.viscached_set      = self.title + '_viscached'
        self.success_set        = self.viscached_set
        self.cleanup_last_cycle.append(self.viscached_set)  # Clean up at beginning of next cycle
        # DO NOT INHERIT! These keys are for passing on to other indexers
        self.followup_prep_list = None                        # No followup to a following indexer
        self.staged_cycles_list = self.title + '_staged'      # Will take from  primary self.followup_ready_list

    def viscached_uuid(self, uuid):
        self.list_extend(self.viscached_set, [uuid])

    def get_one_cycle(self, xmin, registry):
        uuids = []
        next_xmin = None

        (undone_xmin, uuids, cycle_interrupted) = self.priority_cycle(registry)
        # NOTE: unlike with primary_indexer priority_cycle() can be called after get_initial_state()
        if len(uuids) > 0:
            if not cycle_interrupted:  # AKA reindex signal
                return (-1, next_xmin, uuids)  # -1 ensures using the latest xmin
            if xmin is None or int(xmin) > undone_xmin:
                return (undone_xmin, next_xmin, uuids)

        # To avoid race conditions, move ready_list to end of staged. Then work on staged.
        latest = self.get_list(self.followup_ready_list)
        if latest != []:
            self.delete_objs([self.followup_ready_list])  # TODO: tighten this by adding a locking semaphore
            self.list_extend(self.staged_cycles_list, latest) # Push back for start of next uuid cycle

        staged_list = self.get_list(self.staged_cycles_list)
        if not staged_list or len(staged_list) == 0:
            return (xmin, None, [])
        looking_at = 0
        for val in staged_list:
            looking_at += 1
            if val.startswith("xmin:"):
                if xmin is None:
                    #assert(len(uuids) == 0)  # This is expected but is it assertable?  Shouldn't bet on it
                    xmin = val[5:]
                    continue
                else:
                    next_xmin = val[5:]
                    if next_xmin == xmin:  # shouldn't happen, but just in case
                        next_xmin = None
                        continue
                    looking_at -= 1
                    break   # got all the uuids for the current xmin
            else:
                uuids.append(val)

        if xmin is None:  # could happen if first and only cycle did not start with xmin
            xmin = self.get().get('last_xmin',-1)

        uuid_count = len(uuids)
        if len(uuids) > 0:
            if len(staged_list) == looking_at:
               self.delete_objs([self.staged_cycles_list])
            elif looking_at > 0:
                self.put_list(self.staged_cycles_list,staged_list[looking_at:]) # Push back for start of next uuid cycle

        return (xmin, next_xmin, uuids)



@view_config(route_name='index_secondary', request_method='POST', permission="index")
def index_secondary(request):
    INDEX = request.registry.settings['snovault.elasticsearch.index']
    # Secondary_indexer works off of already indexed elasticsearch objects!
    request.datastore = 'elasticsearch'

    record = request.json.get('record', False)
    dry_run = request.json.get('dry_run', False)
    es = request.registry[ELASTIC_SEARCH]
    indexer = request.registry['secondary'+INDEXER]

    # keeping track of state
    state = SecondState(es, INDEX)

    last_xmin = None
    result = state.get_initial_state()
    last_xmin = result.get('xmin')
    next_xmin = None
    xmin = None  # will be at the beginning of the queue
    result.update(
        last_xmin=last_xmin,
        xmin=xmin
    )

    uuid_count = 0
    indexing_errors = []
    first_txn = datetime.datetime.now(pytz.utc)
    cycles = 0

    (xmin, next_xmin, uuids) = state.get_one_cycle(xmin,request.registry)

    uuid_count = len(uuids)
    if uuid_count > 0 and (xmin is None or int(xmin) <= 0):  # Happens when the a reindex all signal occurs.
        xmin = get_current_xmin(request)

    ### NOTE: These lines may not be appropriate when work other than vis_caching is being done.
    if uuid_count > 500:  # some arbitrary cutoff.
        # There is an efficiency trade off examining many non-visualizable uuids
        # # vs. the cost of eliminating those uuids from the list ahead of time.
        uuids = list(set(all_visualizable_uuids(request.registry)).intersection(uuids))
        uuid_count = len(uuids)
    ### END OF NOTE

    if uuid_count and not dry_run:
        # Starts one cycle of uuids to secondarily index
        result.update(
            last_xmin=last_xmin,
            xmin=xmin,
        )
        result = state.start_cycle(uuids, result)

        # Make no effort to incrementally index... all in
        errors = indexer.update_objects(request, uuids, xmin)     # , snapshot_id)

        indexing_errors.extend(errors)  # ignore errors?
        result['errors'] = indexing_errors

        result = state.finish_cycle(result, indexing_errors)

    if uuid_count == 0:
        result.pop('indexed',None)

    return result


def all_visualizable_uuids(registry):
    return list(all_uuids(registry, types=VISIBLE_DATASET_TYPES_LC))


class SecondaryIndexer(Indexer):
    def __init__(self, registry):
        super(SecondaryIndexer, self).__init__(registry)
        self.state = SecondState(self.es, self.index)  # WARNING, race condition is avoided because there is only one worker

    def get_from_es(request, comp_id):
        '''Returns composite json blob from elastic-search, or None if not found.'''
        return None

    def update_object(self, request, uuid, xmin, restart=False):

        last_exc = None
        # First get the object currently in es
        try:
            result = self.esstorage.get_by_uuid(uuid)  # No reason to restrict by version and that could interfere with reindex all signal.
            #result = self.es.get(index=self.index, id=str(uuid), version=xmin, version_type='external_gte')
            doc = result.source
        except StatementError:
            # Can't reconnect until invalid transaction is rolled back
            raise
        except Exception as e:
            log.error("Error can't find %s in %s", uuid, ELASTIC_SEARCH)
            last_exc = repr(e)

        ### NOTE: if other work is to be done by the secondary indexer, it can be added here.

        if last_exc is None:
            try:
                result = vis_cache_add(request, doc['embedded'])  # result is empty if not visualizable
                if len(result):
                    # Warning: potentiallly slow uuid-level accounting, but single process so no concurency issue
                    self.state.viscached_uuid(uuid)
            except Exception as e:
                log.error('Error indexing %s', uuid, exc_info=True)
                #last_exc = repr(e)
                pass  # It's only a vis_blob.

        if last_exc is not None:
            timestamp = datetime.datetime.now().isoformat()
            return {'error_message': last_exc, 'timestamp': timestamp, 'uuid': str(uuid)}
