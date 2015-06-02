from pyramid.view import view_config
from contentbase.elasticsearch import ELASTIC_SEARCH
from pyramid.security import effective_principals
from .search import (
    load_columns,
    load_results
)
from collections import OrderedDict

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


def includeme(config):
    config.add_route('region-search', '/region-search{slash:/?}')
    config.add_route('suggest', '/suggest{slash:/?}')
    config.scan(__name__)


def get_filtered_query(principals, file_uuids, result_fields):
    return {
        'query': {
            'filtered': {
                'filter': {
                    'and': {
                        'filters': [
                            {
                                'terms': {
                                    'principals_allowed.view': principals
                                }
                            },
                            {
                                'terms': {
                                    'embedded.files.uuid': file_uuids
                                }
                            }
                        ]
                    }
                }
            }
        },
        '_source': list(result_fields),
    }


def get_peak_query(start, end):
    """
    return peak query
    """
    return {
        'query': {
            'filtered': {
                'filter': {
                    'and': {
                        'filters': [
                            {
                                'range': {
                                    'start': {
                                        'lte': end,
                                    }
                                }
                            },
                            {
                                'range': {
                                    'end': {
                                        'gte': start,
                                    }
                                }
                            }
                        ],
                        '_cache': True
                    }
                }
            }
        },
        'fields': ['uuid']
    }


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
    }
    principals = effective_principals(request)
    es = request.registry[ELASTIC_SEARCH]
    term = request.params.get('region', '*')
    annotation = request.params.get('annotation', '*')
    assembly = request.params.get('assembly', '*')
    if assembly == '*':
        assembly = 'hg19'
    if term != '*' and assembly != '*':
        terms = term.split(':')
        chromosome = terms[0]
        positions = terms[1].split('-')
        if len(positions) > 0 and len(positions) == 1:
            start = end = positions[0]
        elif len(positions) == 2:
            start = positions[0]
            end = positions[1]
        try:
            peak_results = es.search(body=get_peak_query(start, end), index=chromosome,
                                     doc_type=assembly, size=99999)
        except:
            result['notification'] = 'Please enter valid coordinates'
            return result
        file_uuids = []
        for hit in peak_results['hits']['hits']:
            if hit['fields']['uuid'] not in file_uuids:
                file_uuids.append(hit['fields']['uuid'][0])
        file_uuids = list(set(file_uuids))
        result_fields = load_columns(request, ['experiment'], result)
        result_fields = result_fields.union(_REGION_FIELDS)
        es_results = es.search(
            body=get_filtered_query(principals, file_uuids, result_fields),
            index='encoded', doc_type='experiment', size=25
        )
        load_results(request, es_results, result)
        result['notification'] = 'No results found'
        if len(result['@graph']):
            new_results = []
            result['total'] = es_results['hits']['total']
            result['notification'] = 'Success'
            for item in result['@graph']:
                item['highlight'] = []
                new_files = []
                for f in item['files']:
                    if f['derived_from']['uuid'] in file_uuids:
                        new_files.append(f)
                        item['highlight'].append(f['derived_from']['uuid'])
                item['files'] = new_files
                if len(item['files']):
                    new_results.append(item)
            result['@graph'] = new_results
    elif annotation != '*':
        # got to handle gene names, IDs and other annotations here
        result['notification'] = 'Annotations are not yet handled'
    else:
        result['notification'] = 'Please enter valid coordinates'
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
