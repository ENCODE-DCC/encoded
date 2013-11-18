
from pyramid.view import view_config
from ..contentbase import (
    Root
)
from pyelasticsearch import ElasticSearch
es = ElasticSearch('http://localhost:9200')


# TODO: FilteredQuery should be improved
class FilteredQuery(dict):

    def __init__(self):
        self.query = dict({'filtered': {'query': {'queryString': {"query": ''}}, 'filter': {'and': {'filters': []}}}})
        self.facets = dict()
        self.fields = []

    def __setattr__(self, k, v):
        if k in self.keys():
            self[k] = v
        elif not hasattr(self, k):
            self[k] = v
        else:
            raise AttributeError("Cannot set '%s', cls attribute already exists" % (k, ))

    def __getattr__(self, k):
        if k in self.keys():
            return self[k]
        raise AttributeError

    def __setterm__(self, v):
        self['query']['filtered']['query']['queryString']['query'] = v

    def __setfilter__(self, k, v):
        self['query']['filtered']['filter']['and']['filters'].append({'bool': {'must': {'term': {k + '.untouched': v}}}})

    def __setmissingfilter__(self, v):
        self['query']['filtered']['filter']['and']['filters'].append({'missing': {'field': v}})


@view_config(name='search', context=Root, request_method='GET', permission='search')
def search(context, request):
    ''' Search view connects to ElasticSearch and returns the results'''

    result = context.__json__(request)
    params = request.params
    root = request.root
    result.update({
        '@id': '/search/',
        '@type': ['search'],
        'title': 'Search ENCODE',
        'facets': [],
        '@graph': [],
        'columns': {},
        'count': {},
        'filters': [],
        'notification': ''
    })

    if 'limit' in params:
        size = 999999
    else:
        size = 100

    try:
        search_term = params['searchTerm']
    except:
        if 'type' in params:
            if params['type'] == '*':
                result['notification'] = 'Please enter search term'
                return result
            else:
                search_term = "*"
        else:
            result['notification'] = 'Please enter search term'
            return result

    try:
        # Checking for index type
        search_type = params['type']
    except:
        if not search_term:
            result['notification'] = 'Please enter search term'
            return result
        # This code block executes the search for all the types of data
        query = {'query': {}, 'facets': {}, 'fields': []}
        query['query'] = {'query_string': {'query': search_term}}
        indices = ['antibody_approval', 'biosample', 'experiment', 'target']
        fields = ['@id', '@type']
        for index in indices:
            collection = root[index]
            result['columns'].update(collection.columns)
            for column in collection.columns:
                fields.append(column)

        query['fields'] = list(set(fields))
        
        # Should have some limit on size
        # Should have a better way to organize the count
        s = es.search(query, index=indices, size=999999)
        antibody_count = biosample_count = experiment_count = target_count = 0
        for dataS in s['hits']['hits']:
            data_highlight = dataS['fields']
            if dataS['fields']['@type'][0] == 'antibody_approval':
                antibody_count = antibody_count + 1
            elif dataS['fields']['@type'][0] == 'biosample':
                biosample_count = biosample_count + 1
            elif dataS['fields']['@type'][0] == 'experiment':
                experiment_count = experiment_count + 1
            elif dataS['fields']['@type'][0] == 'target':
                target_count = target_count + 1
            result['count']['biosamples'] = biosample_count
            result['count']['antibodies'] = antibody_count
            result['count']['experiments'] = experiment_count
            result['count']['targets'] = target_count
            if 'highlight' in dataS:
                for key in dataS['highlight'].keys():
                    data_highlight['highlight'] = dataS['highlight'][key]
            else:
                data_highlight['highlight'] = []
            result['@graph'].append(data_highlight)
        
        if len(result['@graph']):
            result['notification'] = 'Success'
        else:
            result['notification'] = 'No results found'
        
        return result
    else:
        
        # Handling wild card searches for all types
        search_type = params['type']
        if search_term == '*' and search_type == '*':
            result['notification'] = 'Please enter search terme'
            return result
        
        # Building query for filters
        collections = root.by_item_type
        fields = ['@id', '@type']
        for collection_name in collections:
            if search_type == collection_name:
                collection = root[collection_name]
                index = collection_name
                schema = collection.schema
                result['columns'] = columns = collection.columns
                break
        
        # Builds filtered query which supports multiple facet selection
        query = FilteredQuery()
        regular_query = 1
        for key, value in params.iteritems():
            if key not in ['type', 'searchTerm', 'limit', 'format']:
                regular_query = 0
                query.__setterm__(search_term)
                if value == 'other':
                    query.__setmissingfilter__(key)
                else:
                    query.__setfilter__(key, value)
                result['filters'].append({key: value})
        
        # If not FQ use regular Query
        if regular_query:
            query = {'query': {}, 'facets': {}, 'fields': []}
            query['query'] = {'query_string': {'query': search_term}}
        
        # Adding fields to the query
        for column in columns:
            fields.append(column)
        query['fields'] = fields

        if 'facets' in schema:
            for facet in schema['facets']:
                face = {'terms': {'field': '', 'size': size}}
                face['terms']['field'] = schema['facets'][facet] + '.untouched'
                query['facets'][facet] = face

                # Remove the facet if is already selected
                for f in result['filters']:
                    if schema['facets'][facet] == f.keys()[0]:
                        del(query['facets'][facet])
        else:
            # If no facets are present remove attribute from query
            del(query['facets'])

        # Execute the query
        results = es.search(query, index=index, size=size)

        # Loading facets in to the results
        if 'facets' in results:
            facet_results = results['facets']
            for facet in facet_results:
                face = {}
                face['field'] = schema['facets'][facet]
                face[facet] = []
                for term in facet_results[facet]['terms']:
                    face[facet].append({term['term']: term['count']})
                if facet_results[facet]['missing'] != 0:
                    face[facet].append({'other': facet_results[facet]['missing']})
                result['facets'].append(face)

        for dataS in results['hits']['hits']:
            data_highlight = dataS['fields']
            if 'highlight' in dataS:
                for key in dataS['highlight'].keys():
                    data_highlight['highlight'] = dataS['highlight'][key]
            else:
                data_highlight['highlight'] = []
            result['@graph'].append(data_highlight)

        result['count'][root.by_item_type[collection_name].__name__] = results['hits']['total']
        if len(result['@graph']):
            result['notification'] = 'Success'
        else:
            result['notification'] = 'No results found'
        return result
