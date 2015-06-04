from elasticsearch.exceptions import (
    ConflictError,
    NotFoundError,
)
from pyramid.view import view_config
from sqlalchemy.exc import StatementError
from contentbase import DBSESSION
from contentbase.storage import (
    TransactionRecord,
)
from .interfaces import ELASTIC_SEARCH
import datetime
import logging
import pytz
import urllib3
import io
import gzip
import csv
from ..embedding import embed
from urllib.parse import (
    urlencode,
)


log = logging.getLogger(__name__)
INDEXER = 'indexer'
SEARCH_MAX = 99999  # OutOfMemoryError if too high


def includeme(config):
    config.add_route('index', '/index')
    config.add_route('file_index', '/file_index')
    config.scan(__name__)
    registry = config.registry
    registry[INDEXER] = Indexer(registry)


@view_config(route_name='index', request_method='POST', permission="index")
def index(request):
    INDEX = request.registry.settings['contentbase.elasticsearch.index']
    # Setting request.datastore here only works because routed views are not traversed.
    request.datastore = 'database'
    record = request.json.get('record', False)
    dry_run = request.json.get('dry_run', False)
    recovery = request.json.get('recovery', False)
    es = request.registry[ELASTIC_SEARCH]
    indexer = request.registry[INDEXER]

    session = request.registry[DBSESSION]()
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
        self.index = registry.settings['contentbase.elasticsearch.index']

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
                index=self.index, doc_type=doctype, body=result,
                id=str(uuid), version=xmin, version_type='external_gte',
                request_timeout=30,
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


def tsvreader(file):
    reader = csv.reader(file, delimiter='\t')
    for row in reader:
        yield row


def get_file(es, properties):
    url = 'https://www.encodedcc.org' + properties['href']
    print("Indexing file - " + url)
    urllib3.disable_warnings()
    http = urllib3.PoolManager()
    r = http.request('GET', url)
    comp = io.BytesIO()
    comp.write(r.data)
    comp.seek(0)
    r.release_conn()
    file_data = {}
    with gzip.open(comp, mode="rt") as file:
        for row in tsvreader(file):
            chrom, start, end = row[0].lower(), int(row[1]), int(row[2])
            if isinstance(start, int) and isinstance(end, int):
                if chrom in file_data:
                    file_data[chrom] = file_data[chrom] + list(range(start, end))
                else:
                    file_data[chrom] = list(range(start, end))
    for key in file_data:
        doc = {
            'uuid': properties['uuid'],
            'coordinates': list(set(file_data[key]))
        }
        try:
            es.create(index=key)
        except:
            pass
        es.index(index=key, doc_type=properties['assembly'],
                 body=doc, id=properties['uuid'])


@view_config(route_name='file_index', request_method='POST', permission="index")
def file_index(request):
    '''Indexes bed files in ENCODE'''

    es = request.registry.get(ELASTIC_SEARCH, None)
    params = {
        'type': ['experiment'],
        'status': ['released'],
        'assay_term_name': ['ChIP-seq', 'DNase-seq'],
        'replicates.library.biosample.donor.organism.scientific_name': ['Homo sapiens'],
        'field': ['files.href', 'files.assembly', 'files.uuid',
                  'files.output_type', 'files.file_format_type',
                  'files.file_format', 'assay_term_name'],
        'limit': ['all']
    }
    path = '/search/?%s' % urlencode(params, True)
    for properties in embed(request, path, as_user=True)['@graph']:
        for f in properties['files']:
            # This is totally hack to restrict number of files indexed.
            if f['file_format'] == 'bed':
                if properties['assay_term_name'] == 'ChIP-seq' and \
                        f['output_type'] == 'optimal idr thresholded peaks':
                    get_file(es, f)
                elif properties['assay_term_name'] == 'DNase-seq' and \
                        'file_format_type' in f and \
                        f['file_format_type'] == 'narrowPeak':
                    get_file(es, f)
