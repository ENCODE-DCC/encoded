from encoded.viewconfigs.matrix import MatrixView
from urllib.parse import urlencode
from snovault.helpers.helper import format_facets


class SummaryView(MatrixView):
    def __init__(self, context, request):
        super(SummaryView, self).__init__(context, request)
        self.result['matrix'] = ''
        self.matrix = ''
        self.no_audits_groupings = ['no.audit.error', 'no.audit.not_compliant', 'no.audit.warning']

    def preprocess_view(self):
        self.result['@id'] = self.request.route_path('summary', slash='/') + self.search_base
        self.result['@type'] = ['Summary']
        self.result['notification'] = ''
        self.type_info = self.types[self.doc_types[0]]
        self.schema = self.type_info.schema

        self.validate_items()

        self.type_info = self.types[self.doc_types[0]]
        self.schema = self.type_info.schema
        self.result['title'] = self.type_info.name + ' Summary'
        self.result['summary'] = self.type_info.factory.summary_data.copy()

        self.summary = self.result['summary']
        self.summary['search_base'] = self.request.route_path('search', slash='/') + self.search_base
        self.summary['clear_summary'] = self.request.route_path('summary', slash='/') + '?type=' + self.doc_types[0]

        self.result['views'] = self.construct_result_views(summary=True)

        clear_qs = urlencode([("type", typ) for typ in self.doc_types])
        self.result['clear_filters'] = self.request.route_path('summary', slash='/') + (('?' + clear_qs) if clear_qs else '')

        # Construct query
        query = self.construct_query(self.summary, 'summary')

        # Query elastic search
        es_results = self.query_elastic_search(query, self.es_index)
        aggregations = es_results['aggregations']
        self.result['summary']['doc_count'] = total = aggregations['summary']['doc_count']
        self.result['summary']['max_cell_doc_count'] = 0
        summary_groupings = self.summary['grouping']
        self.result['summary'][summary_groupings[0]] = es_results['aggregations']['summary']

        # Format facets for results
        self.result['facets'] = format_facets(es_results,
                                              self.facets,
                                              self.used_filters,
                                              (self.schema,),
                                              total,
                                              self.principals)
        return self.result
