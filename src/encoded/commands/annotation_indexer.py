import logging
import requests
from pyramid.paster import get_app
from contentbase.elasticsearch import ELASTIC_SEARCH
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
_GENEINFO_URL = 'http://mygene.info/v2/gene/'


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
    species = ' (homo sapiens)'
    counter = 0
    response = requests.get(_HGNC_FILE)
    header = []
    for row in response.content.decode('utf-8').split('\n'):
        # skipping header row
        if counter == 0:
            header = row.split('\t')
            counter += 1
            continue
        r = dict(zip(header, row.split('\t')))
        if r['Ensembl Gene ID'] is None:
            continue
        r['annotations'] = []
        r['name_suggest'] = {
            'input': [r['Approved Name'] + species,
                      r['Approved Symbol'] + species,
                      r['Ensembl Gene ID'] + species,
                      r['HGNC ID'] + species],
            'payload': {'id': counter}
        }

        # Adding gene synonyms to autocomplete
        if r['Synonyms'] is not None:
            synonyms = [x.strip(' ') + species for x in r['Synonyms'].split(',')]
            r['name_suggest']['input'] = r['name_suggest']['input'] + synonyms

        # Adding Entrez gene id if there exists one to autocomplete
        if 'Entrez Gene ID' in r:
            if isinstance(r['Entrez Gene ID'], float):
                r['name_suggest']['input'].append(
                    str(int(r['Entrez Gene ID'])) + ' (Gene ID)')

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
        es.index(index=index, doc_type=doc_type, body=r, id=counter)
        counter += 1


def all_annotations(es):
    """
    Mouse, C Elegans, Drosophila annotations are handled here
    """
    urls = [_MOUSE_FILE, _DM_FILE, _CE_FILE]
    counter = 0
    for url in urls:
        response = requests.get(_HGNC_FILE)
        header = []
        for row in response.content.decode('utf-8').split('\n'):
            # skipping header row
            if counter == 0:
                header = row.split('\t')
                counter += 1
                continue
            r = dict(zip(header, row.split('\t')))
            if 'Chromosome Name' not in r:
                continue
            counter += 1
            r['annotations'] = []
            annotation = get_annotation()
            if url == _MOUSE_FILE:
                species = ' (mus musculus)'
                r['name_suggest'] = {
                    'input': [r['Ensembl Gene ID'] + species],
                    'payload': {'id': counter}
                }
                if 'MGI symbol' in r and r['MGI symbol'] is not None:
                    r['name_suggest']['input'].append(r['MGI symbol'] + species)
                if 'MGI ID' in r and r['MGI ID'] is not None:
                    r['name_suggest']['input'].append(r['MGI ID'] + species)
                annotation['assembly_name'] = 'GRCm38'
                mm9_url = '{geneinfo}{ensembl}?fields=genomic_pos_mm9'.format(
                    geneinfo=_GENEINFO_URL,
                    ensembl=r['Ensembl Gene ID']
                )
                try:
                    response = requests.get(mm9_url).json()
                except:
                    continue
                else:
                    if 'genomic_pos_mm9' in response and isinstance(response['genomic_pos_mm9'], dict):
                            ann = get_annotation()
                            ann['assembly_name'] = 'GRCm37'
                            ann['chromosome'] = response['genomic_pos_mm9']['chr']
                            ann['start'] = response['genomic_pos_mm9']['start']
                            ann['end'] = response['genomic_pos_mm9']['end']
                            r['annotations'].append(ann)
            elif url == _DM_FILE:
                species = ' (drosophila melanogaster)'
                r['name_suggest'] = {
                    'input': [r['Associated Gene Name'] + species,
                              r['Ensembl Gene ID'] + species],
                    'payload': {'id': counter}
                }
                if 'Ensembl Gene ID.1' in r:
                    r['name_suggest']['input'].append(r['Ensembl Gene ID.1'] + species)
                annotation['assembly_name'] = 'BDGP6'
            else:
                species = ' (c. elegans)'
                r['name_suggest'] = {
                    'input': [r['Associated Gene Name'] + species,
                              r['Ensembl Gene ID'] + species],
                    'payload': {'id': counter}
                }
                annotation['assembly_name'] = 'WBcel235'

            # Adding Entrez gene id if there exists one to autocomplete
            if 'EntrezGene ID' in r:
                if isinstance(r['EntrezGene ID'], float):
                    r['name_suggest']['input'].append(str(int(r['EntrezGene ID'])) + ' (Gene ID)')

            annotation['chromosome'] = r['Chromosome Name']
            annotation['start'] = r['Gene Start (bp)']
            annotation['end'] = r['Gene End (bp)']
            r['annotations'].append(annotation)
            del r['Chromosome Name'], r['Gene Start (bp)'], r['Gene End (bp)']
            es.index(index=index, doc_type=doc_type, body=r, id=counter)


def create_index(es):
    ''' Create annotations index '''
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
    '''
    Get annotations from multiple sources
    This helps to implement autocomplete for region search
    '''

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
    try:
        create_index(es)
    except:
        pass
    else:
        human_annotations(es)


if __name__ == '__main__':
    main()
