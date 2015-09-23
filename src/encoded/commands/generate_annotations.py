import logging
import requests
import json

EPILOG = __doc__

_HGNC_FILE = 'https://s3-us-west-1.amazonaws.com/encoded-build/annotations/human/hgnc_dump_03-30-2015.tsv'
_MOUSE_FILE = 'https://s3-us-west-1.amazonaws.com/encoded-build/annotations/mouse/mouse.txt'
_DM_FILE = 'https://s3-us-west-1.amazonaws.com/encoded-build/annotations/drosophila/dm.txt'
_CE_FILE = 'https://s3-us-west-1.amazonaws.com/encoded-build/annotations/worm/c_elegans.txt'
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
    response = requests.get(_HGNC_FILE)
    header = []
    annotations = []
    for row in response.content.decode('utf-8').split('\n'):
        # Populating headers and skipping header row
        if len(header) == 0:
            header = row.split('\t')
            continue

        r = dict(zip(header, row.split('\t')))

        # Ensembl ID is used to grab annotations for different references
        if 'Ensembl Gene ID' not in r:
            continue
        elif r['Ensembl Gene ID'] is None:
            continue
            
        # Annotations are keyed by Gene ID in ES
        if 'Entrez Gene ID' not in r:
            continue

        # Assumption: payload.id and id should always be same
        doc = {'annotations': []}
        doc['name_suggest'] = {
            'input': [r['Approved Name'] + species,
                      r['Approved Symbol'] + species,
                      r['HGNC ID'],
                      r['Entrez Gene ID'] + ' (Gene ID)'],
            'payload': {'id': r['HGNC ID']}
        }
        doc['id'] = r['HGNC ID']

        if r['Entrez Gene ID'].isdigit():
            r['Entrez Gene ID'] = int(r['Entrez Gene ID'])

        # Adding gene synonyms to autocomplete
        if r['Synonyms'] is not None and r['Synonyms'] != '':
            synonyms = [x.strip(' ') + species for x in r['Synonyms'].split(',')]
            doc['name_suggest']['input'] = doc['name_suggest']['input'] + synonyms

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
    return annotations


def mouse_annotations(mouse_file):
    """
    Updates and get JSON file for mouse annotations
    """
    annotations = []
    response = requests.get(mouse_file)
    header = []
    for row in response.content.decode('utf-8').split('\n'):
        # skipping header row
        if len(header) == 0:
            header = row.split('\t')
            continue

        r = dict(zip(header, row.split('\t')))
        if 'Chromosome Name' not in r:
            continue

        doc = {'annotations': []}
        species = ' (mus musculus)'
        doc['name_suggest'] = {
            'input': [],
            'payload': {'id': r['Ensembl Gene ID']}
        }
        doc['id'] = r['Ensembl Gene ID']

        if 'MGI symbol' in r and r['MGI symbol'] is not None:
            doc['name_suggest']['input'].append(r['MGI symbol'] + species)

        if 'MGI ID' in r and r['MGI ID'] is not None:
            doc['name_suggest']['input'].append(r['MGI ID'] + species)

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
            continue
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
    return annotations


def other_annotations(file, species, assembly):
    """
    Generates C. elegans and drosophila annotaions
    """
    annotations = []
    response = requests.get(file)
    header = []
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

        doc['name_suggest'] = {
            'input': [r['Associated Gene Name'] + species],
            'payload': {'id': r['Ensembl Gene ID']}
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
    annotations = other_annotations(_DM_FILE, ' (D. melanogaster)', 'BDGP6') +\
        other_annotations(_CE_FILE, ' (C. elegans)', 'WBcel235') +\
        human_annotations(_HGNC_FILE) +\
        mouse_annotations(_MOUSE_FILE)

    # Create annotations JSON file
    with open('annotations.json', 'w') as outfile:
        json.dump(annotations, outfile)


if __name__ == '__main__':
    main()
