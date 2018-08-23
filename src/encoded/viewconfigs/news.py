from snovault.viewconfigs.searchview import SearchView
from encoded.helpers.helper import format_results


class NewsView(SearchView):
    def __init__(self, context, request):
        super(NewsView, self).__init__(context, request)
        self.search_term = '*'
        self.facets = []
        self.from_ = 0
        self.size = 25
        self.es_index = 'page'

    def set_facets(self):
        if len(self.doc_types) == 1 and 'facets' in self.types[self.doc_types[0]].schema:
            self.facets.extend(self.types[self.doc_types[0]].schema['facets'].items())

    def preprocess_view(self):
        self.result['@id'] = '/news/' + self.search_base
        self.result['@type'] = ['News']
        self.result['notification'] = ''

        # construct doc_types
        self.construct_doc_types(['Page'])

        # construct query
        static_items = [('type', 'Page'), ('news', 'true'), ('status', 'released')]
        query = self.construct_query(static_items, False)
        # Delete these keys as these are not needed for news
        del query['sort']['embedded.label']
        del self.result['sort']['label']

        # Query elastic search and update results
        es_results = self.query_elastic_search(query, self.es_index, self.from_, self.size)
        self.result['total'] = self.get_total_results(es_results)
        if not self.result['total']:
            return self.result

        self.result['notification'] = 'Success'

        # Place the search results into the @graph property.
        graph = format_results(self.request, es_results['hits']['hits'], self.result)
        self.result['@graph'] = list(graph)

        # Update facets
        self.result['facets'] = self.construct_facets(es_results, self.result['total'])

        return self.result
