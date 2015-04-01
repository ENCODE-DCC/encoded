import logging
import pandas as pd
import requests
from pyramid.paster import get_app
from ..indexing import ELASTIC_SEARCH
from elasticsearch.exceptions import (
    RequestError,
)

index = 'annotations'
doc_type = 'default'

EPILOG = __doc__
_HGNC_FILE = 'https://s3-us-west-1.amazonaws.com/encoded-build/annotations/human/hgnc_dump_03-30-2015.tsv'
_MOUSE_FILE = 'https://s3-us-west-1.amazonaws.com/encoded-build/annotations/mouse/mouse.txt'
_DM_FILE = 'https://s3-us-west-1.amazonaws.com/encoded-build/annotations/drosophila/dm.txt'
_CE_FILE = 'https://s3-us-west-1.amazonaws.com/encoded-build/annotations/worm/c_elegans.txt'
_JSON_ANNOTATION_FILE = ''
_ENSEMBL_URL = 'http://rest.ensembl.org/'


def get_annotation():
    return {
        'assembly_name': '',
        'chromosome': '',
        'start': '',
        'end': ''
    }


def assembly_mapper(location, species, input_assembly, output_assembly):
    # All others
    new_url = _ENSEMBL_URL + 'map/' + species + '/' \
        + input_assembly + '/' + location + '/' + output_assembly \
        + '/?content-type=application/json'
    try:
        new_response = requests.get(new_url).json()
    except:
        return('', '', '')
    else:
        if not len(new_response['mappings']):
            return('', '', '')
        data = new_response['mappings'][0]['mapped']
        chromosome = data['seq_region_name']
        start = data['start']
        end = data['end']
        return(chromosome, start, end)


def human_annotations(es):
    """
    Generates JSON from TSV files
    """
    data_frame = pd.read_csv(_HGNC_FILE, delimiter='\t')
    records = data_frame.where(pd.notnull(data_frame), None).T.to_dict()
    results = [records[it] for it in records]
    counter = 0
    for i, r in enumerate(results):
        if r['Ensembl Gene ID'] is None:
            continue
        r['annotations'] = []
        r['name_suggest'] = {
            'input': [
                r['Approved Name'],
                r['Approved Symbol'],
                r['Ensembl Gene ID'],
                r['HGNC ID']
                ],
            'payload': {'id': i}
            }
        if r['Synonyms'] is not None:
            synonyms = [x.strip(' ') for x in r['Synonyms'].split(',')]
            r['name_suggest']['input'] = r['name_suggest']['input'] + synonyms

        url = '{ensembl}lookup/id/{id}?content-type=application/json'.format(
            ensembl=_ENSEMBL_URL,
            id=r['Ensembl Gene ID'])
        try:
            response = requests.get(url).json()
        except:
            continue
        else:
            annotation = get_annotation()
            if 'assembly_name' not in response:
                print(response)
                continue
            annotation['assembly_name'] = response['assembly_name']
            annotation['chromosome'] = response['seq_region_name']
            annotation['start'] = response['start']
            annotation['end'] = response['end']
            r['annotations'].append(annotation)

            # Get GRcH37 annotation
            location = response['seq_region_name'] \
                + ':' + str(response['start']) \
                + '-' + str(response['end'])
            ann = get_annotation()
            ann['assembly_name'] = 'GRCh37'
            ann['chromosome'], ann['start'], ann['end'] = \
                assembly_mapper(location, response['species'],
                                'GRCh38', 'GRCh37')
            r['annotations'].append(ann)
        es.index(index=index, doc_type=doc_type, body=r, id=i)
        counter = i
    return counter


def all_annotations(es, counter):
    """
    Mouse, C Elegans, Drosophila annotations are handled here
    """
    urls = [_CE_FILE]
    results = []
    for url in urls:
        data_frame = pd.read_csv(url, delimiter='\t')
        records = data_frame.where(pd.notnull(data_frame), None).T.to_dict()
        results = results + [records[it] for it in records]
        for r in results:
            counter += 1
            r['annotations'] = []
            annotation = get_annotation()
            if url == _MOUSE_FILE:
                r['name_suggest'] = {
                    'input': [r['MGI symbol'], r['Ensembl Gene ID'], r['MGI ID']],
                    'payload': {'id': counter}
                }
                annotation['assembly_name'] = 'GRCm38'
            elif url == _DM_FILE:
                r['name_suggest'] = {
                    'input': [r['Associated Gene Name'], r['Ensembl Gene ID'],
                              r['Ensembl Gene ID.1']],
                    'payload': {'id': counter}
                }
                annotation['assembly_name'] = 'BDGP6'
            else:
                r['name_suggest'] = {
                    'input': [r['Associated Gene Name'], r['Ensembl Gene ID']],
                    'payload': {'id': counter}
                }
                annotation['assembly_name'] = 'WBcel235'
            annotation['chromosome'] = r['Chromosome Name']
            annotation['start'] = r['Gene Start (bp)']
            annotation['end'] = r['Gene End (bp)']
            r['annotations'].append(annotation)
            del r['Chromosome Name'], r['Gene Start (bp)'], r['Gene End (bp)']
            es.index(index=index, doc_type=doc_type, body=r, id=counter)


def create_index(es):
    try:
        es.indices.create(index=index)
    except RequestError:
        es.indices.delete(index=index)
        es.indices.create(index=index)

    mapping = {
        'properties': {
            'name_suggest': {
                'type': 'completion',
                'index_analyzer': 'standard',
                'search_analyzer': 'standard',
                'payloads': True
            }
        }
    }
    try:
        es.indices.put_mapping(
            index=index,
            doc_type=doc_type,
            body={doc_type: mapping}
        )
    except:
        print("Could not create mapping for the collection %s", doc_type)
    else:
        es.indices.refresh(index=index)


def main():
    ''' Indexes Bed files are loaded to elasticsearch '''

    import argparse
    parser = argparse.ArgumentParser(
        description="Index data in Elastic Search", epilog=EPILOG,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument('--app-name', help="Pyramid app name in configfile")
    parser.add_argument('--reload-json', help="Generates JSON files if 'true' \
    is supplied.", action='store_true', default=False)
    parser.add_argument('config_uri', help="path to configfile")
    args = parser.parse_args()

    logging.basicConfig()
    app = args.app_name

    # Loading app will have configured from config file. Reconfigure here:
    logging.getLogger('encoded').setLevel(logging.DEBUG)
    app = get_app(args.config_uri, args.app_name)
    es = app.registry[ELASTIC_SEARCH]
    create_index(es)
    counter = human_annotations(es)
    all_annotations(es, counter)


if __name__ == '__main__':
    main()
