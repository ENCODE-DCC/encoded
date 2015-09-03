from pyramid.view import view_config
from contentbase.elasticsearch import ELASTIC_SEARCH
from pyramid.security import effective_principals
from .search import (
    load_columns,
    load_results,
    set_filters,
    set_facets,
    get_filtered_query,
    load_facets
)
from collections import OrderedDict
import requests

_ENSEMBL_URL = 'http://rest.ensembl.org/'

_ASSEMBLY_MAPPER = {
    'GRCh38': 'hg20',
    'GRCh37': 'hg19',
    'GRCm38': 'mm10',
    'GRCm37': 'mm9',
    'BDGP6': 'dm4',
    'BDGP5': 'dm3',
    'WBcel235': 'WBcel235'
}

_REGION_FIELDS = [
    'embedded.files.uuid',
    'embedded.files.accession',
    'embedded.files.href',
    'embedded.files.file_format',
    'embedded.files.assembly',
    'embedded.files.output_type',
    'embedded.files.derived_from.uuid'
]

_FACETS = [
    ('assay_term_name', {'title': 'Assay'}),
    ('biosample_term_name', {'title': 'Biosample term'}),
    ('target.label', {'title': 'Target'}),
    ('Organism', {
        'title': 'replicates.library.biosample.donor.organism.scientific_name'
    }),
    ('Organ', {'title': 'replicates.library.biosample.organ_slims'})
]


def includeme(config):
    config.add_route('region-search', '/region-search{slash:/?}')
    config.add_route('suggest', '/suggest{slash:/?}')
    config.scan(__name__)


def get_peak_query(start, end):
    """
    return peak query
    """
    return {
        'query': {
            'filtered': {
                'filter': {
                    'nested': {
                        'path': 'positions',
                        'filter': {
                            'bool': {
                                'must': [
                                    {
                                        'range': {
                                            'positions.start': {
                                                'lte': end,
                                            }
                                        }
                                    },
                                    {
                                        'range': {
                                            'positions.end': {
                                                'gte': start,
                                            }
                                        }
                                    }
                                ]
                            }
                        }
                    }
                },
                '_cache': True,
            }
        }
    }


def sanitize_coordinates(term):
    terms = term.split(':')
    chromosome = terms[0]
    positions = terms[1].split('-')
    if len(positions) > 0 and len(positions) == 1:
        start = end = positions[0].replace(',', '')
    elif len(positions) == 2:
        start = positions[0].replace(',', '')
        end = positions[1].replace(',', '')
    return chromosome, start, end


def get_annotation_coordinates(es, id):
    ''' Gets annotation coordinates from annotation index in ES '''

    chromosome, start, end  = '', '', ''
    try:
        es_results = es.get(index='annotations', doc_type='default', id=id)
    except:
        return chromosome, start, end
    else:
        annotations = es_results['_source']['annotations']
        for annotation in annotations:
            if annotation['assembly_name'] == 'GRCh37':
                chromosome = 'chr%s' % (annotation['chromosome'])
                start = annotation['start']
                end = annotation['end']
    return chromosome, start, end


def get_derived_files(results, file_uuids):
    ''' Associate bed and bigBed files to draw tracks '''

    new_results = []
    for item in results:
        item['highlight'] = []
        new_files = []
        for f in item['files']:
            if 'file_format' not in f or f['file_format'] not in ['bigBed', 'bed']:
                continue
            if 'derived_from' in f:
                if f['uuid'] in file_uuids:
                    # handling bed files derived from bigBed files
                    for derived_file in f['derived_from']:
                        if derived_file['file_format'] == 'bigBed':
                            item['highlight'].append({
                                'bed': f['accession'],
                                'bigBed': derived_file['accession']
                            })
                            new_files.append(derived_file)
                else:
                    # Handing bigbed files derived from bed files
                    for derived_file in f['derived_from']:
                        if derived_file['uuid'] in file_uuids:
                            item['highlight'].append({
                                'bed': derived_file['accession'],
                                'bigBed': f['accession']
                            })
                            new_files.append(f)
        item['files'] = new_files
        if len(item['files']) > 0:
            new_results.append(item)
    return new_results


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
        chromosome = 'chr' + data['seq_region_name']
        start = data['start']
        end = data['end']
        return(chromosome, start, end)


def get_rsid_coordinates(id):
    url = '{ensembl}variation/human/{id}?content-type=application/json'.format(
        ensembl=_ENSEMBL_URL,
        id=id
    )
    try:
        new_response = requests.get(url).json()
    except:
        return('', '', '')
    else:
        if not len(new_response['mappings']):
            return('', '', '')
        for mapping in new_response['mappings']:
            if mapping['assembly_name'] == 'GRCh38':
                location = mapping['location']
        return assembly_mapper(location, 'human', 'GRCh38', 'GRCh37')


