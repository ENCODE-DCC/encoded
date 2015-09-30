import urllib3
import io
import gzip
import csv
from contentbase.embed import embed
from urllib.parse import (
    urlencode,
)
from pyramid.view import view_config
from contentbase.elasticsearch import ELASTIC_SEARCH

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
_SPECIES = {
    'Homo sapiens': ['hg19']
}


def includeme(config):
    config.add_route('bulk_file_indexer', '/bulk_file_indexer')
    config.add_route('index_file', '/index_file')
    config.scan(__name__)


def tsvreader(file):
    reader = csv.reader(file, delimiter='\t')
    for row in reader:
        yield row


def get_mapping():
    return {
        'hg19': {
            '_all': {
                'enabled': False
            },
            '_source': {
                'enabled': False
            },
            'properties': {
                'uuid': {
                    'type': 'string',
                    'index': 'not_analyzed'
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


def get_assay_term_name(request, accession):
    '''
    Input file accession and returns assay_term_name of the experiment the file
    belongs to
    '''
    context = request.embed(accession)
    if 'assay_term_name' in context:
        return context['assay_term_name']
    return None


@view_config(route_name='index_file', request_method='POST', permission="index")
def index_file(context, request):
    """
    Indexes bed files in elasticsearch index
    """

    # if file doesn't have dataset then just don't index
    if 'dataset' not in context:
        return

    # If no status or not released just return
    if 'status' not in context and context['status'] is not 'released':
        return

    # Guard if assay_term_name doesn't exist
    assay_term_name = get_assay_term_name(request, context['dataset'])
    if assay_term_name is None:
        return

    # We are only certain bed files for given assays. This validates them.
    flag = False
    for k, v in _INDEXED_DATA[assay_term_name].items():
        if k in context and context[k] in v:
            if 'file_format' in context and context['file_format'] == 'bed':
                flag = True
                break
    if not flag:
        return

    es = request.registry.get(ELASTIC_SEARCH, None)
    url = 'https://www.encodeproject.org' + context['href']
    urllib3.disable_warnings()
    http = urllib3.PoolManager()
    r = http.request('GET', url)
    comp = io.BytesIO()
    comp.write(r.data)
    comp.seek(0)
    r.release_conn()
    file_data = dict()
    with gzip.open(comp, mode="rt") as file:
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
    for key in file_data:
        doc = {
            'uuid': context['uuid'],
            'positions': file_data[key]
        }
        if not es.indices.exists(key):
            es.indices.create(index=key, body=index_settings())
            es.indices.put_mapping(index=key, doc_type='hg19',
                                   body=get_mapping())
        es.index(index=key, doc_type=context['assembly'], body=doc,
                 id=context['uuid'])


@view_config(route_name='bulk_file_indexer', request_method='POST', permission="index")
def bulk_file_indexer(request):
    '''
    Utility view to index all bed files in elasticsearch
    TODO: This should be removed once peak indexer is integrated with real time
    indexing.
    '''

    params = {
        'type': ['experiment'],
        'status': ['released'],
        'assay_term_name': [assay for assay in _INDEXED_DATA],
        'replicates.library.biosample.donor.organism.scientific_name':
        [organism for organism in _SPECIES],
        'field': ['files.href', 'files.assembly', 'files.uuid',
                  'files.output_type', 'files.file_type', 'files.file_format',
                  'assay_term_name', 'files.status', 'files.dataset'],
        'limit': ['all']
    }
    path = '/search/?%s' % urlencode(params, True)
    for properties in embed(request, path, as_user=True)['@graph']:
        for f in properties['files']:
            index_file(f, request)
