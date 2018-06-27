from pyramid.httpexceptions import HTTPBadRequest
from snovault.viewconfigs.base_view import BaseView
from encoded.helpers.helper import search_result_actions
from snovault.helpers.helper import (
    get_filtered_query,
    get_search_fields,
    set_filters,
    set_facets,
    format_facets
)


audit_facets = [
    ('audit.ERROR.category', {'title': 'Audit category: ERROR'}),
    ('audit.NOT_COMPLIANT.category', {'title': 'Audit category: NOT COMPLIANT'}),
    ('audit.WARNING.category', {'title': 'Audit category: WARNING'}),
    ('audit.INTERNAL_ACTION.category', {'title': 'Audit category: DCC ACTION'})
]


class MatrixView(BaseView):
    def __init__(self, context, request):
        super(MatrixView, self).__init__(context, request)
        self.result['matrix'] = ''
        self.matrix = ''

    def validate_items(self):
        if len(self.doc_types) != 1:
            msg = 'Search result matrix currently requires specifying a single type.'
            raise HTTPBadRequest(explanation=msg)
        item_type = self.doc_types[0]
        if item_type not in self.types:
            msg = 'Invalid type: {}'.format(item_type)
            raise HTTPBadRequest(explanation=msg)
        if not hasattr(self.type_info.factory, 'matrix'):
            msg = 'No matrix configured for type: {}'.format(item_type)
            raise HTTPBadRequest(explanation=msg)

    def set_result_title(self):
        if self.type_info.name is 'Annotation':
            title = 'Encyclopedia'
        else:
            title = self.type_info.name + ' Matrix'
        return title

    def construct_result_views(self, matrix=False, summary=False):
        views = [
            {
                'href': self.request.route_path('search', slash='/') + self.search_base,
                'title': 'View results as list',
                'icon': 'list-alt',
            },
            {
                'href': self.request.route_path('report', slash='/') + self.search_base,
                'title': 'View tabular report',
                'icon': 'table',
            }
        ]
        if matrix:
            if hasattr(self.type_info.factory, 'summary_data'):
                views.append({
                    'href': self.request.route_path('summary', slash='/') + self.search_base,
                    'title': 'View summary report',
                    'icon': 'summary',
                })
        if summary:
            views.append({
                'href': self.request.route_path('matrix', slash='/') + self.search_base,
                'title': 'View summary matrix',
                'icon': 'th',
            })
        return views

    def construct_query(self, view, view_type='matrix'):
        search_fields, highlights = get_search_fields(self.request, self.doc_types)

        # Builds filtered query which supports multiple facet selection
        query = get_filtered_query(self.search_term,
                                   search_fields,
                                   [],
                                   self.principals,
                                   self.doc_types)
        if self.search_term == '*':
            # query['query']['match_all'] = {}
            del query['query']['query_string']
        # If searching for more than one type, don't specify which fields to search
        else:
            # del query['query']['bool']['must']['multi_match']['fields']
            query['query']['query_string']['fields'].extend(['_all', '*.uuid', '*.md5sum', '*.submitted_file_name'])

        # set aggs
        self.set_query_aggs(query, view, view_type)
        if view_type == 'summary':
            query['size'] = 0
        return query

    def set_query_aggs(self, query, view, view_type):
        # Setting filters.
        # Rather than setting them at the top level of the query
        # we collect them for use in aggregations later.
        query_filters = query['post_filter'].pop('bool')
        filter_collector = {'post_filter': {'bool': query_filters}}
        self.used_filters = set_filters(self.request, filter_collector, self.result)
        filters = filter_collector['post_filter']['bool']['must']

        if view_type == 'matrix':
            negative_filters = filter_collector['post_filter']['bool']['must_not']
        elif view_type == 'summary':
            negative_filters = None

        # Adding facets to the query
        self.facets = [(field, facet) for field, facet in self.schema['facets'].items() if
                       field in view['x']['facets'] or field in view['y']['facets']]

        # Display all audits if logged in, or all but INTERNAL_ACTION if logged out
        if view_type == 'matrix':
            for audit_facet in audit_facets:
                if self.search_audit and 'group.submitter' in self.principals or 'INTERNAL_ACTION' not in audit_facet[0]:
                    self.facets.append(audit_facet)

        query['aggs'] = set_facets(self.facets, self.used_filters, self.principals, self.doc_types)
        self.construct_xygroupings(query, view, view_type, filters, negative_filters)

    def construct_xygroupings(self, query, view, view_type, filters, negative_filters=None):

        # Group results in 2 dimensions
        x_grouping = view['x']['group_by']
        y_groupings = view['y']['group_by']
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
        if view_type == 'matrix':
            query['aggs']['matrix'] = {
                "filter": {
                    "bool": {
                        "must": filters,
                        "must_not": negative_filters
                    }
                },
                "aggs": aggs,
            }
        elif view_type == 'summary':
            summary_aggs = None
            summary_groupings = view['grouping']
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
            query['aggs']['summary'] = {
                "filter": {
                    "bool": {
                        "must": filters,
                    }
                },
                "aggs": summary_aggs,
            }

    def query_elastic_search(self, query, es_index):
        # Execute the query
        es_results = self.elastic_search.search(body=query, index=es_index)
        return es_results

    def construct_facets(self, es_results, total):
        facets = format_facets(es_results,
                               self.facets,
                               self.used_filters,
                               (self.schema,),
                               total,
                               self.principals)
        return facets

    def summarize_buckets(self, x_buckets, outer_bucket, grouping_fields):
        group_by = grouping_fields[0]
        grouping_fields = grouping_fields[1:]
        if not grouping_fields:
            counts = {}
            for bucket in outer_bucket[group_by]['buckets']:
                doc_count = bucket['doc_count']
                if doc_count > self.matrix['max_cell_doc_count']:
                    self.matrix['max_cell_doc_count'] = doc_count
                counts[bucket['key']] = doc_count
            summary = []
            for bucket in x_buckets:
                summary.append(counts.get(bucket['key'], 0))
            outer_bucket[group_by] = summary
        else:
            for bucket in outer_bucket[group_by]['buckets']:
                self.summarize_buckets(x_buckets, bucket, grouping_fields)

    def preprocess_view(self):
        self.result['@id'] = self.request.route_path('matrix', slash='/') + self.search_base
        self.result['@type'] = ['Matrix']
        self.result['notification'] = ''
        self.type_info = self.types[self.doc_types[0]]
        self.schema = self.type_info.schema
        self.validate_items()
        self.result['title'] = self.set_result_title()
        self.result['matrix'] = self.type_info.factory.matrix.copy()

        # Populate matrix list
        self.matrix = self.result['matrix']
        self.matrix['x']['limit'] = self.request.params.get('x.limit', 20)
        self.matrix['y']['limit'] = self.request.params.get('y.limit', 5)
        self.matrix['search_base'] = self.request.route_path('search', slash='/') + self.search_base
        self.matrix['clear_matrix'] = self.request.route_path('matrix', slash='/') + '?type=' + self.doc_types[0]

        self.result['views'] = self.construct_result_views(matrix=True)

        # Construct query
        query = self.construct_query(self.matrix)

        # Query elastic search
        es_results = self.query_elastic_search(query, self.es_index)

        # Format matrix for results
        aggregations = es_results['aggregations']
        self.result['matrix']['doc_count'] = total = aggregations['matrix']['doc_count']
        self.result['matrix']['max_cell_doc_count'] = 0

        # Format facets for results
        self.result['facets'] = format_facets(es_results,
                                              self.facets,
                                              self.used_filters,
                                              (self.schema,),
                                              total,
                                              self.principals)

        # Summarize buckets
        x_grouping = self.matrix['x']['group_by']
        y_groupings = self.matrix['y']['group_by']
        self.summarize_buckets(
            aggregations['matrix']['x']['buckets'],
            aggregations['matrix'],
            y_groupings + [x_grouping])

        self.result['matrix']['y'][y_groupings[0]] = aggregations['matrix'][y_groupings[0]]
        self.result['matrix']['x'].update(aggregations['matrix']['x'])

        # Add batch actions
        self.result.update(search_result_actions(self.request,
                                                 self.doc_types,
                                                 es_results))

        # Adding total
        self.result['total'] = es_results['hits']['total']
        if self.result['total']:
            self.result['notification'] = 'Success'
        else:
            # http://googlewebmastercentral.blogspot.com/2014/02/faceted-navigation-best-and-5-of-worst.html
            self.request.response.status_code = 404
            self.result['notification'] = 'No results found'

        return self.result
