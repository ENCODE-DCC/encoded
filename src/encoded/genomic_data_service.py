import requests

REGISTRY_DATA_SERVICE = 'genomic_data_service'
RNA_GET_FACETS = ['assayType', 'annotation', 'biosample_term_name', 'biosample_classification', 'biosample_sex', 'biosample_organ',  'biosample_system']
RNA_GET_EXPRESSIONS = '/expressions/bytes'
RNA_GET_AUTOCOMPLETE = '/autocomplete'

# react component orders columns by "the position" in the hash map
RNA_GET_COLUMNS = {
    'featureID': {'title': 'Feature ID'},
    'tpm': {'title': 'Counts (TPM)'},
    'fpkm': {'title': 'Counts (FPKM)'},
    'assayType': {'title': 'Assay (RNA SubType)'},
    'libraryPrepProtocol': {'title': 'Experiment'},
    'expressionID': {'title': 'File'},
    'annotation': {'title': 'Annotation'},
    'biosample_term_name': {'title': 'Biosample'},
    'biosample_classification': {'title': 'Classification'},
    'biosample_sex': {'title': 'Sex'},
    'biosample_organ': {'title': 'Organ'},
    'biosample_system': {'title': 'System'},
    'biosample_summary': {'title': 'Summary'}
}

class GenomicDataService():
    # default search value is a temporary feature for the current alpha UI client
    def __init__(self, registry, request, default_search='ENSG00000088320.3'):
        self.path = registry.settings.get(REGISTRY_DATA_SERVICE)
        self.request = request
        self.default_search = default_search

        self.parse_params()


    def parse_params(self):
        params = self.request.params

        self.genes   = params.get('genes')
        self.units   = params.get('units', 'tpm')
        self.page    = params.get('page', 1)
        self.sort    = params.get('sort')
        self.columns = RNA_GET_COLUMNS.copy()
        self.columns.pop('tpm' if self.units == 'fpkm' else 'fpkm')
        self.autocomplete_query = params.get('q', '')

        if self.sort:
            desc = self.sort[0] == '-'
            self.sort_by = self.sort[1:] if desc else self.sort
            self.sort_order = 'desc' if desc else 'asc'

        self.filter_params = {}
        for facet in RNA_GET_FACETS:
            if params.get(facet):
                self.filter_params[facet] = params.get(facet)

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

        search = self.default_search
        if self.genes:
            search = ','.join([gene.strip() for gene in self.genes.split(',')])

        params.append(f'featureIDList={search}')

        if self.units:
            params.append(f'units={self.units}')

        if self.sort:
            params.append(f'sort={self.sort}')

        if self.page:
            params.append(f'page={self.page}')

        for filter_ in self.filter_params:
            params.append(f'{filter_}={self.filter_params.get(filter_)}')

        return '&'.join(params)


    def rna_get_request(self, endpoint=RNA_GET_EXPRESSIONS, format_='json'):
        url = f'{self.path}{endpoint}?{self.rna_get_request_query_string(format_)}'

        results = requests.get(url, timeout=3).json()

        self.expressions = results['expressions']
        self.total = results['total']
        self.facets = []

        for facet in results['facets']:
            facet_data = {
                'field': facet,
                'title': self.columns[facet]['title'],
                'terms': [{'key': term[0], 'doc_count': term[1]} for term in results['facets'][facet]],
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
            '@graph': self.expressions
        }

        if self.sort:
            response['sort'] = {}
            response['sort'][self.sort_by] = {
                'order': self.sort_order,
                'unmapped_type': 'keyword'
            }

        return response
