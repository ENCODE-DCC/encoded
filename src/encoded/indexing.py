from collections import defaultdict
from elasticsearch import Elasticsearch
from elasticsearch.exceptions import (
    ConflictError,
    NotFoundError,
)
from pyramid.events import (
    BeforeRender,
    subscriber,
)
from pyramid.traversal import resource_path
from elasticsearch.connection import Urllib3HttpConnection
from elasticsearch.serializer import SerializationError
from pyramid.view import view_config
from uuid import UUID
from .contentbase import (
    AfterModified,
    BeforeModified,
    Created,
)
from .embedding import embed
from .renderers import json_renderer
from .stats import ElasticsearchConnectionMixin
from .storage import (
    DBSession,
    TransactionRecord,
)
import functools
import json
import logging
import transaction

log = logging.getLogger(__name__)
ELASTIC_SEARCH = __name__ + ':elasticsearch'
INDEX = 'encoded'


def includeme(config):
    config.add_route('index', '/index')
    config.scan(__name__)

    if 'elasticsearch.server' in config.registry.settings:
        es = Elasticsearch(
            [config.registry.settings['elasticsearch.server']],
            serializer=PyramidJSONSerializer(json_renderer),
            connection_class=TimedUrllib3HttpConnection,
        )
        #es.session.hooks['response'].append(requests_timing_hook('es'))
        config.registry[ELASTIC_SEARCH] = es



class PyramidJSONSerializer(object):
    mimetype = 'application/json'

    def __init__(self, renderer):
        self.renderer = renderer

    def loads(self, s):
        try:
            return json.loads(s)
        except (ValueError, TypeError) as e:
            raise SerializationError(s, e)

    def dumps(self, data):
        # don't serialize strings
        if isinstance(data, (type(''), type(u''))):
            return data

        try:
            return self.renderer.dumps(data)
        except (ValueError, TypeError) as e:
            raise SerializationError(data, e)


class TimedUrllib3HttpConnection(ElasticsearchConnectionMixin, Urllib3HttpConnection):
    pass


@view_config(route_name='index', request_method='POST', permission="index")
def index(request):
    record = request.json.get('record', False)
    dry_run = request.json.get('dry_run', False)
    es = request.registry[ELASTIC_SEARCH]

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
    else:
        try:
            status = es.get(index=INDEX, doc_type='meta', id='indexing')
        except NotFoundError:
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
        renamed = set()
        max_xid = 0
        txn_count = 0
        for txn in txns.all():
            txn_count += 1
            max_xid = max(max_xid, txn.xid)
            renamed.update(txn.data.get('renamed', ()))
            updated.update(txn.data.get('updated', ()))

        result['txn_count'] = txn_count
        if txn_count == 0:
            return result

        es.indices.refresh(index=INDEX)
        res = es.search(index=INDEX, body={
            'filter': {
                'terms': {
                    'embedded_uuids': updated,
                    'linked_uuids': renamed,
                    '_cache': False,
                },
            },
            '_source': False,
        })
        referencing = {hit['_id'] for hit in res['hits']['hits']}
        now_referencing = set()
        add_dependent_objects(request.root, updated, now_referencing)
        invalidated = referencing | now_referencing
        result.update(
            max_xid=max_xid,
            renamed=renamed,
            updated=updated,
            referencing=len(referencing),
            now_referencing=len(now_referencing),
            invalidated=len(invalidated),
        )


    if not dry_run:
        result['indexed'] = es_update_object(request, invalidated, xmin)
        if record:
            es.index(index=INDEX, doc_type='meta', body=result, id='indexing')

        es.indices.refresh(index=INDEX)

    return result


def all_uuids(root, types=None):
    # First index user and access_key so people can log in
    initial = ['user', 'access_key']
    for collection_name in initial:
        collection = root.by_item_type[collection_name]
        if types is not None and collection_name not in types:
            continue
        for uuid in collection:
            yield str(uuid)
    for collection_name in sorted(root.by_item_type):
        if collection_name in initial:
            continue
        if types is not None and collection_name not in types:
            continue
        collection = root.by_item_type[collection_name]
        for uuid in collection:
            yield str(uuid)


def add_dependent_objects(root, new, existing):
    # Getting the dependent objects for the indexed object
    objects = new.difference(existing)
    while objects:
        dependents = set()
        for uuid in objects:
            item = root.get_by_uuid(uuid)

            dependents.update(
                str(model.source_rid) for model in item.model.revs
            )
            
            item_type = item.item_type
            item_rels = item.model.rels
            for rel in item_rels:
                key = (item_type, rel.rel)
                if key not in root.all_merged_rev:
                    continue
                rev_item = root.get_by_uuid(rel.target_rid)
                if key in rev_item.merged_rev.values():
                    dependents.add(str(rel.target_rid))

        existing.update(objects)
        objects = dependents.difference(existing)


def es_update_object(request, objects, xmin):
    es = request.registry[ELASTIC_SEARCH]
    i = -1
    for i, uuid in enumerate(objects):
        try:
            result = embed(request, '/%s/@@index-data' % uuid, as_user='INDEXER')
        except Exception as e:
            log.warning('Error indexing %s', uuid, exc_info=True)
        else:
            doctype = result['object']['@type'][0]
            try:
                es.index(index=INDEX, doc_type=doctype, body=result, id=str(uuid), version=xmin, version_type='external')
            except ConflictError:
                log.warning('Conflict indexing %s at version %d', uuid, xmin, exc_info=True)
            except Exception as e:
                log.warning('Error indexing %s', uuid, exc_info=True)
            else:
                if (i + 1) % 50 == 0:
                    log.info('Indexing %s %d', result['object']['@id'], i + 1)

        if (i + 1) % 50 == 0:
            es.indices.flush(index=INDEX)

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
    context = event.object
    # Create property if that doesn't exist
    try:
        updated = request._encoded_updated
    except AttributeError:
        updated = request._encoded_updated = defaultdict(set)

    uuid = str(context.uuid)
    name = resource_path(context)
    updated[uuid].add(name)


@subscriber(BeforeRender)
def es_update_data(event):
    request = event['request']
    updated = getattr(request, '_encoded_updated', None)

    if not updated:
        return

    txn = transaction.get()
    txn._extension['updated'] = updated.keys()
    txn._extension['renamed'] = [uuid for uuid, names in updated.items() if len(names) > 1]

    # XXX How can we ensure consistency here but update written records
    # immediately? The listener might already be indexing on another
    # connection. SERIALIZABLE isolation insufficient because ES writes not
    # serialized. Could either:
    # - Queue up another reindex on the listener
    # - Use conditional puts to ES based on serial before commit.
    # txn = transaction.get()
    # txn.addAfterCommitHook(es_update_object_in_txn, (request, updated))
