"""
# Summary View
Some Desc

## Inheritance
SummaryView<-MatrixView<-BaseView

### MatrixView function dependecies
- validate_items
"""
from urllib.parse import urlencode

from encoded.viewconfigs.matrix import MatrixView

from snovault.helpers.helper import (  # pylint: disable=import-error
    get_filtered_query,
    get_search_fields,
    set_facets,
    set_filters,
)


class SummaryView(MatrixView):
    '''SummaryView'''
    def __init__(self, context, request):
        super(SummaryView, self).__init__(context, request)
        self._facets = []
        self._summary = None

    def _construct_query(self):
        '''Helper method for preprocessing view'''
        search_fields, _ = get_search_fields(self.request, self.doc_types)
        query = get_filtered_query(
            self.search_term,
            search_fields,
            [],
            self.principals,
            self.doc_types
        )
        if self.search_term == '*':
            del query['query']['query_string']
        else:
            query['query']['query_string']['fields'].extend(
                ['_all', '*.uuid', '*.md5sum', '*.submitted_file_name']
            )
        self._set_query_aggs(query)
        query['size'] = 0
        return query

    def _construct_xygroupings(
            self,
            query,
            filters,
        ):
        '''Helper Method for constructing query'''
        x_grouping = self.summary['x']['group_by']
        y_groupings = self.summary['y']['group_by']
        summary_groupings = self.summary['grouping']
        x_agg = {
            "terms": {
                "field": 'embedded.' + x_grouping,
                "size": 999999,
            },
        }
        aggs = {x_grouping: x_agg}
        for field in reversed(y_groupings):
            aggs = {
                field: {
                    "terms": {
                        "field": 'embedded.' + field,
                        "size": 999999,
                    },
                    "aggs": aggs,
                },
            }
        summary_aggs = None
        for field in reversed(summary_groupings):
            sub_summary_aggs = summary_aggs
            summary_aggs = {
                field: {
                    "terms": {
                        "field": 'embedded.' + field,
                        "size": 999999,
                    },
                },
            }
            if sub_summary_aggs:
                summary_aggs[field]['aggs'] = sub_summary_aggs
        aggs['x'] = x_agg
        query['aggs']['summary'] = {
            "filter": {
                "bool": {
                    "must": filters,
                }
            },
            "aggs": summary_aggs,
        }

    def _set_query_aggs(self, query):
        '''Helper Method for constructing query'''
        query_filters = query['post_filter'].pop('bool')
        filter_collector = {'post_filter': {'bool': query_filters}}
        used_filters = set_filters(
            self.request,
            filter_collector,
            self.result,
        )
        filters = filter_collector['post_filter']['bool']['must']
        self._facets = [
            (field, facet)
            for field, facet in self.schema['facets'].items()
            if (
                field in self.summary['x']['facets'] or
                field in self.summary['y']['facets']
            )
        ]
        query['aggs'] = set_facets(self._facets, used_filters, self.principals, self.doc_types)
        self._construct_xygroupings(query, filters)

    def preprocess_view(self):
        '''
        Main function to construct query and build view results json
        * Only publicly accessible function
        '''
        self.result['@id'] = self.request.route_path('summary', slash='/') + self.search_base
        self.result['@type'] = ['Summary']
        self.result['notification'] = ''
        type_info = self.types[self.doc_types[0]]
        schema = type_info.schema
        self.validate_items(type_info)
        self.result['title'] = type_info.name + ' Summary'
        self.result['summary'] = type_info.factory.summary_data.copy()
        self._summary = self.result['summary']
        search_base = self.request.route_path('search', slash='/') + self.search_base
        self._summary['search_base'] = search_base
        clear_summary = self.request.route_path('summary', slash='/') + '?type=' + self.doc_types[0]
        self.summary['clear_summary'] = clear_summary
        self.result['views'] = [
            self.view_item.result_list,
            self.view_item.tabular_report,
            self.view_item.summary_matrix
        ]
        clear_qs = urlencode([("type", typ) for typ in self.doc_types])
        summary_route = self.request.route_path('summary', slash='/')
        self.result['clear_filters'] = summary_route + (('?' + clear_qs) if clear_qs else '')
        query = self._construct_query()

        es_results = self.elastic_search.search(body=query, index=self.es_index)
        aggregations = es_results['aggregations']
        total = aggregations['summary']['doc_count']
        self.result['summary']['doc_count'] = total
        self.result['summary']['max_cell_doc_count'] = 0
        summary_groupings = self.summary['grouping']
        self.result['summary'][summary_groupings[0]] = es_results['aggregations']['summary']
        self.result['facets'] = self.format_facets(
            es_results,
            self.facets,
            self.used_filters,
            (schema,),
            total,
            self.principals
        )
        return self.result
