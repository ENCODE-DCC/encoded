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

# Assays and corresponding file types that are being indexed
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
    config.add_route('file_index', '/file_index')
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
            'uuid': properties['uuid'],
            'positions': file_data[key]
        }
        if not es.indices.exists(key):
            es.indices.create(index=key)
            es.indices.put_mapping(index=key, doc_type='hg19',
                                   body=get_mapping())
        es.index(index=key, doc_type=properties['assembly'],
                 body=doc, id=properties['uuid'])


@view_config(route_name='file_index', request_method='POST', permission="index")
def file_index(request):
    '''Indexes bed files in ENCODE'''

    es = request.registry.get(ELASTIC_SEARCH, None)
    params = {
        'type': ['experiment'],
        'status': ['released'],
        'assay_term_name': [assay for assay in _INDEXED_DATA],
        'replicates.library.biosample.donor.organism.scientific_name':
        [organism for organism in _SPECIES],
        'field': ['files.href', 'files.assembly', 'files.uuid',
                  'files.output_type', 'files.file_type', 'assay_term_name'],
        'limit': ['all']
    }
    path = '/search/?%s' % urlencode(params, True)
    for properties in embed(request, path, as_user=True)['@graph']:
        for f in properties['files']:
            for k, v in _INDEXED_DATA[properties['assay_term_name']].items():
                if k in f and f[k] in v:
                    get_file(es, f)
                    break
