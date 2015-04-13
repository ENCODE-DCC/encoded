from collections import defaultdict
from .embedding import embed
from elasticsearch import Elasticsearch, helpers
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
from .contentbase import (
    AfterModified,
    BeforeModified,
    Created,
    simple_path_ids,
)
from sqlalchemy.exc import StatementError
from .renderers import json_renderer
from .stats import ElasticsearchConnectionMixin
from .storage import (
    DBSession,
    TransactionRecord,
)
import datetime
import json
import logging
import pytz
import transaction
import urllib3
import gzip
import io
import pandas as pd
import numpy as np
from urllib.parse import (
    urlencode,
)


log = logging.getLogger(__name__)
ELASTIC_SEARCH = 'elasticsearch'
INDEX = 'encoded'
INDEXER = 'indexer'
SEARCH_MAX = 99999  # OutOfMemoryError if too high


def includeme(config):
    config.add_route('index', '/index')
    config.add_route('file_index', '/file_index')
    config.scan(__name__)
    config.add_request_method(lambda request: defaultdict(set), '_updated_uuid_paths', reify=True)
    config.add_request_method(lambda request: {}, '_initial_back_rev_links', reify=True)
    registry = config.registry

    if 'elasticsearch.server' in registry.settings:
        es = Elasticsearch(
            [registry.settings['elasticsearch.server']],
            serializer=PyramidJSONSerializer(json_renderer),
            connection_class=TimedUrllib3HttpConnection,
            timeout=30,
        )
        registry[ELASTIC_SEARCH] = es
        registry[INDEXER] = Indexer(registry)


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
    # Setting request.datastore here only works because routed views are not traversed.
    request.datastore = 'database'
    record = request.json.get('record', False)
    dry_run = request.json.get('dry_run', False)
    recovery = request.json.get('recovery', False)
    es = request.registry[ELASTIC_SEARCH]
    indexer = request.registry[INDEXER]

    session = DBSession()
    connection = session.connection()
    # http://www.postgresql.org/docs/9.3/static/functions-info.html#FUNCTIONS-TXID-SNAPSHOT
    if recovery:
        # Not yet possible to export a snapshot on a standby server:
        # http://www.postgresql.org/message-id/CAHGQGwEtJCeHUB6KzaiJ6ndvx6EFsidTGnuLwJ1itwVH0EJTOA@mail.gmail.com
        query = connection.execute(
            "SET TRANSACTION ISOLATION LEVEL READ COMMITTED, READ ONLY;"
            "SELECT txid_snapshot_xmin(txid_current_snapshot()), NULL;"
        )
    else:
        query = connection.execute(
            "SET TRANSACTION ISOLATION LEVEL SERIALIZABLE, READ ONLY, DEFERRABLE;"
            "SELECT txid_snapshot_xmin(txid_current_snapshot()), pg_export_snapshot();"
        )
    # DEFERRABLE prevents query cancelling due to conflicts but requires SERIALIZABLE mode
    # which is not available in recovery.
    result, = query.fetchall()
    xmin, snapshot_id = result  # lowest xid that is still in progress

    first_txn = None
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
            if first_txn is None:
                first_txn = txn.timestamp
            else:
                first_txn = min(first_txn, txn.timestamp)
            renamed.update(txn.data.get('renamed', ()))
            updated.update(txn.data.get('updated', ()))

        result['txn_count'] = txn_count
        if txn_count == 0:
            return result

        es.indices.refresh(index=INDEX)
        res = es.search(index=INDEX, size=SEARCH_MAX, body={
            'filter': {
                'or': [
                    {
                        'terms': {
                            'embedded_uuids': updated,
                            '_cache': False,
                        },
                    },
                    {
                        'terms': {
                            'linked_uuids': renamed,
                            '_cache': False,
                        },
                    },
                ],
            },
            '_source': False,
        })
        if res['hits']['total'] > SEARCH_MAX:
            invalidated = all_uuids(request.root)
        else:
            referencing = {hit['_id'] for hit in res['hits']['hits']}
            invalidated = referencing | updated
            result.update(
                max_xid=max_xid,
                renamed=renamed,
                updated=updated,
                referencing=len(referencing),
                invalidated=len(invalidated),
                txn_count=txn_count,
                first_txn_timestamp=first_txn.isoformat(),
            )

    if not dry_run:
        result['indexed'] = indexer.update_objects(request, invalidated, xmin, snapshot_id)
        if record:
            es.index(index=INDEX, doc_type='meta', body=result, id='indexing')

        es.indices.refresh(index=INDEX)

    if first_txn is not None:
        result['lag'] = str(datetime.datetime.now(pytz.utc) - first_txn)

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


class Indexer(object):
    def __init__(self, registry):
        self.es = registry[ELASTIC_SEARCH]

    def update_objects(self, request, uuids, xmin, snapshot_id):
        i = -1
        for i, uuid in enumerate(uuids):
            path = self.update_object(request, uuid, xmin)

            if (i + 1) % 50 == 0:
                log.info('Indexing %s %d', path, i + 1)

        return i + 1

    def update_object(self, request, uuid, xmin):
        try:
            result = request.embed('/%s/@@index-data' % uuid, as_user='INDEXER')
        except Exception:
            log.warning('Error indexing %s', uuid, exc_info=True)
            return uuid

        doctype = result['object']['@type'][0]
        try:
            self.es.index(
                index=INDEX, doc_type=doctype, body=result,
                id=str(uuid), version=xmin, version_type='external_gte',
            )
        except StatementError:
            # Can't reconnect until invalid transaction is rolled back
            raise
        except ConflictError:
            log.warning('Conflict indexing %s at version %d', uuid, xmin, exc_info=True)
        except Exception:
            log.warning('Error indexing %s', uuid, exc_info=True)
        return result['object']['@id']

    def shutdown(self):
        pass


