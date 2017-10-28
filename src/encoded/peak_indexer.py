import urllib3
import io
import gzip
import csv
import logging
import collections
from pyramid.view import view_config
from sqlalchemy.sql import text
from elasticsearch.exceptions import (
    NotFoundError
)
from snovault import DBSESSION, COLLECTIONS
from snovault.storage import (
    TransactionRecord,
)
from snovault.elasticsearch.indexer import all_uuids
from snovault.elasticsearch.interfaces import (
    ELASTIC_SEARCH,
    SNP_SEARCH_ES,
)
import copy
from pprint import pprint as pp

SEARCH_MAX = 99999  # OutOfMemoryError if too high
log = logging.getLogger(__name__)


# hashmap of assays and corresponding file types that are being indexed
_INDEXED_DATA = {
    'ChIP-seq': {
        'output_type': ['optimal idr thresholded peaks'],
    },
    'DNase-seq': {
        'file_type': ['bed narrowPeak']
    },
    'eCLIP': {
        'file_type': ['bed narrowPeak']
    }
}

# Species and references being indexed
_ASSEMBLIES = ['hg19', 'mm10', 'mm9', 'GRCh38']


def includeme(config):
    config.add_route('index_file', '/index_file')
    config.scan(__name__)



def tsvreader(file):
    reader = csv.reader(file, delimiter='\t')
    for row in reader:
        yield row

# Mapping should be generated dynamically for each assembly type


def get_mapping(assembly_name='hg19'):
    return {
        assembly_name: {
            '_all': {
                'enabled': False
            },
            '_source': {
                'enabled': True
            },
            'properties': {
                'uuid': {
                    'type': 'keyword',
                },
                'positions': {
                    'type': 'nested',
                    'properties': {
                        'start': {
                            'type': 'long'
                        },
                        'end': {
                            'type': 'long'
                        }
                    }
                }
            }
        }
    }


def index_settings():
    return {
        'index': {
            'number_of_shards': 1
        }
    }


def get_assay_term_name(accession, request):
    '''
    Input file accession and returns assay_term_name of the experiment the file
    belongs to
    '''
    context = request.embed(accession)
    if 'assay_term_name' in context:
        return context['assay_term_name']
    return None


def all_bed_file_uuids(request):
    stmt = text("select distinct(resources.rid) from resources, propsheets where resources.rid = propsheets.rid and resources.item_type='file' and propsheets.properties->>'file_format' = 'bed' and properties->>'status' = 'released';")
    connection = request.registry[DBSESSION].connection()
    uuids = connection.execute(stmt)
    return [str(item[0]) for item in uuids]


def index_peaks(uuid, request):
    """
    Indexes bed files in elasticsearch index
    """
    context = request.embed('/', str(uuid), '@@object')
    if 'assembly' not in context:
        return

    assembly = context['assembly']

    # Treat mm10-minimal as mm1
    if assembly == 'mm10-minimal':
        assembly = 'mm10'



    if 'File' not in context['@type'] or 'dataset' not in context:
        return

    if 'status' not in context or context['status'] != 'released':
        return

    # Index human data for now
    if assembly not in _ASSEMBLIES:
        return

    assay_term_name = get_assay_term_name(context['dataset'], request)
    if assay_term_name is None or isinstance(assay_term_name, collections.Hashable) is False:
        return

    flag = False

    for k, v in _INDEXED_DATA.get(assay_term_name, {}).items():
        if k in context and context[k] in v:
            if 'file_format' in context and context['file_format'] == 'bed':
                flag = True
                break
    if not flag:
        return

    urllib3.disable_warnings()
    es = request.registry.get(SNP_SEARCH_ES, None)
    http = urllib3.PoolManager()
    r = http.request('GET', request.host_url + context['href'])
    if r.status != 200:
        return
    comp = io.BytesIO()
    comp.write(r.data)
    comp.seek(0)
    r.release_conn()
    file_data = dict()

    with gzip.open(comp, mode='rt') as file:
        for row in tsvreader(file):
            chrom, start, end = row[0].lower(), int(row[1]), int(row[2])
            if isinstance(start, int) and isinstance(end, int):
                if chrom in file_data:
                    file_data[chrom].append({
                        'start': start + 1,
                        'end': end + 1
                    })
                else:
                    file_data[chrom] = [{'start': start + 1, 'end': end + 1}]
            else:
                log.warn('positions are not integers, will not index file')

    for key in file_data:
        doc = {
            'uuid': context['uuid'],
            'positions': file_data[key]
        }
        if not es.indices.exists(key):
            es.indices.create(index=key, body=index_settings())

        if not es.indices.exists_type(index=key, doc_type=assembly):
            es.indices.put_mapping(index=key, doc_type=assembly, body=get_mapping(assembly))

        es.index(index=key, doc_type=assembly, body=doc, id=context['uuid'])


