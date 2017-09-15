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
    def __init__(self, es, key):
        super(SecondState, self).__init__(es,key, title='secondary')
        self.viscached_set      = self.title + '_viscached'
        self.success_set        = self.viscached_set
        self.cleanup_last_cycle.append(self.viscached_set)  # Clean up at beginning of next cycle
        ### OPTIONAL: secodary_indexer does audits
        ### self.audited_set        = self.title + '_audited'
        ### self.cleanup_last_cycle = [self.last_set,self.viscached_set,self.audited_set]  # Clean up at beginning of next cycle
        ### OPTIONAL: secodary_indexer does audits
        # DO NOT INHERIT! These keys are for passing on to other indexers
        self.followup_prep_list = None                        # No followup to a following indexer
        self.staged_cycles_list = self.followup_ready_list    # inherited from primary IndexerState

    ### OPTIONAL: secodary_indexer does audits
    ### def audited_all(self, uuids):
    ###    # Avoid individual uuid-level accounting (SLOW) and do this at end of cycle
    ###    self.list_extend(self.audited_set, uuids)
    ### OPTIONAL: secodary_indexer does audits

    def viscached_uuid(self, uuid):
        #self.set_add(self.viscached_set, [uuid])  # Too slow when list is long
        self.list_extend(self.viscached_set, [uuid])

    def get_one_cycle(self, xmin, registry):
        uuids = []
        next_xmin = None

        (undone_xmin, uuids, cycle_interrupted) = self.priority_cycle(registry)
        if len(uuids) > 0:
            if not cycle_interrupted:  # AKA reindex signal
                return (-1, next_xmin, uuids)  # -1 ensures using the latest xmin
            if xmin is None or int(xmin) > undone_xmin:
                return (undone_xmin, next_xmin, uuids)

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
            xmin = self.get(self.state_id).get('last_xmin',-1)

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

    # Do we need worker pool? Only if we do audits

    # keeping track of state
    state = SecondState(es,INDEX)

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
    cycles = 0

    while True:  # Cycles on xmin grouped indexer cycles

        (xmin, next_xmin, uuids) = state.get_one_cycle(xmin,request.registry)

        cycle_uuid_count = len(uuids)
        if cycle_uuid_count > 0 and (xmin is None or int(xmin) <= 0):  # Happens when the a reindex all signal occurs.
            xmin = get_current_xmin(request)

        ### OPTIONAL: secodary_indexer does audits
        #   These lines are not appropriate when audits are involved, unless there is a set of auditable obj types.
        if cycle_uuid_count > 100:  # some arbitrary cutoff.
            uuids = list(set(all_visualizable_uuids(request.registry)).intersection(uuids))
            cycle_uuid_count = len(uuids)
        ### OPTIONAL: secodary_indexer does audits

        if cycle_uuid_count == 0:  # No more uuids in the queue
            break

        cycles += 1

        if not dry_run:
            # Starts one cycle of uuids to secondarily index
            result.update(
                last_xmin=last_xmin,
                xmin=xmin,
            )
            result = state.start_cycle(uuids, result)

            #snapshot_id = None  # Not sure why this will be needed.  The xmin should be all that is needed.

            # Make no effort to incrementally index... all in
            errors = indexer.update_objects(request, uuids, xmin)     # , snapshot_id)

            indexing_errors.extend(errors)  # ignore errors?
            result['errors'] = indexing_errors

            ### OPTIONAL: secodary_indexer does audits
            ### state.audited_all(uuids)
            ### OPTIONAL: secodary_indexer does audits
            result = state.finish_cycle(result,indexing_errors)

            uuid_count += cycle_uuid_count

            ### OPTIONAL: secodary_indexer does audits
            ### # Flush is probably needed for audits.  Is not needed for viscache
            ### es.indices.refresh(index=INDEX)
            ### if flush:
            ###     try:
            ###         es.indices.flush_synced(index=INDEX)  # Faster recovery on ES restart
            ###     except ConflictError:
            ###         pass
            ### OPTIONAL: secodary_indexer does audits

            if next_xmin is not None:
                last_xmin = xmin
                xmin = None  # already pushed next_xmin back onto queue
                next_xmin = None
                result['status'] = 'cycling'
                state.put(result)
            else:
                break

    if uuid_count > 0:
        result['status'] = 'done'
        state.put(result)
        log.warn("Secondary indexer handled %d uuids" % uuid_count)
        if cycles > 1:
            result['lag'] = str(datetime.datetime.now(pytz.utc) - first_txn)
    else:
        result['indexed'] = 0

    return result