@subscriber(Created)
@subscriber(BeforeModified)
@subscriber(AfterModified)
def record_updated_uuid_paths(event):
    context = event.object
    updated = event.request._updated_uuid_paths
    uuid = str(context.uuid)
    name = resource_path(context)
    updated[uuid].add(name)


@subscriber(BeforeModified)
def record_initial_back_revs(event):
    context = event.object
    initial = event.request._initial_back_rev_links
    properties = context.upgrade_properties()
    initial[context.uuid] = {
        path: set(simple_path_ids(properties, path))
        for path in context.type_info.merged_back_rev
    }


@subscriber(Created)
@subscriber(AfterModified)
def invalidate_new_back_revs(event):
    ''' Invalidate objects that rev_link to us
    Catch those objects which newly rev_link us
    '''
    context = event.object
    updated = event.request._updated_uuid_paths
    initial = event.request._initial_back_rev_links.get(context.uuid, {})
    properties = context.upgrade_properties()
    current = {
        path: set(simple_path_ids(properties, path))
        for path in context.type_info.merged_back_rev
    }
    for rel, uuids in current.items():
        for uuid in uuids.difference(initial.get(rel, ())):
            updated[uuid]


@subscriber(BeforeRender)
def es_update_data(event):
    request = event['request']
    updated_uuid_paths = request._updated_uuid_paths

    if not updated_uuid_paths:
        return

    txn = transaction.get()
    data = txn._extension
    renamed = data['renamed'] = [
        uuid for uuid, names in updated_uuid_paths.items()
        if len(names) > 1
    ]
    updated = data['updated'] = list(updated_uuid_paths.keys())

    response = request.response
    response.headers['X-Updated'] = ','.join(updated)
    if renamed:
        response.headers['X-Renamed'] = ','.join(renamed)

    record = data.get('_encoded_transaction_record')
    if record is None:
        return

    xid = record.xid
    if xid is None:
        return

    response.headers['X-Transaction'] = str(xid)

    # Only set session cookie for web users
    namespace = None
    login = request.authenticated_userid
    if login is not None:
        namespace, userid = login.split('.', 1)

    if namespace == 'mailto':
        edits = request.session.setdefault('edits', [])
        edits.append([xid, list(updated), list(renamed)])
        edits[:] = edits[-10:]

    # XXX How can we ensure consistency here but update written records
    # immediately? The listener might already be indexing on another
    # connection. SERIALIZABLE isolation insufficient because ES writes not
    # serialized. Could either:
    # - Queue up another reindex on the listener
    # - Use conditional puts to ES based on serial before commit.
    # txn = transaction.get()
    # txn.addAfterCommitHook(es_update_object_in_txn, (request, updated))


def get_file(es, properties):
    print("Indexing file - " + properties['href'])
    urllib3.disable_warnings()
    http = urllib3.PoolManager()
    r = http.request('GET', 'https://www.encodedcc.org' + properties['href'])
    comp = io.BytesIO()
    comp.write(r.data)
    comp.seek(0)
    f = gzip.GzipFile(fileobj=comp, mode='rb')
    del comp
    r.release_conn()
    file_data = pd.read_csv(
        f, delimiter='\t', header=None, chunksize=10000, engine="python")
    for new_frame in file_data:
        # dropping useless columns
        if len(new_frame.columns) == 10:
            new_frame = new_frame.drop([3, 4, 5, 6, 7, 8, 9], 1)
        elif len(new_frame.columns) == 9:
            new_frame = new_frame.drop([3, 4, 5, 6, 7, 8], 1)
        else:
            print(properties['uuid'])
            continue
        new_frame.columns = ['chromosome', 'start', 'end']
        new_frame[['start', 'end']] = new_frame[['start', 'end']].astype(int)
        new_frame = new_frame[~np.isnan(new_frame['start'])]
        new_frame = new_frame[~np.isnan(new_frame['end'])]
        new_frame['start'] = new_frame['start'] + 1
        new_frame['end'] = new_frame['end'] + 1
        new_frame['uuid'] = properties['uuid']
        gp_chr = dict(list(new_frame.groupby('chromosome')))
        for g in gp_chr:
            chr_data = gp_chr[g]
            try:
                es.create(index=g)
            except:
                pass
            records = chr_data.where(pd.notnull(chr_data), None).T.to_dict()
            list_records = [records[it] for it in records]
            helpers.bulk(
                es,
                list_records,
                index=g,
                doc_type=properties['assembly']
            )


@view_config(route_name='file_index', request_method='POST', permission="index")
def file_index(request):
    '''Indexes bed files in ENCODE'''

    es = request.registry.get(ELASTIC_SEARCH, None)
    params = {
        'type': ['experiment'],
        'status': ['released'],
        'assay_term_name': ['ChIP-seq', 'DNase-seq'],
        'replicates.library.biosample.donor.organism.scientific_name': ['Homo sapiens'],
        'field': ['assay_term_name', 'files.href', 'files.assembly', 'files.uuid',
                  'files.output_type', 'files.file_format'],
        'limit': ['all']
    }
    path = '/search/?%s' % urlencode(params, True)
    for properties in embed(request, path, as_user=True)['@graph']:
        for f in properties['files']:
            # This is totally hack to restrict number of files indexed.
            if properties['assay_term_name'] == 'ChIP-seq' and \
                    f['output_type'] == 'UniformlyProcessedPeakCalls':
                    get_file(es, f)
            else:
                if f['file_format'] == 'bed_narrowPeak':
                    get_file(es, f)
