"""
# Audit View
Some Desc

Note: This will have redundacy with other search related views.  To Be
Optimized.

## Inheritance
AuditView<-MatrixView<-BaseView

### MatrixView function dependencies
- _set_result_title
- _validate_items
### BaseView function dependencies
- _format_facets
"""
import copy

from encoded.helpers.helper import search_result_actions
from encoded.viewconfigs.matrix import MatrixView

from snovault.helpers.helper import (  # pylint: disable=import-error
    get_filtered_query,
    get_search_fields,
    set_facets,
    set_filters,
)


class AuditView(MatrixView):  #pylint: disable=too-few-public-methods
    '''Audit View'''
    _view_name = 'audit'
    _factory_name = 'matrix'
    def __init__(self, context, request):
        super(AuditView, self).__init__(context, request)
        self._no_audits_groupings = [
            'no.audit.error',
            'no.audit.not_compliant',
            'no.audit.warning'
        ]

    def _construct_aggs(self, x_grouping, audit_field_list):
        '''Helper Method for constructing query'''
        # pylint: disable=too-many-locals
        x_agg = {
            "terms": {
                "field": 'embedded.' + x_grouping,
                "size": 999999,  # no limit
            },
        }
        aggs = {
            'audit.ERROR.category': {
                'aggs': {
                    x_grouping: x_agg
                },
                'terms': {
                    'field': 'audit.ERROR.category', 'size': 999999
                }
            },
            'audit.WARNING.category': {
                'aggs': {
                    x_grouping: x_agg
                },
                'terms': {
                    'field': 'audit.WARNING.category', 'size': 999999
                }
            },
            'audit.NOT_COMPLIANT.category': {
                'aggs': {
                    x_grouping: x_agg
                },
                'terms': {
                    'field': 'audit.NOT_COMPLIANT.category', 'size': 999999
                }
            }
        }
        temp = {}
        temp_copy = {}
        for group in reversed(self._no_audits_groupings):
            temp = {
                "missing": {
                    "field": audit_field_list[self._no_audits_groupings.index(group)]
                },
                "aggs": {
                    x_grouping: x_agg
                },
            }
            if (self._no_audits_groupings.index(group) + 1) < len(self._no_audits_groupings):
                inc_key = (self._no_audits_groupings.index(group) + 1)
                no_audit_key = self._no_audits_groupings[inc_key]
                temp["aggs"][no_audit_key] = temp_copy
            temp_copy = copy.deepcopy(temp)
        update_temp = {}
        update_temp[self._no_audits_groupings[0]] = temp
        aggs.update(update_temp)
        if "audit.INTERNAL_ACTION.category" in self._facets[len(self._facets) - 1]:
            aggs['audit.INTERNAL_ACTION.category'] = {
                'aggs': {
                    x_grouping: x_agg
                },
                'terms': {
                    'field': 'audit.INTERNAL_ACTION.category', 'size': 999999
                }
            }
            very_nested_obj = {
                "missing": {"field": "audit.INTERNAL_ACTION.category"},
                "aggs": {x_grouping: x_agg}
            }
            aggs_nest_one = aggs['no.audit.error']['aggs']
            aggs_nest_two = aggs_nest_one['no.audit.not_compliant']['aggs']
            aggs_nest_thr = aggs_nest_two['no.audit.warning']['aggs']
            aggs_nest_thr['no.audit.internal_action'] = very_nested_obj
            self._no_audits_groupings.append("no.audit.internal_action")
        aggs['x'] = x_agg
        return aggs

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
        audit_field_list, used_filters = self._set_query_aggs(query)
        return query, audit_field_list, used_filters

    def _construct_xygroupings(
            self,
            query,
            filters,
            negative_filters,
            audit_field_list
        ):
        '''Helper Method for constructing query'''
        # pylint: disable=arguments-differ
        x_grouping = self._matrix['x']['group_by']
        aggs = self._construct_aggs(x_grouping, audit_field_list)
        query['aggs']['matrix'] = {
            "filter": {
                "bool": {
                    "must": filters,
                    "must_not": negative_filters
                }
            },
            "aggs": aggs,
        }

    def _summarize_buckets(self, x_buckets, outer_bucket, audit_field_list, bucket_key):
        """
        Preprocesses view.

            :param x_buckets: x bucket
            :param outer_bucket: outer bucket
            :param audit_field_list: audit field list
            :param bucket_key: buckey key
        """
        # pylint: disable=arguments-differ
        for category in audit_field_list:
            counts = {}
            for bucket in outer_bucket[category]['buckets']:
                counts = {}
                for assay in bucket[bucket_key]['buckets']:
                    doc_count = assay['doc_count']
                    if doc_count > self._matrix['max_cell_doc_count']:
                        self._matrix['max_cell_doc_count'] = doc_count
                    if 'key' in assay:
                        counts[assay['key']] = doc_count
                summary = []
                for xbucket in x_buckets:
                    summary.append(counts.get(xbucket['key'], 0))
                bucket[bucket_key] = summary

    def _set_query_aggs(self, query):
        '''Helper method for preprocessing view'''
        # Setting filters.
        # Rather than setting them at the top level of the query
        # we collect them for use in aggregations later.
        query_filters = query['post_filter'].pop('bool')
        filter_collector = {'post_filter': {'bool': query_filters}}
        used_filters = set_filters(
            self._request,
            filter_collector,
            self._result,
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
        for audit_facet in self._audit_facets:
            if (self._search_audit and 'group.submitter' in self._principals or
                    'INTERNAL_ACTION' not in audit_facet[0]):
                self._facets.append(audit_facet)
        audit_field_list_copy = []
        audit_field_list = []
        for item in self._facets:
            if item[0].rfind('audit.') > -1:
                audit_field_list.append(item)
        audit_field_list_copy = audit_field_list.copy()
        for item in audit_field_list_copy:
            temp = item[0]
            audit_field_list[audit_field_list.index(item)] = temp
        query['aggs'] = set_facets(
            self._facets,
            used_filters,
            self._principals,
            self._doc_types,
        )
        self._construct_xygroupings(
            query,
            filters,
            negative_filters,
            audit_field_list
        )
        return audit_field_list, used_filters

    def _summarize_no_audits(
            self,
            x_buckets,
            outer_bucket,
            grouping_fields,
            aggregations,
            bucket_key
        ): # pylint: disable=too-many-arguments
        """
        Preprocesses view.

            :param x_buckets: x buckets
            :param outer_bucket: outer buckets
            :param grouping_fields: field groups
            :param aggregations: aggregations
            :param bucket_key: bucket key
        """
        group_by = grouping_fields[0]
        grouping_fields = grouping_fields[1:]
        if grouping_fields:
            self._summarize_no_audits(
                x_buckets,
                outer_bucket[group_by],
                grouping_fields,
                aggregations,
                bucket_key
            )
        counts = {}
        for assay in outer_bucket[group_by][bucket_key]['buckets']:
            doc_count = assay['doc_count']
            if doc_count > self._matrix['max_cell_doc_count']:
                self._matrix['max_cell_doc_count'] = doc_count
            if 'key' in assay:
                counts[assay['key']] = doc_count
        summary = []
        for xbucket in x_buckets:
            summary.append(counts.get(xbucket['key'], 0))
        aggregations[group_by] = outer_bucket[group_by][bucket_key]
        aggregations[group_by][bucket_key] = summary
        aggregations[group_by].pop("buckets", None)
        aggregations[group_by].pop("sum_other_doc_count", None)
        aggregations[group_by].pop("doc_count_error_upper_bound", None)

    def _update_aggregations(self, aggregations):
        '''Helper method for preprocessing view'''
        aggregations['matrix']['no.audit.error']['key'] = 'no errors'
        aggregations['matrix']['no.audit.not_compliant']['key'] = 'no errors and compliant'
        no_audit_warning_key = 'no errors, compliant, and no warnings'
        aggregations['matrix']['no.audit.warning']['key'] = no_audit_warning_key
        if "no.audit.internal_action" in self._no_audits_groupings:
            aggregations['matrix']['no.audit.internal_action']['key'] = "no audits"
        aggregations['matrix']['no_audits'] = {}
        aggregations['matrix']['no_audits']['buckets'] = []
        for category in aggregations['matrix']:
            if "no.audit" in category:
                aggregations['matrix']['no_audits']['buckets'].append(
                    aggregations['matrix'][category]
                )
        for audit in self._no_audits_groupings:
            aggregations['matrix'].pop(audit)
        bucket_audit_category_list = []
        for audit in aggregations['matrix']:
            if "audit" in audit:
                audit_category_dict = {}
                audit_category_dict['audit_label'] = aggregations['matrix'][audit]
                audit_category_dict['key'] = audit
                bucket_audit_category_list.append(audit_category_dict)
        bucket_audit_category_dict = {}
        bucket_audit_category_dict['buckets'] = bucket_audit_category_list
        self._result['matrix']['y']['label'] = "Audit Category"
        self._result['matrix']['y']['group_by'][0] = "audit_category"
        self._result['matrix']['y']['group_by'][1] = "audit_label"
        self._result['matrix']['y']['audit_category'] = bucket_audit_category_dict
        self._result['matrix']['x'].update(aggregations['matrix']['x'])

    def preprocess_view(self):
        '''
        Main function to construct query and build view results json
        * Only publicly accessible function
        '''
        audit_route = self._request.route_path('audit', slash='/')
        self._result['@id'] = audit_route + self._search_base
        self._result['@type'] = ['AuditMatrix']
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
        # Because the formatting of the query edits the sub-objects of the matrix, we need to
        # deepcopy the matrix so the original type_info.factory.matrix is not modified, allowing
        # /matrix to get the correct data and to not be able to access the /audit data.
        self._result['matrix'] = copy.deepcopy(type_info.factory.matrix)
        self._matrix = self._result['matrix']
        self._matrix['x']['limit'] = self._request.params.get('x.limit', 20)
        self._matrix['y']['limit'] = self._request.params.get('y.limit', 5)
        search_route = self._request.route_path('search', slash='/')
        self._matrix['search_base'] = search_route + self._search_base
        self._matrix['clear_matrix'] = '{}?type={}'.format(
            self._request.route_path('audit', slash='/'),
            self._doc_types[0],
        )
        self._result['views'] = [
            self._view_item.result_list,
            self._view_item.tabular_report
        ]
        query, audit_field_list, used_filters = self._construct_query()
        es_results = self._elastic_search.search(body=query, index=self._es_index)
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
        doc_type = self._doc_types[0].lower()
        bucket_key = ('annotation_type' if doc_type == 'annotation' else 'assay_title')
        self._summarize_buckets(
            aggregations['matrix']['x']['buckets'],
            aggregations['matrix'],
            audit_field_list,
            bucket_key)
        self._summarize_no_audits(
            aggregations['matrix']['x']['buckets'],
            aggregations['matrix'],
            self._no_audits_groupings,
            aggregations['matrix'],
            bucket_key)
        self._update_aggregations(aggregations)
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