def get_ensemblid_coordinates(id):
    url = '{ensembl}lookup/id/{id}?content-type=application/json'.format(
        ensembl=_ENSEMBL_URL,
        id=id
    )
    try:
        response = requests.get(url).json()
    except:
        return('', '', '')
    else:
        if response['assembly_name'] == 'GRCh38':
            location = '{chr}:{start}-{end}'.format(
                chr=response['seq_region_name'],
                start=response['start'],
                end=response['end']
            )
        else:
            return('', '', '')
        return assembly_mapper(location, 'human', 'GRCh38', 'GRCh37')


@view_config(route_name='region-search', request_method='GET', permission='search')
def region_search(context, request):
    """
    Search files by region.
    """
    result = {
        '@id': '/region-search/' + ('?' + request.query_string if request.query_string else ''),
        '@type': ['region-search'],
        'title': 'Search by region',
        'facets': [],
        '@graph': [],
        'columns': OrderedDict(),
        'notification': '',
        'filters': []
    }
    principals = effective_principals(request)
    es = request.registry[ELASTIC_SEARCH]
    term = request.params.get('region', '*')
    if term == '':
        term = '*'
    annotation = request.params.get('annotation', '*')
    assembly = request.params.get('assembly', 'hg19')
    if term != '*' and assembly != '*':
        if len(term.split(':')) < 2:
            term = term.lower()
            if term.startswith('rs'):
                chromosome, start, end = get_rsid_coordinates(term)
            elif term.startswith('ens'):
                chromosome, start, end = get_ensemblid_coordinates(term)
            elif annotation != '*':
                chromosome, start, end = get_annotation_coordinates(es, annotation)
            else:
                result['notification'] = 'Please enter valid coordinates or select annotation'
                return result
        else:
            chromosome, start, end = sanitize_coordinates(term)
    elif annotation != '*':
        chromosome, start, end = get_annotation_coordinates(es, annotation)
    else:
        result['notification'] = 'Please enter valid coordinates'
        return result

    # Check if there are valid coordinates
    if chromosome == '' or start == '' or end == '':
        result['notification'] = 'No annotations found'
        return result
    else:
        result['region'] = '{chr}:{start}-{end}'.format(
            chr=chromosome, start=start, end=end
        )

    # Search for peaks for the coordinates we got
    try:
        peak_results = es.search(body=get_peak_query(start, end),
                                 index=chromosome,
                                 doc_type=assembly,
                                 size=99999)
    except Exception:
        result['notification'] = 'Please enter valid coordinates'
        return result
    file_uuids = []
    for hit in peak_results['hits']['hits']:
        if hit['_id']not in file_uuids:
            file_uuids.append(hit['_id'])
    file_uuids = list(set(file_uuids))
    result_fields = load_columns(request, ['experiment'], result)
    result_fields = result_fields.union(_REGION_FIELDS)
    result['notification'] = 'No results found'

    # if more than one peak found return the experiments with those peak files
    if len(file_uuids):
        query = get_filtered_query('', [], result_fields, principals)
        del query['query']
        query['filter']['and']['filters'].append({
            'terms': {
                'embedded.files.uuid': file_uuids
            }
        })
        used_filters = set_filters(request, query, result)
        used_filters['files.uuid'] = file_uuids
        set_facets(_FACETS, used_filters, query, principals)
        es_results = es.search(
            body=query, index='encoded', doc_type='experiment', size=10
        )
        load_results(request, es_results, result)
        load_facets(es_results, _FACETS, result)
        if len(result['@graph']):
            new_results = get_derived_files(result['@graph'], file_uuids)
            if len(new_results) > 0:
                result['total'] = len(new_results)
                result['notification'] = 'Success'
            result['@graph'] = new_results
    return result


@view_config(route_name='suggest', request_method='GET', permission='search')
def suggest(context, request):
    text = ''
    result = {
        '@id': '/suggest/' + ('?q=' + text),
        '@type': ['suggest'],
        'title': 'Suggest',
        '@graph': [],
    }
    if 'q' in request.params:
        text = request.params.get('q', '')
    else:
        return []
    es = request.registry[ELASTIC_SEARCH]
    query = {
        "suggester": {
            "text": text,
            "completion": {
                "field": "name_suggest",
                "size": 10
            }
        }
    }
    try:
        results = es.suggest(index='annotations', body=query)
    except:
        return {}
    else:
        result['@id'] = '/suggest/' + ('?q=' + text)
        result['@graph'] = results['suggester'][0]['options']
        return result
