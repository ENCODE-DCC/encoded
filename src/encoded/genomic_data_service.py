import random
import requests

from elasticsearch import Elasticsearch
from encoded.searches.interfaces import RNA_CLIENT
from snovault.elasticsearch import PyramidJSONSerializer
from snovault.elasticsearch import TimedUrllib3HttpConnection
from snovault.json_renderer import json_renderer


def includeme(config):
    rna_host = config.registry.settings.get(
        'rna_expression_elasticsearch_server'
    )
    config.registry[RNA_CLIENT] =  Elasticsearch(
        rna_host,
        serializer=PyramidJSONSerializer(json_renderer),
        connection_class=TimedUrllib3HttpConnection,
        timeout=200,
        retry_on_timeout=True,
    )


REGISTRY_DATA_SERVICE = 'genomic_data_service'
RNA_GET_FACETS = [
    'assayType',
    'biosample_classification',
    'biosample_term_name',
    'biosample_organ',
    'biosample_system',
    'biosample_sex',
    'annotation',
]
RNA_GET_EXPRESSIONS = '/expressions/bytes'
RNA_GET_AUTOCOMPLETE = '/autocomplete'
REGION_SEARCH = '/region-search'

# react component orders columns by "the position" in the hash map
RNA_GET_COLUMNS = {
    'featureID': {'title': 'Feature ID'},
    'gene_symbol': {'title': 'Gene'},
    'tpm': {'title': 'Counts (TPM)'},
    'fpkm': {'title': 'Counts (FPKM)'},
    'assayType': {'title': 'Assay (RNA SubType)'},
    'biosample_term_name': {'title': 'Biosample term name'},
    'libraryPrepProtocol': {'title': 'Experiment'},
    'expressionID': {'title': 'File'},
    'annotation': {'title': 'Assembly'},
    'biosample_classification': {'title': 'Biosample classification'},
    'biosample_sex': {'title': 'Sex'},
    'biosample_organ': {'title': 'Organ'},
    'biosample_system': {'title': 'System'},
    'biosample_summary': {'title': 'Summary'}
}


FACET_TERM_MAP = {
    'GRCh38': 'Homo sapiens',
    'mm10': 'Mus musculus',
}


REVERSE_FACET_TERM_MAP = {
    'Homo sapiens': 'GRCh38',
    'Mus musculus': 'mm10',
}


FACET_TITLE_MAP = {
    'Assembly': 'Organism',
}


FACET_FIELD_MAP = {
    'annotation': 'organism',
}


REVERSE_FACET_FIELD_MAP = {
    'organism': 'annotation'
}


GENES = [
    'REM1',
    'APOE',
    'POMC',
    'BRCA1',
    'EP300',
    'IL6, TP53, AKT1'
]


def get_filtered_and_sorted_facets(facets):
    return sorted(
        (
            facet
            for facet in facets
            if facet in RNA_GET_FACETS
        ),
        key=lambda facet: RNA_GET_FACETS.index(facet)
    )


def get_random_gene():
    return random.choice(GENES)


# Aliasing e.g. `annotation=GRCh38` as `organism=Homo+sapiens`.
def map_encoded_param_to_data_service_param(key, value):
    key = REVERSE_FACET_FIELD_MAP.get(key, key)
    value = REVERSE_FACET_TERM_MAP.get(value, value)
    return f'{key}={value}'


