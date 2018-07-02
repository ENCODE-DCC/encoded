import copy
from encoded.viewconfigs.matrix import MatrixView
from encoded.helpers.helper import search_result_actions
from snovault.helpers.helper import format_facets


class AuditView(MatrixView):
    def __init__(self, context, request):
        super(AuditView, self).__init__(context, request)
        self.result['matrix'] = ''
        self.matrix = ''
        self.no_audits_groupings = ['no.audit.error', 'no.audit.not_compliant', 'no.audit.warning']

    def construct_result_views(self):
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
        return views

    def construct_xygroupings(self, query, filters, negative_filters):
        # To get list of audit categories from facets
        audit_field_list_copy = []
        audit_field_list = []
        for item in self.facets:
            if item[0].rfind('audit.') > -1:
                audit_field_list.append(item)

        audit_field_list_copy = audit_field_list.copy()

        # Gets just the fields from the tuples from facet data
        for item in audit_field_list_copy:  # for each audit label
            temp = item[0]
            audit_field_list[audit_field_list.index(item)] = temp  # replaces list with just audit field

        # Group results in 2 dimensions
        x_grouping = self.matrix['x']['group_by']
        y_groupings = audit_field_list

        aggs = self.construct_aggs(x_grouping, y_groupings, audit_field_list)
        query['aggs']['matrix'] = {
            "filter": {
                "bool": {
                    "must": filters,
                    "must_not": negative_filters
                }
            },
            "aggs": aggs,
        }

    def construct_aggs(self, x_grouping, y_grouping, audit_field_list):
        x_agg = {
            "terms": {
                "field": 'embedded.' + x_grouping,
                "size": 999999,  # no limit
            },
        }
        # aggs query for audit category rows
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

        # This is a nested query with error as the top most level and warning as the innermost level.
        # It allows for there to be multiple missing fields in the query.
        # To construct this we go through the no_audits_groupings backwards and construct the query
        # from the inside out.
        temp = {}
        temp_copy = {}
        for group in reversed(self.no_audits_groupings):
            temp = {
                "missing": {
                    "field": audit_field_list[self.no_audits_groupings.index(group)]
                },
                "aggs": {
                    x_grouping: x_agg
                },
            }
            # If not the last element in no_audits_groupings then add the inner query
            # inside the next category query. Therefore, as temp is updated, it sets the old temp,
            # which is now temp_copy, within itself. This creates the nested structure.
            if (self.no_audits_groupings.index(group) + 1) < len(self.no_audits_groupings):
                temp["aggs"][self.no_audits_groupings[(self.no_audits_groupings.index(group) + 1)]] = temp_copy
            temp_copy = copy.deepcopy(temp)

        # This adds the outermost grouping label to temp.
        update_temp = {}
        update_temp[self.no_audits_groupings[0]] = temp

        # Aggs query gets updated with no audits queries.
        aggs.update(update_temp)

        # If internal action data is able to be seen in facets (if logged in) then add it to aggs for
        # both: 1) an audit category row for Internal Action and 2) the no audits row as innermost
        # level of nested query to create a no audits at all row within no audits.
        # Additionally, add it to the no_audits_groupings list to be used in summarize_no_audits later.
        if "audit.INTERNAL_ACTION.category" in self.facets[len(self.facets) - 1]:
            aggs['audit.INTERNAL_ACTION.category'] = {
                'aggs': {
                    x_grouping: x_agg
                },
                'terms': {
                    'field': 'audit.INTERNAL_ACTION.category', 'size': 999999
                }
            }
            aggs['no.audit.error']['aggs']['no.audit.not_compliant']['aggs']['no.audit.warning']['aggs']['no.audit.internal_action'] = {
                "missing": {"field": "audit.INTERNAL_ACTION.category"},
                "aggs": {x_grouping: x_agg}
            }
            self.no_audits_groupings.append("no.audit.internal_action")

        aggs['x'] = x_agg

        return aggs

    def summarize_buckets(self, x_buckets, outer_bucket, grouping_fields):
        # Loop through each audit category and get proper search result data and format it
        for category in grouping_fields:  # for each audit category
            counts = {}
            # Go through each bucket
            for bucket in outer_bucket[category]['buckets']:
                counts = {}
                # Go through each assay for a key/row and get count and add to counts dictionary
                # that keeps track of counts for each key/row.
                for assay in bucket['assay_title']['buckets']:
                    doc_count = assay['doc_count']
                    if doc_count > self.matrix['max_cell_doc_count']:
                        self.matrix['max_cell_doc_count'] = doc_count
                    if 'key' in assay:
                        counts[assay['key']] = doc_count

                # We now have `counts` containing each displayed key and the corresponding count for a
                # row of the matrix. Convert that to a list of counts (cell values for a row of the
                # matrix) to replace the existing bucket for the given grouping_fields term with a
                # simple list of counts without their keys -- the position within the list corresponds
                # to the keys within 'x'.
                summary = []
                for xbucket in x_buckets:
                    summary.append(counts.get(xbucket['key'], 0))
                bucket['assay_title'] = summary

    def summarize_no_audits(self, x_buckets, outer_bucket, grouping_fields, aggregations):
        # Loop by recursion through grouping_fields until we get the terminal no audit field. So
        # get the initial no audit field in the list and save the rest for the recursive call.
        group_by = grouping_fields[0]
        grouping_fields = grouping_fields[1:]

        # If there are still items in grouping_fields, then loop by recursion until there is
        # nothing left in grouping_fields.
        if grouping_fields:
            self.summarize_no_audits(x_buckets, outer_bucket[group_by], grouping_fields, aggregations)

        counts = {}
        # We have recursed through to the last grouping_field in the array given in the top-
        # level summarize_buckets call. Now we can get down to actually converting the search
        # result data. First loop through each element in the term's 'buckets' which contain
        # displayable key and a count.
        for assay in outer_bucket[group_by]['assay_title']['buckets']:
            # Grab the count for the row, and keep track of the maximum count we find by
            # mutating the max_cell_doc_count property of the matrix for the front end to use
            # to color the cells. Then we add to a counts dictionary that keeps track of each
            # displayed term and the corresponding count.
            doc_count = assay['doc_count']
            if doc_count > self.matrix['max_cell_doc_count']:
                self.matrix['max_cell_doc_count'] = doc_count
            if 'key' in assay:
                counts[assay['key']] = doc_count

        # We now have `counts` containing each displayed key and the corresponding count for a
        # row of the matrix. Convert that to a list of counts (cell values for a row of the
        # matrix) to replace the existing bucket for the given grouping_fields term with a
        # simple list of counts without their keys -- the position within the list corresponds
        # to the keys within 'x'.
        summary = []
        for xbucket in x_buckets:
            summary.append(counts.get(xbucket['key'], 0))
        # Set proper results in aggregations. Instead of keeping the nested structure from the
        # query, set each no audit category as a separate item. Delete the other information
        # from the nested queries. *Not really sure if this information is necessary so I just
        # took it out.*
        aggregations[group_by] = outer_bucket[group_by]['assay_title']
        aggregations[group_by]['assay_title'] = summary
        aggregations[group_by].pop("buckets", None)
        aggregations[group_by].pop("sum_other_doc_count", None)
        aggregations[group_by].pop("doc_count_error_upper_bound", None)

    def update_aggregations(self, aggregations):
        # There is no generated key for the no audit categories, so we need to manually add them so
        # that they will be able to be read in the JS file.
        aggregations['matrix']['no.audit.error']['key'] = 'no errors'
        aggregations['matrix']['no.audit.not_compliant']['key'] = 'no errors and compliant'
        aggregations['matrix']['no.audit.warning']['key'] = 'no errors, compliant, and no warnings'
        if "no.audit.internal_action" in self.no_audits_groupings:
            aggregations['matrix']['no.audit.internal_action']['key'] = "no audits"

        # We need to format the no audits entries as subcategories in an overal 'no_audits' row.
        # To do this, we need to make it the same format as the audit category entries so the JS
        # file will read them and treat them equally.
        aggregations['matrix']['no_audits'] = {}
        aggregations['matrix']['no_audits']['buckets'] = []

        # Add the no audit categories into the overall no_audits entry.
        for category in aggregations['matrix']:
            if "no.audit" in category:
                aggregations['matrix']['no_audits']['buckets'].append(aggregations['matrix'][category])

        # Remove the no audit categories now that they have been added to the overall no_audits row.
        for audit in self.no_audits_groupings:
            aggregations['matrix'].pop(audit)

        # Formats all audit categories into readable/usable format for auditmatrix.js
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
        # Add correctly formatted data to results
        self.result['matrix']['y']['audit_category'] = bucket_audit_category_dict
        self.result['matrix']['x'].update(aggregations['matrix']['x'])

    def preprocess_view(self):
        self.result['@id'] = self.request.route_path('audit', slash='/') + self.search_base
        self.result['@type'] = ['AuditMatrix']
        self.result['notification'] = ''
        self.type_info = self.types[self.doc_types[0]]
        self.schema = self.type_info.schema

        self.validate_items()

        self.type_info = self.types[self.doc_types[0]]
        self.schema = self.type_info.schema
        self.result['title'] = self.set_result_title()
        self.result['matrix'] = self.type_info.factory.matrix.copy()

        # Populate matrix list
        self.matrix = self.result['matrix']
        self.matrix['x']['limit'] = self.request.params.get('x.limit', 20)
        self.matrix['y']['limit'] = self.request.params.get('y.limit', 5)
        self.matrix['search_base'] = self.request.route_path('search', slash='/') + self.search_base
        self.matrix['clear_matrix'] = self.request.route_path('matrix', slash='/') + '?type=' + self.doc_types[0]

        self.result['views'] = self.construct_result_views

        # Construct query
        query = self.construct_query()

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
            y_groupings)
        self.summarize_no_audits(
            aggregations['matrix']['x']['buckets'],
            aggregations['matrix'],
            self.no_audits_groupings,
            aggregations['matrix'])

        # Update aggregations
        self.update_aggregations(aggregations)

        # Add batch actions
        self.result.update(search_result_actions(self.request,
                                                 self.doc_types,
                                                 self.es_results))

        # Adding total
        self.result['total'] = es_results['hits']['total']
        if self.result['total']:
            self.result['notification'] = 'Success'
        else:
            # http://googlewebmastercentral.blogspot.com/2014/02/faceted-navigation-best-and-5-of-worst.html
            self.request.response.status_code = 404
            self.result['notification'] = 'No results found'

        return self.result
