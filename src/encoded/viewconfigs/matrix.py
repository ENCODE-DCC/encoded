"""
# Matrix View
Some Desc

## Inheritance
MatrixView<-BaseView

### BaseView function dependencies
- _format_facets
"""
from pyramid.httpexceptions import HTTPBadRequest  # pylint: disable=import-error

from encoded.helpers.helper import (
    search_result_actions,
    View_Item)

from snovault.helpers.helper import (  # pylint: disable=import-error
    get_filtered_query,
    get_search_fields,
    set_filters,
    set_facets,
)
from snovault.viewconfigs.base_view import BaseView  # pylint: disable=import-error


class MatrixView(BaseView):  #pylint: disable=too-few-public-methods
    '''Matrix View'''
    _view_name = 'matrix'
    _factory_name = 'matrix'
    _filter_exclusion = [
        'type', 'limit', 'y.limit', 'x.limit', 'mode', 'annotation',
        'format', 'frame', 'datastore', 'field', 'region', 'genome',
        'sort', 'from', 'referrer',
    ]

    def __init__(self, context, request):
        super(MatrixView, self).__init__(context, request)
        self._view_item = View_Item(request, self._search_base)
        self._facets = []
        self._schema = None

    @staticmethod
    def _set_result_title(type_info):
        """Set class and child classes."""
        title = type_info.name + ' matrix'
        return title

    def _construct_query(self, search_result, matrix):
        """Preprocess query."""
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
        used_filters = self._set_query_aggs(query, search_result, matrix)
        return query, used_filters

    def _construct_result_views(self, type_info):
        '''Helper method for preprocessing view'''
        views = [
            self._view_item.result_list,
            self._view_item.tabular_report
        ]
        if hasattr(type_info.factory, 'summary_data'):
            views.append(self._view_item.summary_report)
        return views

    def _construct_xygroupings(self, query, filters, negative_filters, matrix):
        """Construct xy group."""
        x_grouping = matrix['x']['group_by']
        y_groupings = matrix['y']['group_by']
        x_agg = {
            "terms": {
                "field": 'embedded.' + x_grouping,
                "size": 999999,  # no limit
            },
        }
        aggs = {x_grouping: x_agg}
        for field in reversed(y_groupings):
            aggs = {
                field: {
                    "terms": {
                        "field": 'embedded.' + field,
                        "size": 999999,  # no limit
                    },
                    "aggs": aggs,
                },
            }
        aggs['x'] = x_agg
        query['aggs']['matrix'] = {
            "filter": {
                "bool": {
                    "must": filters,
                    "must_not": negative_filters
                }
            },
            "aggs": aggs,
        }

    def _validate_items(self, type_info):
        """Validate items."""
        msg = None
        if len(self._doc_types) != 1:
            msg = (
                'Search result {} currently requires specifying a '
                'single type.'.format(
                    self._view_name,
                )
            )
        elif self._doc_types[0] not in self._types:
            msg = 'Invalid type: {}'.format(self._doc_types[0])
        elif not hasattr(type_info.factory, self._factory_name):
            msg = 'No {} configured for type: {}'.format(
                self._factory_name,
                self._doc_types[0],
            )
        if msg:
            raise HTTPBadRequest(explanation=msg)

    def _set_query_aggs(self, query, search_result, matrix):
        """Construct facets of search query."""
        query_filters = query['post_filter'].pop('bool')
        filter_collector = {'post_filter': {'bool': query_filters}}
        used_filters = set_filters(
            self._request,
            filter_collector,
            search_result,
            filter_exclusion=self._filter_exclusion
        )
        filters = filter_collector['post_filter']['bool']['must']
        negative_filters = filter_collector['post_filter']['bool']['must_not']
        self._facets = [
            (field, facet)
            for field, facet in self._schema['facets'].items()
            if (
                field in matrix['x']['facets'] or
                field in matrix['y']['facets']
                )
        ]
        # Show all audits if logged in or all but INTERNAL_ACTION if logged out
        for audit_facet in self._audit_facets:
            if (
                    self._search_audit and
                    'group.submitter' in self._principals or
                    'INTERNAL_ACTION' not in audit_facet[0]
            ):
                self._facets.append(audit_facet)
        query['aggs'] = set_facets(
            self._facets,
            used_filters,
            self._principals,
            self._doc_types
        )
        self._construct_xygroupings(query, filters, negative_filters, matrix)
        return used_filters

    def _summarize_buckets(
            self,
            x_buckets,
            outer_bucket,
            grouping_fields,
            matrix
    ):
        """
        Set bucket summary.

            :param x_buckets: x buckets
            :param outer_bucket: Outer bucket
            :param grouping_fields: Grouping fields
            :param matrix: Matrix
        """
        group_by = grouping_fields[0]
        grouping_fields = grouping_fields[1:]
        if not grouping_fields:
            counts = {}
            for bucket in outer_bucket[group_by]['buckets']:
                doc_count = bucket['doc_count']
                if doc_count > matrix['max_cell_doc_count']:
                    matrix['max_cell_doc_count'] = doc_count
                counts[bucket['key']] = doc_count
            summary = []
            for bucket in x_buckets:
                summary.append(counts.get(bucket['key'], 0))
            outer_bucket[group_by] = summary
        else:
            for bucket in outer_bucket[group_by]['buckets']:
                self._summarize_buckets(
                    x_buckets,
                    bucket,
                    grouping_fields,
                    matrix
                )

    def preprocess_view(self):
        """Construct query and build view search result json."""
        matrix_route = self._request.route_path('matrix', slash='/')
        search_result = {}
        search_result['@context'] = self._request.route_path('jsonld_context')
        search_result['filters'] = []
        search_result['@id'] = matrix_route + self._search_base
        search_result['@type'] = ['Matrix']
        search_result['notification'] = ''
        # TODO: Validate doc types in base class in one location
        # Now we do it here and in _validate_items
        type_info = None
        if len(self._doc_types) == 1:
            if self._doc_types[0] in self._types:
                type_info = self._types[self._doc_types[0]]
                self._schema = type_info.schema
        self._validate_items(type_info)
        search_result['title'] = self._set_result_title(type_info)
        search_result['matrix'] = type_info.factory.matrix.copy()
        matrix = {}
        matrix = search_result['matrix']
        matrix['x']['limit'] = self._request.params.get('x.limit', 20)
        matrix['y']['limit'] = self._request.params.get('y.limit', 5)
        search_route = self._request.route_path('search', slash='/')
        matrix['search_base'] = search_route + self._search_base
        matrix['clear_matrix'] = matrix_route + '?type=' + self._doc_types[0]
        search_result['views'] = self._construct_result_views(type_info)
        query, used_filters = self._construct_query(search_result, matrix)
        es_results = self._elastic_search.search(
            body=query,
            index=self._es_index
        )
        aggregations = es_results['aggregations']
        total = aggregations['matrix']['doc_count']
        search_result['matrix']['doc_count'] = total
        search_result['matrix']['max_cell_doc_count'] = 0
        search_result['facets'] = self._format_facets(
            es_results,
            self._facets,
            used_filters,
            (self._schema,),
            total,
            self._principals
        )
        x_grouping = matrix['x']['group_by']
        y_groupings = matrix['y']['group_by']
        self._summarize_buckets(
            aggregations['matrix']['x']['buckets'],
            aggregations['matrix'],
            y_groupings + [x_grouping],
            matrix
        )
        search_result['matrix']['y'][y_groupings[0]] = aggregations['matrix'][y_groupings[0]]
        search_result['matrix']['x'].update(aggregations['matrix']['x'])
        search_result.update(
            search_result_actions(
                self._request,
                self._doc_types,
                es_results
            )
        )
        search_result['total'] = es_results['hits']['total']
        if search_result['total']:
            search_result['notification'] = 'Success'
        else:
            self._request.response.status_code = 404
            search_result['notification'] = 'No results found'
        return search_result
