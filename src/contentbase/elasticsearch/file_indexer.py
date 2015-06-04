import urllib3
import io
import gzip
import csv
from ..embedding import embed
from urllib.parse import (
    urlencode,
)
from collections import defaultdict
from pyramid.view import view_config
from .interfaces import ELASTIC_SEARCH


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
                    'type': 'long'
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
    file_data = defaultdict(set)
    with gzip.open(comp, mode="rt") as file:
        for row in tsvreader(file):
            chrom, start, end = row[0].lower(), int(row[1]), int(row[2])
            if isinstance(start, int) and isinstance(end, int):
                    file_data[chrom].update(range(start, end + 1))
    for key in file_data:
        doc = {
            'uuid': properties['uuid'],
            'positions': list(set(file_data[key]))
        }
        if not es.indices.exists(key):
            es.indices.create(index=key)
            es.indices.put_mapping(index=key, doc_type='hg19', body=get_mapping())
        es.index(index=key, doc_type=properties['assembly'], body=doc, id=properties['uuid'])


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