@view_config(route_name='index_file', request_method='POST', permission="index")
def index_file(request):
    registry = request.registry
    INDEX = registry.settings['snovault.elasticsearch.index']
    request.datastore = 'database'
    dry_run = request.json.get('dry_run', False)
    recovery = request.json.get('recovery', False)
    record = request.json.get('record', False)
    es = registry[ELASTIC_SEARCH]
    es_peaks = registry[SNP_SEARCH_ES]

    session = registry[DBSESSION]()
    connection = session.connection()
    if recovery:
        query = connection.execute(
            "SET TRANSACTION ISOLATION LEVEL READ COMMITTED, READ ONLY;"
            "SELECT txid_snapshot_xmin(txid_current_snapshot());"
        )
    else:
        query = connection.execute(
            "SET TRANSACTION ISOLATION LEVEL SERIALIZABLE, READ ONLY, DEFERRABLE;"
            "SELECT txid_snapshot_xmin(txid_current_snapshot());"
        )
    xmin = query.scalar()  # lowest xid that is still in progress

    first_txn = None
    last_xmin = None
    if 'last_xmin' in request.json:
        last_xmin = request.json['last_xmin']
    else:
        try:
            status = es_peaks.get(index='snovault', doc_type='meta', id='peak_indexing')
        except NotFoundError:
            pass
        else:
            last_xmin = status['_source']['xmin']

    result = {
        'xmin': xmin,
        'last_xmin': last_xmin,
    }
    if last_xmin is None:
        result['types'] = request.json.get('types', None)
        invalidated = list(all_uuids(registry))
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

        es.indices.refresh(index='_all')
        res = es.search(index='_all', size=SEARCH_MAX, body={
            'query': {
                'bool': {
                    'should': [
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
            }
        })
        if res['hits']['total'] > SEARCH_MAX:
            invalidated = list(all_uuids(request.registry))
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
        err = None
        uuid_current = None
        pp('length of invalidated {}'.format(len(invalidated)))
        invalidated_files = list(set(invalidated).intersection(set(all_bed_file_uuids(request))))
        try:
            files_indexed = 0
            for uuid in invalidated_files:
                uuid_current = uuid
                index_peaks(uuid, request)
                files_indexed += 1
        except Exception as e:
            log.error('Error indexing %s', uuid_current, exc_info=True)
            err = repr(e)
        result['errors'] = [err]
        result['indexed'] = len(invalidated)
        if record:
            try:
                es_peaks.index(index='snovault', doc_type='meta', body=result, id='peak_indexing')
            except:
                error_messages = copy.deepcopy(result['errors'])
                del result['errors']
                es_peaks.index(index='snovault', doc_type='meta', body=result, id='peak_indexing')
                for item in error_messages:
                    if 'error' in item:
                        log.error('Indexing error for {}, error message: {}'.format(item['uuid'], item['error']))
                        item['error'] = "Error occured during indexing, check the logs"
                result['errors'] = error_messages

    return result