class GenomicDataService():
    # default search value is a temporary feature for the current alpha UI client
    def __init__(self, registry, request):
        self.path = registry.settings.get(REGISTRY_DATA_SERVICE)
        self.request = request

        self.parse_params()


    def parse_params(self):
        params = self.request.params

        self.genes   = params.get('genes') or get_random_gene()
        self.units   = params.get('units', 'tpm')
        self.page    = params.get('page', 1)
        self.sort    = params.get('sort', f'-{self.units}')
        self.columns = RNA_GET_COLUMNS.copy()
        self.columns.pop('tpm' if self.units == 'fpkm' else 'fpkm')
        self.autocomplete_query = params.get('q', '')

        if self.sort:
            desc = self.sort[0] == '-'
            self.sort_by = self.sort[1:] if desc else self.sort
            self.sort_order = 'desc' if desc else 'asc'

        self.filter_params = {}
        for facet in RNA_GET_FACETS:
            normalized_facet = FACET_FIELD_MAP.get(facet, facet)
            param_value = params.get(normalized_facet)
            if param_value:
                self.filter_params[normalized_facet] = param_value

        self.filters = [{'field': 'type', 'term': 'Rna Get', 'remove': '/rnaget'}]

        for filter_ in self.filter_params:
            query_string = []

            # exclude filter from original query string
            for param in params:
                if param != filter_:
                    query_string.append(f'{param}={params.get(param)}')

            self.filters.append({
                'field': filter_,
                'term': self.filter_params[filter_],
                'remove': f'{self.request.path}?{"&".join(query_string)}'
            })


    def rna_get_request_query_string(self, format_='json'):
        params = [f'format={format_}']
        search = ','.join(
            [
                gene.strip()
                for gene in self.genes.split(',')
            ]
        )
        params.append(f'featureIDList={search}')

        if self.units:
            params.append(f'units={self.units}')

        if self.sort:
            params.append(f'sort={self.sort}')

        if self.page:
            params.append(f'page={self.page}')

        for key, value in self.filter_params.items():
            params.append(
                map_encoded_param_to_data_service_param(
                    key,
                    value
                )
            )

        return '&'.join(params)


    def rna_get_request(self, endpoint=RNA_GET_EXPRESSIONS, format_='json'):
        url = f'{self.path}{endpoint}?{self.rna_get_request_query_string(format_)}'

        results = requests.get(url, timeout=3).json()

        self.expressions = results['expressions']
        self.total = results['total']
        self.facets = []
        for facet in get_filtered_and_sorted_facets(results['facets'].keys()):
            title = self.columns[facet]['title']
            facet_data = {
                'field': FACET_FIELD_MAP.get(facet, facet),
                'title': FACET_TITLE_MAP.get(title, title),
                'terms': [
                    {
                        'key': FACET_TERM_MAP.get(term[0], term[0]),
                        'doc_count': term[1],
                    }
                    for term in results['facets'][facet]
                ],
                'type': 'terms'
            }
            facet_data['total'] = sum([term['doc_count'] for term in facet_data['terms']])
            self.facets.append(facet_data)

        # this forces the current components to show an empty state
        if self.total == 0:
            for facet in self.facets:
                facet['total'] += 1


    def rna_get_autocomplete(self):
        suggestions = []

        if self.autocomplete_query:
            try:
                url = f'{self.path}{RNA_GET_AUTOCOMPLETE}?gene={self.autocomplete_query}'

                results = requests.get(url, timeout=3).json()

                if 'genes' in results:
                    suggestions = [{'text': result} for result in results['genes']]
            except:
                pass

        return {
            '@graph': suggestions,
            '@type': ['suggest'],
            '@id': f'/rnaget-autocomplete?q={self.autocomplete_query}',
            'title': 'Suggest'
        }


    def rna_get(self):
        self.rna_get_request()

        for expression in self.expressions:
            expression['featureID'] += f"/{expression['encodeID'].split('/')[-2]}"

            for key in expression:
                if expression[key] == None:
                    expression[key] = ''

                if key == 'analysis' and expression[key]:
                    expression[key] = expression[key][1:-1]

                if key == 'libraryPrepProtocol' and expression[key]:
                    expression[key] = expression[key].split('/')[-1]

        response = {
            'title': 'RNA Get',
            '@type': ['rnaseq'],
            '@id': self.request.path_qs,
            'total': self.total,
            'non_sortable': ['annotation'],
            'columns': self.columns,
            'filters': self.filters,
            'facets': self.facets,
            '@graph': self.expressions,
            'selected_genes': self.genes,
        }

        if self.sort:
            response['sort'] = {}
            response['sort'][self.sort_by] = {
                'order': self.sort_order,
                'unmapped_type': 'keyword'
            }

        return response


    def region_search(self, assembly, chromosome, start, end):
        params = {
            'assembly': assembly,
            'chr': chromosome.replace('chr', ''),
            'start': start,
            'end': end,
            'files_only': True
        }

        query_params = '&'.join([f'{k}={params[k]}' for k in params.keys()])

        url = f'{self.path}{REGION_SEARCH}?{query_params}'

        results = requests.get(url, timeout=3).json()

        return results
