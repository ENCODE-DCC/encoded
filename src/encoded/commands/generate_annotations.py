import requests
import json
import re
import time


EPILOG = __doc__

_HUMAN_URL = 'https://www.encodeproject.org/search/?type=Gene&format=json&locations=*&field=geneid&field=name&field=symbol&field=synonyms&field=dbxrefs&field=locations&organism.scientific_name=Homo+sapiens&limit=all'
_MOUSE_URL = 'https://www.encodeproject.org/search/?type=Gene&format=json&locations=*&field=geneid&field=name&field=symbol&field=synonyms&field=dbxrefs&field=locations&organism.scientific_name=Mus+musculus&limit=all'


def get_annotation():
    return {
        'assembly_name': '',
        'chromosome': '',
        'start': '',
        'end': ''
    }


def human_annotations(url):
    annotations = []
    species = ' (homo sapiens)'
    species_for_payload = re.split('[(|)]', species)[1]
    response = requests.get(url)
    for gene in response.json()['@graph']:
        doc = {'annotations': []}
        if 'dbxrefs' in gene:
            hgnc_id = [x for x in gene['dbxrefs'] if x.startswith('HGNC:')]
            if len(hgnc_id) == 1:
                hgnc_id = ''.join(hgnc_id)
                if 'name' in gene:
                    doc['suggest'] = {
                        'input': [gene['name'] + species, gene['symbol'] + species, hgnc_id, gene['geneid'] + ' (Gene ID)']
                    }
                    doc['payload'] = {'id': hgnc_id, 'species': species_for_payload}
                    doc['id'] = hgnc_id

                if 'synonyms' in gene:
                    synonyms = [s + species for s in gene['synonyms']]
                    doc['suggest']['input'] = doc['suggest']['input'] + synonyms

                annotation = get_annotation()

                if 'locations' in gene:
                    for location in gene['locations']:
                        annotation['assembly_name'] = location['assembly']
                        annotation['chromosome'] = location['chromosome'][3:]
                        annotation['start'] = location['start']
                        annotation['end'] = location['end']
                        doc['annotations'].append(annotation)

                annotations.append({
                    'index': {
                        '_index': 'annotations',
                        '_type': 'default',
                        '_id': doc['id']
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
        epilog=EPILOG,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    human = human_annotations(_HUMAN_URL)
    annotations = human

    # Create annotations JSON file
    with open('annotations_local.json', 'w') as outfile:
        json.dump(annotations, outfile)


if __name__ == '__main__':
    main()
