from pyelasticsearch import ElasticSearch
from pyelasticsearch.exceptions import ElasticHttpNotFoundError
from pyramid.events import (
    BeforeRender,
    subscriber,
)
from pyramid.view import view_config
from uuid import UUID
from .contentbase import (
    AfterModified,
    BeforeModified,
    Created,
    make_subrequest,
)
from .renderers import json_renderer
from .stats import requests_timing_hook
from .storage import (
    DBSession,
    TransactionRecord,
)
import functools
import logging
import transaction

log = logging.getLogger(__name__)
ELASTIC_SEARCH = __name__ + ':elasticsearch'
INDEX = 'encoded'


def includeme(config):
    config.add_route('index', '/index')
    config.scan(__name__)

    if 'elasticsearch.server' in config.registry.settings:
        es = ElasticSearch(config.registry.settings['elasticsearch.server'])
        es._encode_json = json_renderer.dumps
        es.session.hooks['response'].append(requests_timing_hook('es'))
        config.registry[ELASTIC_SEARCH] = es


@view_config(route_name='index', request_method='POST', permission="index")
def index(request):
    record = request.json.get('record', False)
    dry_run = request.json.get('dry_run', False)
    es = request.registry.get(ELASTIC_SEARCH, None)

    session = DBSession()
    connection = session.connection()
    # http://www.postgresql.org/docs/9.3/static/functions-info.html#FUNCTIONS-TXID-SNAPSHOT
    query = connection.execute("""
        SET TRANSACTION ISOLATION LEVEL SERIALIZABLE, READ ONLY, DEFERRABLE;
        SELECT txid_snapshot_xmin(txid_current_snapshot());
    """)
    xmin = query.scalar()  # lowest xid that is still in progress

    last_xmin = None
    if 'last_xmin' in request.json:
        last_xmin = request.json['last_xmin']
    elif es is not None:
        try:
            status = es.get(INDEX, 'meta', 'indexing')
        except ElasticHttpNotFoundError:
            pass
        else:
            last_xmin = status['_source']['xmin']

    result = {
        'xmin': xmin,
        'last_xmin': last_xmin,
    }

    if last_xmin is None:
        result['types'] = types = request.json.get('types', None)
        invalidated = all_uuids(request.root, types)
    else:
        txns = session.query(TransactionRecord).filter(
            TransactionRecord.xid >= last_xmin,
        )

        invalidated = set()
        updated = set()
        max_xid = 0
        txn_count = 0
        for txn in txns.all():
            txn_count += 1
            max_xid = max(max_xid, txn.xid)
            invalidated.update(UUID(uuid) for uuid in txn.data.get('invalidated', ()))
            updated.update(UUID(uuid) for uuid in txn.data.get('updated', ()))

        if txn_count == 0:
            max_xid = None

        new_referencing = set()
        add_dependent_objects(request.root, updated, new_referencing)
        invalidated.update(new_referencing)
        result.update(
            max_xid=max_xid,
            txn_count=txn_count,
            invalidated=[str(uuid) for uuid in invalidated],
        )

    if not dry_run and es is not None:
        result['count'] = count = es_update_object(request, invalidated)
        if count and record:
            es.index(INDEX, 'meta', result, 'indexing')

        es.refresh(INDEX)

    return result


def all_uuids(root, types=None):
    # First index user and access_key so people can log in
    initial = ['user', 'access_key']
    for collection_name in initial:
        collection = root.by_item_type[collection_name]
        if types is not None and collection_name not in types:
            continue
        for count, uuid in enumerate(collection):
            yield uuid
    for collection_name in sorted(root.by_item_type):
        if collection_name in initial:
            continue
        if types is not None and collection_name not in types:
            continue
        collection = root.by_item_type[collection_name]
        for count, uuid in enumerate(collection):
            yield uuid


def add_dependent_objects(root, new, existing):
    # Getting the dependent objects for the indexed object
    objects = new.difference(existing)
    while objects:
        dependents = set()
        for uuid in objects:
            item = root.get_by_uuid(uuid)

            dependents.update({
                model.source_rid for model in item.model.revs
            })
            
            item_rels = item.model.rels
            for rel in item_rels:
                rev_item = root.get_by_uuid(rel.target_rid)
                if (rel.source.item_type, rel.rel) in rev_item.merged_rev.values():
                    dependents.add(rel.target_rid)

        existing.update(objects)
        objects = dependents.difference(existing)


def es_update_object(request, objects):
    es = request.registry[ELASTIC_SEARCH]
    i = -1
    for i, uuid in enumerate(objects):
        subreq = make_subrequest(request, '/%s/@@index-data' % uuid)
        subreq.override_renderer = 'null_renderer'
        subreq.remote_user = 'INDEXER'
        result = request.invoke_subrequest(subreq)
        doctype = result['object']['@type'][0]
        es.index(INDEX, doctype, result, str(uuid))
        if (i + 1) % 50 == 0:
            es.flush(INDEX)
            log.info('Indexing %s %d', result['object']['@id'], i + 1)

    return i + 1



def run_in_doomed_transaction(fn, committed, *args, **kw):
    if not committed:
        return
    txn = transaction.begin()
    txn.doom()  # enables SET TRANSACTION READ ONLY;
    try:
        fn(*args, **kw)
    finally:
        txn.abort()


# After commit hook needs own transaction
es_update_object_in_txn = functools.partial(
    run_in_doomed_transaction, es_update_object,
)


@subscriber(Created)
@subscriber(BeforeModified)
@subscriber(AfterModified)
def record_created(event):
    request = event.request
    # Create property if that doesn't exist
    try:
        referencing = request._encoded_referencing
    except AttributeError:
        referencing = request._encoded_referencing = set()
    try:
        updated = request._encoded_updated
    except AttributeError:
        updated = request._encoded_updated = set()

    uuid = event.object.uuid
    updated.add(uuid)

    # Record dependencies here to catch any to be removed links
    # XXX replace with uuid_closure in elasticsearch document
    add_dependent_objects(request.root, {uuid}, referencing)


@subscriber(BeforeRender)
def es_update_data(event):
    request = event['request']
    updated = getattr(request, '_encoded_updated', None)

    if not updated:
        return

    invalidated = getattr(request, '_encoded_referencing', set())

    txn = transaction.get()
    txn._extension['updated'] = [str(uuid) for uuid in updated]
    txn._extension['invalidated'] = [str(uuid) for uuid in invalidated]

    # XXX How can we ensure consistency here but update written records
    # immediately? The listener might already be indexing on another
    # connection. SERIALIZABLE isolation insufficient because ES writes not
    # serialized. Could either:
    # - Queue up another reindex on the listener
    # - Use conditional puts to ES based on serial before commit.
    # txn = transaction.get()
    # txn.addAfterCommitHook(es_update_object_in_txn, (request, updated))
