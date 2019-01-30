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
import time
import logging

logging.basicConfig(filename='search_test_1.log', level=logging.DEBUG)

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
        if self._view_name == 'matrix':  # hack
            self._result['matrix'] = ''
            self._matrix = ''
        self._view_item = View_Item(request, self._search_base)
        self._facets = []
        self._schema = None
        

    @staticmethod
    def _set_result_title(type_info):
        '''Helper function for class and child classes'''
        title = type_info.name + ' matrix'
        return title

    def _construct_query(self):
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
        used_filters = self._set_query_aggs(query)
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

    def _construct_xygroupings(self, query, filters, negative_filters):
        '''Helper Method for constructing query'''
        x_grouping = self._matrix['x']['group_by']
        y_groupings = self._matrix['y']['group_by']
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

    def _set_query_aggs(self, query):
        '''Helper Method for constructing query'''
        query_filters = query['post_filter'].pop('bool')
        filter_collector = {'post_filter': {'bool': query_filters}}
        used_filters = set_filters(
            self._request,
            filter_collector,
            self._result,
            filter_exclusion=self._filter_exclusion
        )
        filters = filter_collector['post_filter']['bool']['must']
        negative_filters = filter_collector['post_filter']['bool']['must_not']
        self._facets = [
            (field, facet)
            for field, facet in self._schema['facets'].items()
            if (
                field in self._matrix['x']['facets'] or
                field in self._matrix['y']['facets']
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
        self._construct_xygroupings(query, filters, negative_filters)
        return used_filters

    def _summarize_buckets(self, x_buckets, outer_bucket, grouping_fields):
        group_by = grouping_fields[0]
        grouping_fields = grouping_fields[1:]
        if not grouping_fields:
            counts = {}
            for bucket in outer_bucket[group_by]['buckets']:
                doc_count = bucket['doc_count']
                if doc_count > self._matrix['max_cell_doc_count']:
                    self._matrix['max_cell_doc_count'] = doc_count
                counts[bucket['key']] = doc_count
            summary = []
            for bucket in x_buckets:
                summary.append(counts.get(bucket['key'], 0))
            outer_bucket[group_by] = summary
        else:
            for bucket in outer_bucket[group_by]['buckets']:
                self._summarize_buckets(x_buckets, bucket, grouping_fields)

    def preprocess_view(self):
        '''
        Main function to construct query and build view results json
        * Only publicly accessible function
        '''
        matrix_route = self._request.route_path('matrix', slash='/')
        self._result['@id'] = matrix_route + self._search_base
        self._result['@type'] = ['Matrix']
        self._result['notification'] = ''
        # TODO: Validate doc types in base class in one location
        # Now we do it here and in _validate_items
        type_info = None
        if len(self._doc_types) == 1:
            if self._doc_types[0] in self._types:
                type_info = self._types[self._doc_types[0]]
                self._schema = type_info.schema
        self._validate_items(type_info)
        self._result['title'] = self._set_result_title(type_info)
        self._result['matrix'] = type_info.factory.matrix.copy()
        self._matrix = self._result['matrix']
        self._matrix['x']['limit'] = self._request.params.get('x.limit', 20)
        self._matrix['y']['limit'] = self._request.params.get('y.limit', 5)
        search_route = self._request.route_path('search', slash='/')
        self._matrix['search_base'] = search_route + self._search_base
        matrix_route = self._request.route_path('matrix', slash='/')
        self._matrix['clear_matrix'] = matrix_route + '?type=' + self._doc_types[0]
        self._result['views'] = self._construct_result_views(type_info)
        query, used_filters = self._construct_query()
        print('---------------------------------------------------------------------------------------------------------------')
        #raise ValueError('abc')
        logging.warning('matrix')
        t0 = time.time()
        print('---------------------------------------------------------------------------------------------------------------')         
        es_results = self._elastic_search.search(body=query, index=self._es_index)
        print('---------------------------------------------------------------------------------------------------------------')
        print('end matrix')
        logging.warning(time.time() - t0)
        print('---------------------------------------------------------------------------------------------------------------')         
        aggregations = es_results['aggregations']
        total = aggregations['matrix']['doc_count']
        self._result['matrix']['doc_count'] = total
        self._result['matrix']['max_cell_doc_count'] = 0
        self._result['facets'] = self._format_facets(
            es_results,
            self._facets,
            used_filters,
            (self._schema,),
            total,
            self._principals
        )
        x_grouping = self._matrix['x']['group_by']
        y_groupings = self._matrix['y']['group_by']
        self._summarize_buckets(
            aggregations['matrix']['x']['buckets'],
            aggregations['matrix'],
            y_groupings + [x_grouping]
        )
        self._result['matrix']['y'][y_groupings[0]] = aggregations['matrix'][y_groupings[0]]
        self._result['matrix']['x'].update(aggregations['matrix']['x'])
        self._result.update(
            search_result_actions(
                self._request,
                self._doc_types,
                es_results
            )
        )
        self._result['total'] = es_results['hits']['total']
        if self._result['total']:
            self._result['notification'] = 'Success'
        else:
            self._request.response.status_code = 404
            self._result['notification'] = 'No results found'
        return self._result
