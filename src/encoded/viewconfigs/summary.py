"""
# Summary View
Some Desc

## Inheritance
SummaryView<-MatrixView<-BaseView

### MatrixView function dependencies
- validate_items
### BaseView function dependencies
- _format_facets
"""
from urllib.parse import urlencode

from encoded.viewconfigs.matrix import MatrixView

from snovault.helpers.helper import (  # pylint: disable=import-error
    get_filtered_query,
    get_search_fields,
    set_facets,
    set_filters,
)


class SummaryView(MatrixView):  #pylint: disable=too-few-public-methods
    '''Summary View'''
    _view_name = 'summary'
    _factory_name = 'summary_data'
    def __init__(self, context, request):
        super(SummaryView, self).__init__(context, request)

    def _construct_query(self, search_result, summary):
        '''Helper method for preprocessing view'''
        search_fields, _ = get_search_fields(self._request, self._doc_types)
        query = get_filtered_query(
            self._search_term,
            search_fields,
            [],
            self._principals,
            self._doc_types
        )
        if self._search_term == '*':
            del query['query']['query_string']
        else:
            query['query']['query_string']['fields'].extend(
                ['_all', '*.uuid', '*.md5sum', '*.submitted_file_name']
            )
        used_filters = self._set_query_aggs(query, search_result, summary)
        query['size'] = 0
        return query, used_filters

    def _construct_xygroupings(
            self,
            query,
            filters,
            summary,
    ):
        """Construct xy groupings."""
        # pylint: disable=arguments-differ
        x_grouping = summary['x']['group_by']
        y_groupings = summary['y']['group_by']
        summary_groupings = summary['grouping']
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

    def _set_query_aggs(self, query, search_result, summary):
        '''Helper Method for constructing query'''
        query_filters = query['post_filter'].pop('bool')
        filter_collector = {'post_filter': {'bool': query_filters}}
        used_filters = set_filters(
            self._request,
            filter_collector,
            search_result,
        )
        filters = filter_collector['post_filter']['bool']['must']
        self._facets = [
            (field, facet)
            for field, facet in self._schema['facets'].items()
            if (
                field in summary['x']['facets'] or
                field in summary['y']['facets']
            )
        ]
        query['aggs'] = set_facets(
            self._facets,
            used_filters,
            self._principals,
            self._doc_types
        )
        self._construct_xygroupings(query, filters, summary)
        return used_filters

    def preprocess_view(self):
        """Construct query and build view results json."""
        # TODO: Validate doc types in base class in one location
        # Now we do it here and in _validate_items
        type_info = None
        if len(self._doc_types) == 1:
            if self._doc_types[0] in self._types:
                type_info = self._types[self._doc_types[0]]
                self._schema = type_info.schema
        self._validate_items(type_info)
        summary_route = self._request.route_path('summary', slash='/')
        summary = type_info.factory.summary_data.copy()
        search_result = {
            '@context': self._request.route_path('jsonld_context'),
            'filters': [],
            '@id': summary_route + self._search_base,
            '@type': ['Summary'],
            'notification': '',
            'title': type_info.name + ' summary',
            'summary': summary,
        }
        search_route = self._request.route_path('search', slash='/')
        summary['search_base'] = search_route + self._search_base
        clear_summary = summary_route + '?type=' + self._doc_types[0]
        summary['clear_summary'] = clear_summary
        search_result['views'] = [
            self._view_item.result_list,
            self._view_item.tabular_report,
            self._view_item.summary_matrix
        ]
        clear_qs = urlencode([("type", typ) for typ in self._doc_types])
        summary_route = self._request.route_path('summary', slash='/')
        clear_qs_str = ('?' + clear_qs) if clear_qs else ''
        search_result['clear_filters'] = summary_route + clear_qs_str
        query, used_filters = self._construct_query(search_result, summary)
        es_results = self._elastic_search.search(
            body=query,
            index=self._es_index
        )
        total = es_results['aggregations']['summary']['doc_count']
        search_result['summary']['doc_count'] = total
        search_result['summary']['max_cell_doc_count'] = 0
        summary_groupings = summary['grouping']
        search_result['summary'][summary_groupings[0]] = es_results['aggregations']['summary']
        search_result['facets'] = self._format_facets(
            es_results,
            self._facets,
            used_filters,
            (self._schema,),
            total,
            self._principals
        )
        return search_result
