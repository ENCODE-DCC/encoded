
from pyramid.view import view_config
from ..contentbase import (
    Root
)
from pyelasticsearch import ElasticSearch
es = ElasticSearch('http://localhost:9200')


# Query class should be improved to accomodate filters and other ES functionality
class Query(dict):

    def __init__(self):
        self.query = dict()
        self.facets = dict()
        self.fields = []
        self.highlight = dict({'fields': {"*": {}}})

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


#FilteredQuery class is extended version of Query class
class FilteredQuery(dict):

    def __init__(self):
        self.query = dict({'filtered': {'query': {'queryString': {"query": ''}}, 'filter': {'and': {'filters': []}}}})
        self.facets = dict()
        self.fields = []
        self.highlight = dict({'fields': {"*": {}}})

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
        self['query']['filtered']['filter']['and']['filters'].append({'bool': {'must': {'term': {k: v}}}})

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
        'count': {}
    })
    size = 999999
    
    # if no searchTerm
    try:
        search_term = params['searchTerm']
    except:
        return result

    try:
        search_type = params['type']
    except:
        query = Query()
        # This code block executes the search for all the types of data
        query.query = {'query_string': {'query': search_term}}
        indices = ['antibody_approval', 'biosample', 'experiment', 'target']
        fields = ['@id', '@type']
        for index in indices:
            collection = root[index]
            result['columns'].update(collection.columns)
            for column in collection.columns:
                fields.append(column)

        query.fields = list(set(fields))
        # Should have some limit on size to have better
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
        return result
    else:
        collections = root.by_item_type
        fields = ['@id', '@type']
        for collection_name in collections:
            if search_type == root.by_item_type[collection_name].__name__:
                collection = root[collection_name]
                index = collection_name
                schema = collection.schema
                result['columns'] = columns = collection.columns
                break
        query = Query()
        for column in columns:
            fields.append(column)
        query.fields = fields
        query.query = {'query_string': {'query': search_term}}
        
        for facet in schema['facets']:
            face = {'terms': {'field': '', 'size': size}}
            face['terms']['field'] = schema['facets'][facet] + '.untouched'
            query.facets[facet] = face
        
        # Builds filtered query which supports multiple facet selection
        if len(params) > 2:
            for param in params:
                if param not in ['searchTerm', 'type']:
                    query['filter'] = {'term': {param+'.untouched': params[param]}}
        
        results = es.search(query, index=index, size=size)
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
        result['count'][search_type] = len(results['hits']['hits'])
        return result