def all_visualizable_uuids(registry):
    return list(all_uuids(registry, types=VISIBLE_DATASET_TYPES_LC))


class SecondaryIndexer(Indexer):
    def __init__(self, registry):
        super(SecondaryIndexer, self).__init__(registry)
        self.state = SecondState(self.es,registry.settings['snovault.elasticsearch.index'])  # WARNING, reace condition is avoided because there is only one worker

    def get_from_es(request, comp_id):
        '''Returns composite json blob from elastic-search, or None if not found.'''
        return None

    def update_object(self, request, uuid, xmin, restart=False):

        last_exc = None
        # First get the object currently in es
        try:
            result = self.es.get(index=self.index, id=str(uuid))  # No reason to restrict by version and that would interfere with reindex all signal.
            #result = self.es.get(index=self.index, id=str(uuid), version=xmin, version_type='external_gte')
            doc = result['_source']
        except StatementError:
            # Can't reconnect until invalid transaction is rolled back
            raise
        except Exception as e:
            log.error("Error can't find %s in %s", uuid, ELASTIC_SEARCH)
            last_exc = repr(e)

        ### OPTIONAL: secodary_indexer does audits
        ### # Handle audits:
        ###index_audit = False
        ###if last_exc is None:
        ###    # It might be possible to assert that the audit is either empty or stale
        ###    # TODO assert('audit_stale' is in doc or doc.get('audit') is None)
        ###
        ###    try:
        ###        result = request.embed('/%s/@@index-audits' % uuid, as_user='INDEXER')
        ###        # Should have document with audit only
        ###        assert(result['uuid'] == doc['uuid'])
        ###        if doc.get('audit',{}) != result.get('audit',{}) or doc.get('audit_stale',False):
        ###            doc['audit'] = result['audit']
        ###            doc['audit_stale'] = False
        ###            index_audit = True
        ###    except StatementError:
        ###        # Can't reconnect until invalid transaction is rolled back
        ###        raise
        ###    except Exception as e:
        ###        log.error('Error rendering /%s/@@index-audits', uuid, exc_info=True)
        ###        last_exc = repr(e)
        ###
        ###if index_audit:
        ###    if last_exc is None:
        ###        for backoff in [0, 10, 20, 40, 80]:
        ###            time.sleep(backoff)
        ###            try:
        ###                self.es.index(
        ###                    index=self.index, doc_type=doc['item_type'], body=doc,
        ###                    id=str(uuid), version=xmin, version_type='external_gte',
        ###                    request_timeout=30,
        ###                )
        ###            except StatementError:
        ###                # Can't reconnect until invalid transaction is rolled back
        ###                raise
        ###            except ConflictError:
        ###                #log.warning('Conflict indexing %s at version %d', uuid, xmin)
        ###                # This case occurs when the primary indexer is cycles ahead of the secondary indexer
        ###                # And this uuid will be secondarily indexed again on a second round
        ###                # So no error, pretend it has indexed and move on.
        ###                return  # No use doing any further secondary indexing
        ###            except (ConnectionError, ReadTimeoutError, TransportError) as e:
        ###                log.warning('Retryable error indexing %s: %r', uuid, e)
        ###                last_exc = repr(e)
        ###            except Exception as e:
        ###                log.error('Error indexing %s', uuid, exc_info=True)
        ###                last_exc = repr(e)
        ###                break
        ###            else:
        ###                break
        ### OPTIONAL: secodary_indexer does audits

        ### Now that the audits have been updated to es, the vis_cache can be updated
        if last_exc is None:
            try:
                result = vis_cache_add(request, doc['embedded'])  # result is empty if not visualizable
                if len(result):
                    # Warning: potentiallly slow uuid-level accounting, but single process so no concurency issue
                    self.state.viscached_uuid(uuid)
            except:
                pass  # It's only a vis_blob.

        if last_exc is not None:
            timestamp = datetime.datetime.now().isoformat()
            return {'error_message': last_exc, 'timestamp': timestamp, 'uuid': str(uuid)}

    def shutdown(self):
        pass