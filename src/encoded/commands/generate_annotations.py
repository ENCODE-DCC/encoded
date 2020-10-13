import requests
import json
import re


EPILOG = __doc__

_GENE_URL = 'https://www.encodeproject.org/search/?type=Gene&format=json&locations=*&field=geneid&field=name&field=symbol&field=synonyms&field=dbxrefs&field=locations&field=organism.scientific_name&organism.scientific_name=Homo+sapiens&organism.scientific_name=Mus+musculus&limit=all'


def get_annotation():
    return {
        'assembly_name': '',
        'chromosome': '',
        'start': '',
        'end': ''
    }


def all_annotations(url):
    annotations = []
    response = requests.get(url)
    for gene in response.json()['@graph']:
        doc = {'annotations': []}

        if 'organism' in gene:
            organism = gene['organism'].get('scientific_name')
            if organism == 'Homo sapiens':
                species = ' (homo sapiens)'
            elif organism == 'Mus musculus':
                species = ' (mus musculus)'
            elif organism == 'Caenorhabditis elegans':
                species = ' (caenorhabditis elegans)'
            elif organism == 'Drosophila melanogaster':
                species = ' (drosophila melanogaster)'

            if 'dbxrefs' in gene:
                identifier = [x for x in gene['dbxrefs'] if x.startswith(('HGNC:', 'MGI:', 'WormBase:', 'FlyBase:'))]
                if len(identifier) != 1:
                    continue
                if len(identifier) == 1:
                    identifier = ''.join(identifier)

                    if 'name' not in gene:
                        continue

                    if 'name' in gene:
                        species_for_payload = re.split('[(|)]', species)[1]
                        doc['payload'] = {'id': identifier, 'species': species_for_payload}
                        doc['id'] = identifier
                        if organism == 'Homo sapiens':
                            doc['suggest'] = {
                            'input': [gene['name'] + species, gene['symbol'] + species, identifier, gene['geneid'] + ' (Gene ID)']
                        }
                        elif organism == 'Mus musculus':
                            doc['suggest'] = {'input': [gene['symbol'] + species, identifier + species]}

                    if 'synonyms' in gene and organism == 'Homo sapiens':
                        synonyms = [s + species for s in gene['synonyms']]
                        doc['suggest']['input'] = doc['suggest']['input'] + synonyms

                    if 'locations' in gene:
                        for location in gene['locations']:
                            annotation = get_annotation()
                            assembly = location['assembly']
                            if assembly  == 'hg19':
                                annotation['assembly_name'] = 'GRCh37'
                            elif assembly == 'mm9':
                                annotation['assembly_name'] = 'GRCm37'
                            elif assembly == 'mm10':
                                annotation['assembly_name'] = 'GRCm38'
                            else:
                                annotation['assembly_name'] = assembly
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
    Get annotations from portal Gene objects
    This helps to implement autocomplete for region search
    '''
    import argparse
    parser = argparse.ArgumentParser(
        description="Generate annotations JSON file for multiple species",
        epilog=EPILOG,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    annotations = all_annotations(_GENE_URL)

    # Create annotations JSON file
    with open('annotations_local.json', 'w') as outfile:
        json.dump(annotations, outfile)


if __name__ == '__main__':
    main()
