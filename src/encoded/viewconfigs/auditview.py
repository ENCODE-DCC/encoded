"""
# Audit View
Some Desc

Note: This will have redundacy with other search related views.  To Be
Optimized.

## Inheritance
AuditView<-MatrixView<-BaseView

### MatrixView function dependecies
- set_result_title
- validate_items
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


class AuditView(MatrixView):
    '''AuditView'''
    def __init__(self, context, request):
        super(AuditView, self).__init__(context, request)
        self._facets = []
        self._schema = None
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
        x_grouping = self.matrix['x']['group_by']
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

    def _summarize_buckets(self, x_buckets, outer_bucket, audit_field_list):
        '''Helper method for preprocessing view'''
        for category in audit_field_list:
            counts = {}
            for bucket in outer_bucket[category]['buckets']:
                counts = {}
                for assay in bucket['assay_title']['buckets']:
                    doc_count = assay['doc_count']
                    if doc_count > self.matrix['max_cell_doc_count']:
                        self.matrix['max_cell_doc_count'] = doc_count
                    if 'key' in assay:
                        counts[assay['key']] = doc_count
                summary = []
                for xbucket in x_buckets:
                    summary.append(counts.get(xbucket['key'], 0))
                bucket['assay_title'] = summary

    def _set_query_aggs(self, query):
        '''Helper method for preprocessing view'''
        # Setting filters.
        # Rather than setting them at the top level of the query
        # we collect them for use in aggregations later.
        query_filters = query['post_filter'].pop('bool')
        filter_collector = {'post_filter': {'bool': query_filters}}
        used_filters = set_filters(
            self.request,
            filter_collector,
            self.result,
        )
        filters = filter_collector['post_filter']['bool']['must']
        negative_filters = filter_collector['post_filter']['bool']['must_not']
        self._facets = [
            (field, facet)
            for field, facet in self._schema['facets'].items()
            if (
                field in self.matrix['x']['facets'] or
                field in self.matrix['y']['facets']
            )
        ]
        for audit_facet in self.audit_facets:
            if (self.search_audit and 'group.submitter' in self.principals or
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
            self.principals,
            self.doc_types,
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
            aggregations
        ):
        '''Helper method for preprocessing view'''
        group_by = grouping_fields[0]
        grouping_fields = grouping_fields[1:]
        if grouping_fields:
            self._summarize_no_audits(
                x_buckets,
                outer_bucket[group_by],
                grouping_fields,
                aggregations
            )
        counts = {}
        for assay in outer_bucket[group_by]['assay_title']['buckets']:
            doc_count = assay['doc_count']
            if doc_count > self.matrix['max_cell_doc_count']:
                self.matrix['max_cell_doc_count'] = doc_count
            if 'key' in assay:
                counts[assay['key']] = doc_count
        summary = []
        for xbucket in x_buckets:
            summary.append(counts.get(xbucket['key'], 0))
        aggregations[group_by] = outer_bucket[group_by]['assay_title']
        aggregations[group_by]['assay_title'] = summary
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
        self.result['matrix']['y']['label'] = "Audit Category"
        self.result['matrix']['y']['group_by'][0] = "audit_category"
        self.result['matrix']['y']['group_by'][1] = "audit_label"
        self.result['matrix']['y']['audit_category'] = bucket_audit_category_dict
        self.result['matrix']['x'].update(aggregations['matrix']['x'])

    def preprocess_view(self):
        '''
        Main function to construct query and build view results json
        * Only publicly accessible function
        '''
        self.result['@id'] = self.request.route_path('audit', slash='/') + self.search_base
        self.result['@type'] = ['AuditMatrix']
        self.result['notification'] = ''
        type_info = self.types[self.doc_types[0]]
        self._schema = type_info.schema
        self.validate_items(type_info)
        self.result['title'] = self.set_result_title(type_info)
        # Change in copy mechanism:
        # Oringially: copy.deepcopy(type_info.factory.matrix)
        self.result['matrix'] = type_info.factory.matrix.copy()
        self.matrix = self.result['matrix']
        self.matrix['x']['limit'] = self.request.params.get('x.limit', 20)
        self.matrix['y']['limit'] = self.request.params.get('y.limit', 5)
        self.matrix['search_base'] = self.request.route_path('search', slash='/') + self.search_base
        self.matrix['clear_matrix'] = '{}?type={}'.format(
            self.request.route_path('matrix', slash='/'),
            self.doc_types[0],
        )
        self.result['views'] = [
            self.view_item.result_list,
            self.view_item.tabular_report
        ]
        query, audit_field_list, used_filters = self._construct_query()
        es_results = self.elastic_search.search(body=query, index=self.es_index)
        aggregations = es_results['aggregations']
        total = aggregations['matrix']['doc_count']
        self.result['matrix']['doc_count'] = total
        self.result['matrix']['max_cell_doc_count'] = 0
        self.result['facets'] = self.format_facets(
            es_results,
            self._facets,
            used_filters,
            (self._schema,),
            total,
            self.principals
        )
        self._summarize_buckets(
            aggregations['matrix']['x']['buckets'],
            aggregations['matrix'],
            audit_field_list)
        self._summarize_no_audits(
            aggregations['matrix']['x']['buckets'],
            aggregations['matrix'],
            self._no_audits_groupings,
            aggregations['matrix'])
        self._update_aggregations(aggregations)
        self.result.update(
            search_result_actions(
                self.request,
                self.doc_types,
                es_results
            )
        )
        self.result['total'] = es_results['hits']['total']
        if self.result['total']:
            self.result['notification'] = 'Success'
        else:
            self.request.response.status_code = 404
            self.result['notification'] = 'No results found'
        return self.result
