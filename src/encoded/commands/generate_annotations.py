import requests
import json
import re
import time
import multiprocessing as mp

EPILOG = __doc__

_HGNC_FILE = 'https://www.encodeproject.org/files/ENCFF277WZC/@@download/ENCFF277WZC.tsv'
_MOUSE_FILE = 'https://www.encodeproject.org/files/ENCFF097CIT/@@download/ENCFF097CIT.tsv'
_DM_FILE = 'https://www.encodeproject.org/files/ENCFF311QAL/@@download/ENCFF311QAL.tsv'
_CE_FILE = 'https://www.encodeproject.org/files/ENCFF324UJT/@@download/ENCFF324UJT.tsv'
_ENSEMBL_URL = 'http://rest.ensembl.org/'
_GENEINFO_URL = 'http://mygene.info/v2/gene/'



def get_annotation():
    return {
        'assembly_name': '',
        'chromosome': '',
        'start': '',
        'end': ''
    }

def rate_limited_request(url):
    response = requests.get(url)
    if int(response.headers.get('X-RateLimit-Remaining')) < mp.cpu_count():
        print('spleeping for about {} seconds'.format(response.headers.get('X-RateLimit-Reset')))
        time.sleep(int(float(response.headers.get('X-RateLimit-Reset'))) + 1)
    return response.json()



def assembly_mapper(location, species, input_assembly, output_assembly):
    # All others
    new_url = _ENSEMBL_URL + 'map/' + species + '/' \
        + input_assembly + '/' + location + '/' + output_assembly \
        + '/?content-type=application/json'
    try:
        new_response = rate_limited_request(new_url)
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


def human_single_annotation(r):

        annotations = []
        species = ' (homo sapiens)'
        species_for_payload = re.split('[(|)]', species)[1]
        # Ensembl ID is used to grab annotations for different references
        if 'Ensembl Gene ID' not in r:
            return
        elif r['Ensembl Gene ID'] is None:
            return

        # Annotations are keyed by Gene ID in ES
        if 'Entrez Gene ID' not in r:
            return

        # Assumption: payload.id and id should always be same
        doc = {'annotations': []}
        doc['suggest'] = {
            'input': [r['Approved Name'] + species,
                      r['Approved Symbol'] + species,
                      r['HGNC ID'],
                      r['Entrez Gene ID'] + ' (Gene ID)']
            }
        doc['payload'] = {'id': r['HGNC ID'],
                        'species': species_for_payload
            }
        doc['id'] = r['HGNC ID']

        if r['Entrez Gene ID'].isdigit():
            r['Entrez Gene ID'] = int(r['Entrez Gene ID'])

        # Adding gene synonyms to autocomplete
        if r['Synonyms'] is not None and r['Synonyms'] != '':
            synonyms = [x.strip(' ') + species for x in r['Synonyms'].split(',')]
            doc['suggest']['input'] = doc['suggest']['input'] + synonyms

        url = '{ensembl}lookup/id/{id}?content-type=application/json'.format(
            ensembl=_ENSEMBL_URL,
            id=r['Ensembl Gene ID'])

        try:
            response = rate_limited_request(url)
        except:
            return
        else:
            annotation = get_annotation()
            if 'assembly_name' not in response:
                return
            annotation['assembly_name'] = response['assembly_name']
            annotation['chromosome'] = response['seq_region_name']
            annotation['start'] = response['start']
            annotation['end'] = response['end']
            doc['annotations'].append(annotation)

            # Get GRcH37 annotation
            location = response['seq_region_name'] \
                + ':' + str(response['start']) \
                + '-' + str(response['end'])
            ann = get_annotation()
            ann['assembly_name'] = 'GRCh37'
            ann['chromosome'], ann['start'], ann['end'] = \
                assembly_mapper(location, response['species'],
                                'GRCh38', 'GRCh37')
            doc['annotations'].append(ann)
        annotations.append({
            "index": {
                "_index": "annotations",
                "_type": "default",
                "_id": doc['id']
            }
        })
        annotations.append(doc)
        print('human {}'.format(time.time()))
        return annotations


