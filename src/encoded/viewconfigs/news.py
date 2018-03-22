from snovault.viewconfigs.searchview import SearchView
from encoded.helpers.helper import format_results
from collections import OrderedDict
from snovault.helpers.helper import (
    get_filtered_query,
    get_search_fields,
    list_result_fields,
    set_filters, 
    set_facets,
)


class NewsView(SearchView):
    def __init__(self, context, request):
        super(NewsView, self).__init__(context, request)
        self.from_ = 0
        self.size = 25
        self.es_index = 'page'
        
   
    def preprocess_view(self):
        self.result['@id'] = '/news/' + self.search_base
        self.result['@type'] = ['News']
        self.result['notification'] = ''

        doc_types = ['Page'] # We have no query string to specify a type, but we know we want 'Page' for news items.
        search_fields, highlights = get_search_fields(self.request, doc_types)

        # Build filtered query for Page items for news.
        query = get_filtered_query(
            '*',
            search_fields,
            sorted(list_result_fields(self.request, doc_types)),
            self.principals,
            doc_types
        )

        del query['query']['query_string'] # Keyword search on news items is not implemented yet

        # Set sort order to sort by date_created.
        sort = OrderedDict()
        result_sort = OrderedDict()
        sort['embedded.date_created'] = result_sort['date_created'] = {
            'order': 'desc',
            'unmapped_type': 'keyword',
        }
        query['sort'] = result_sort

        self.result['sort'] = result_sort
        used_filters = set_filters(self.request, 
            query, 
            self.result, 
            [('type', 'Page'), ('news', 'true'), ('status', 'released')]
        )

        # Build up the facets to search.
        facets = []
        if len(doc_types) == 1 and 'facets' in self.types[doc_types[0]].schema:
            facets.extend(self.types[doc_types[0]].schema['facets'].items())

        query['aggs'] = set_facets(facets, used_filters, self.principals, doc_types)
        es_results = self.elastic_search.search(
            body=query, 
            index=self.es_index, 
            doc_type=self.es_index, 
            from_=0, 
            size=25)
        total = es_results['hits']['total']

        # Return 404 if no results found.
        if not total:
            # http://googlewebmastercentral.blogspot.com/2014/02/faceted-navigation-best-and-5-of-worst.html
            self.request.response.status_code = 404
            self.result['notification'] = 'No results found'
            self.result['@graph'] = []
            return self.result

        # At this stage, we know we have good results.
        self.result['notification'] = 'Success'
        self.result['total'] = total

        # Place the search results into the @graph property.
        graph = format_results(self.request, es_results['hits']['hits'], self.result)
        self.result['@graph'] = list(graph)

        # Insert the facet data into the results.
        schemas = [self.types[doc_type].schema for doc_type in doc_types]
        self.result['facets'] = self.format_facets(
            es_results, 
            facets, 
            used_filters, 
            schemas, 
            total, 
            self.principals
        )
        return self.result