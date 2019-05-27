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
    def __init__(
            self,
            context,
            request,
            page_name="matrix",
            hidden_facets=None,
            hidden_facet_terms=None,
            implicit_facet_terms=None,
            hidden_filters=None,
            ):
        super(MatrixView, self).__init__(context, request)
        self._view_item = View_Item(request, self._search_base)
        self._facets = []
        self._schema = None
        self._page_name = page_name
        self._hidden_facets = hidden_facets
        self._hidden_facet_terms = hidden_facet_terms
        self._implicit_facet_terms = implicit_facet_terms
        self._hidden_filters = hidden_filters

    @staticmethod
    def _set_result_title(type_info, page_name='matrix'):
        """Helper function for class and child classes."""
        title = ''.join((type_info.name, ' ', page_name))
        return title

    def _construct_query(self, result_filters, matrix_x_y):
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
        used_filters = self._set_query_aggs(query, result_filters, matrix_x_y)
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

    def _construct_xygroupings(self, query, filters, negative_filters, matrix_x_y):
        '''Helper Method for constructing query'''
        x_grouping = matrix_x_y['x']['group_by']
        y_groupings = matrix_x_y['y']['group_by']
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
        '''Helper function for class and child classes'''
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

    def _set_query_aggs(self, query, result_filters, matrix_x_y):
        '''Helper Method for constructing query'''
        query_filters = query['post_filter'].pop('bool')
        filter_collector = {'post_filter': {'bool': query_filters}}
        used_filters = set_filters(
            self._request,
            filter_collector,
            result_filters,
            filter_exclusion=self._filter_exclusion,
            implicit_facet_terms=self._implicit_facet_terms
        )
        filters = filter_collector['post_filter']['bool']['must']
        negative_filters = filter_collector['post_filter']['bool']['must_not']
        self._facets = [
            (field, facet)
            for field, facet in self._schema['facets'].items()
            if (
                field in matrix_x_y['x']['facets'] or
                field in matrix_x_y['y']['facets']
                )
        ]

        # Display all audits if logged in, or all but INTERNAL_ACTION if logged out
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
        self._construct_xygroupings(query, filters, negative_filters, matrix_x_y)
        return used_filters

    def _summarize_buckets(self, x_buckets, outer_bucket, grouping_fields, matrix):
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
                self._summarize_buckets(x_buckets, bucket, grouping_fields, matrix)

    def _remove_hidden_facet_terms(self, facets):
        """Hide facet terms set to be hidden.

        Arguments:
            facets {Collection} -- Collection of facets
        Returns:
            Collection -- facets without hidden terms

        """
        if not self._hidden_facet_terms or not facets:
            return facets
        for field, terms in self._hidden_facet_terms.items():
            for result in facets:
                if result['field'] == field:
                    index_ = [index_ for index_, term in enumerate(result['terms']) if term['key'] in terms]
                    if index_:
                        del result['terms'][index_[0]]
        return facets

    def _remove_hidden_filters(self, filters):
        """Remove hidden filters.

        Arguments:
            filters {Collection} -- Collectiion of filters

        """
        if not self._hidden_filters or not filters:
            return filters

        hidden_filter_indices = []
        for index_, filter_ in enumerate(filters):
            for field_, term in self._hidden_filters.items():
                if filter_['field'] == field_ and filter_['term'] == term:
                    hidden_filter_indices.append(index_)
        for index_ in hidden_filter_indices[::-1]:
            del filters[index_]
        return filters

    def _remove_hidden_facets(self, facets):
        """
        Remove hidden facets from facet-list.

        Arguments:
            facets {list} -- List of facets

        Returns:
            List -- Facets without hidden facets

        """
        if not self._remove_hidden_facets or not facets or not facet['field'] :
            return facets
        return [facet for facet in facets if facet['field'] not in self._hidden_facets]

    def preprocess_view(self):
        '''
        Main function to construct query and build view results json
        * Only publicly accessible function
        '''
        matrix_route = self._request.route_path(self._view_name, slash='/')
        result_filters = {'filters': []}
        # TODO: Validate doc types in base class in one location
        # Now we do it here and in _validate_items
        type_info = None
        if len(self._doc_types) == 1 and self._doc_types[0] in self._types:
            type_info = self._types[self._doc_types[0]]
            self._schema = type_info.schema
        self._validate_items(type_info)
        matrix = getattr(type_info.factory, self._factory_name).copy()
        matrix['x']['limit'] = self._request.params.get('x.limit', 20)
        matrix['y']['limit'] = self._request.params.get('y.limit', 5)
        search_route = self._request.route_path('search', slash='/')
        matrix['search_base'] = search_route + self._search_base
        matrix['clear_matrix'] = matrix_route + '?type=' + self._doc_types[0]
        matrix_x_y = {
            'x': matrix['x'],
            'y': matrix['y'],
        }
        search_query, used_filters = self._construct_query(
            result_filters,
            matrix_x_y
        )
        es_results = self._elastic_search.search(
            body=search_query,
            index=self._es_index
        )
        aggregations = es_results['aggregations']
        aggregations_total = aggregations['matrix']['doc_count']
        matrix['doc_count'] = aggregations_total
        matrix['max_cell_doc_count'] = 0
        x_grouping = matrix['x']['group_by']
        y_groupings = matrix['y']['group_by']
        matrix['y'][y_groupings[0]] = aggregations['matrix'][y_groupings[0]]
        matrix['x'].update(aggregations['matrix']['x'])
        self._summarize_buckets(
            aggregations['matrix']['x']['buckets'],
            aggregations['matrix'],
            y_groupings + [x_grouping],
            matrix
        )
        facets = self._format_facets(
            es_results,
            self._facets,
            used_filters,
            (self._schema,),
            aggregations_total,
            self._principals
        )
        es_total = es_results['hits']['total']
        notification = 'Success'
        if not es_total:
            self._request.response.status_code = 404
            notification = 'No results found'
        search_result = {
            '@context': self._request.route_path('jsonld_context'),
            'filters': self._remove_hidden_filters(result_filters['filters']),
            '@id': matrix_route + self._search_base,
            '@type': ['Matrix'],
            'title': self._set_result_title(type_info, self._page_name),
            'matrix': matrix,
            'views': self._construct_result_views(type_info),
            'facets': self._remove_hidden_facets(self._remove_hidden_facet_terms(facets)),
            'total': es_total,
            'notification': notification,
        }
        search_result.update(
            search_result_actions(
                self._request,
                self._doc_types,
                es_results
            )
        )
        return search_result