def mouse_single_annotation(r):

    annotations = []

    if 'Chromosome Name' not in r:
        return

    doc = {'annotations': []}
    species = ' (mus musculus)'
    species_for_payload = re.split('[(|)]', species)[1]
    doc['suggest'] = {
        'input': []
        }
    doc['payload'] = {'id': r['Ensembl Gene ID'],
                    'species': species_for_payload
        }
    doc['id'] = r['Ensembl Gene ID']

    if 'MGI symbol' in r and r['MGI symbol'] is not None:
        doc['suggest']['input'].append(r['MGI symbol'] + species)

    if 'MGI ID' in r and r['MGI ID'] is not None:
        doc['suggest']['input'].append(r['MGI ID'] + species)

    doc['annotations'].append({
        'assembly_name': 'GRCm38',
        'chromosome': r['Chromosome Name'],
        'start': r['Gene Start (bp)'],
        'end': r['Gene End (bp)']
    })

    mm9_url = '{geneinfo}{ensembl}?fields=genomic_pos_mm9'.format(
        geneinfo=_GENEINFO_URL,
        ensembl=r['Ensembl Gene ID']
    )
    try:
        response = requests.get(mm9_url).json()
    except:
        return
    else:
        if 'genomic_pos_mm9' in response and isinstance(response['genomic_pos_mm9'], dict):
                ann = get_annotation()
                ann['assembly_name'] = 'GRCm37'
                ann['chromosome'] = response['genomic_pos_mm9']['chr']
                ann['start'] = response['genomic_pos_mm9']['start']
                ann['end'] = response['genomic_pos_mm9']['end']
                doc['annotations'].append(ann)
    annotations.append({
        "index": {
            "_index": "annotations",
            "_type": "default",
            "_id": doc['id']
        }
    })
    annotations.append(doc)
    print('mouse {}'.format(time.time()))
    return annotations


def get_rows_from_file(file_name, row_delimiter):
    response = requests.get(file_name)
    rows = response.content.decode('utf-8').split(row_delimiter)
    header = rows[0].split('\t')
    zipped_rows = [dict(zip(header, row.split('\t'))) for row in rows[1:]]
    return zipped_rows


def prepare_for_bulk_indexing(annotations):
    flattened_annotations = []
    for annotation in annotations:
        if annotation:
            for item in annotation:
                flattened_annotations.append(item)
    return flattened_annotations



def human_annotations(human_file):
    """
    Generates JSON from TSV files
    """
    zipped_rows = get_rows_from_file(human_file, '\r')
    pool = mp.Pool()
    annotations = pool.map(human_single_annotation, zipped_rows)
    return prepare_for_bulk_indexing(annotations)



def mouse_annotations(mouse_file):
    """
    Updates and get JSON file for mouse annotations
    """
    zipped_rows = get_rows_from_file(mouse_file, '\n')
    pool = mp.Pool()
    annotations = pool.map(mouse_single_annotation, zipped_rows)
    return prepare_for_bulk_indexing(annotations)


def other_annotations(file, species, assembly):
    """
    Generates C. elegans and drosophila annotaions
    """
    annotations = []
    response = requests.get(file)
    header = []
    species_for_payload = re.split('[(|)]', species)[1]
    for row in response.content.decode('utf-8').split('\n'):
        # skipping header row
        if len(header) == 0:
            header = row.split('\t')
            continue

        r = dict(zip(header, row.split('\t')))
        if 'Chromosome Name' not in r or 'Ensembl Gene ID' not in r:
            continue

        doc = {'annotations': []}
        annotation = get_annotation()

        doc['suggest'] = {
            'input': [r['Associated Gene Name'] + species]
            }
        doc['payload'] = {'id': r['Ensembl Gene ID'],
                        'species': species_for_payload
            }
        doc['id'] = r['Ensembl Gene ID']
        annotation['assembly_name'] = assembly
        annotation['chromosome'] = r['Chromosome Name']
        annotation['start'] = r['Gene Start (bp)']
        annotation['end'] = r['Gene End (bp)']
        doc['annotations'].append(annotation)
        annotations.append({
            "index": {
                "_index": "annotations",
                "_type": "default",
                "_id": doc['id']
            }
        })
        annotations.append(doc)
    return annotations


def main():
    '''
    Get annotations from multiple sources
    This helps to implement autocomplete for region search
    '''
    import argparse
    parser = argparse.ArgumentParser(
        description="Generate annotations JSON file for multiple species",
        epilog=EPILOG, formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    human = human_annotations(_HGNC_FILE)
    mouse = mouse_annotations(_MOUSE_FILE)
    annotations = human + mouse

    # Create annotations JSON file
    with open('annotations.json', 'w') as outfile:
        json.dump(annotations, outfile)


if __name__ == '__main__':
    main()
