
from pyramid.view import view_config
from ..contentbase import (
    Root
)
from pyelasticsearch import ElasticSearch
from ..schema_utils import (
    load_schema,
)

es = ElasticSearch('http://localhost:9200')
schemas = {
    'biosamples': 'biosample.json',
    'experiments': 'experiment.json',
    'antibodies': 'antibody_approval.json',
    'targets': 'target.json'
}

# This will eventually move to schemas
data = {
    'biosamples': ['@id', '@type', 'accession', 'biosample_term_id', 'biosample_term_name', 'lab.title'],
    'experiments': ['@id', '@type', 'accession', 'description', 'assay_term_name', 'lab.title'],
    'antibodies': ['@id', '@type', 'antibody.accession', 'target.label', 'antibody.source.title'],
    'targets': ['@id', '@type', 'label', 'organism.name', 'lab.title']
}


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
    result.update({
        '@id': '/search/',
        '@type': ['search'],
        'title': 'Search ENCODE',
        '@graph': {}
    })
    items = {}
    items['results'] = []
    items['count'] = {}
    items['facets'] = {}
    params = request.params
    facets = {}

    if 'type' not in params:
        schema = load_schema('biosample.json')
        facets = schema['facets']
    else:
        schema = load_schema(schemas[params.get('type')])
        facets = schema['facets']

    query = Query()
    index = ''

    # Check if we are searching for a specified string or searching everything
    if 'searchTerm' in params:
        if params['searchTerm']:
            if 'type' in params:
                index = schemas[params.get('type')][:-5]
                if len(params) > 2:
                    query = FilteredQuery()
                    query.__setterm__(params.get('searchTerm'))
                    query.fields = data[params.get('type')]
                    for key, value in params.iteritems():
                        if value == 'other':
                            query.__setmissingfilter__(key)
                        elif key != 'searchTerm' and key != 'type':
                            query.__setfilter__(key, value)
                else:
                    query.fields = data[params.get('type')]
                    query.query = {'query_string': {'query': params.get('searchTerm')}}
            else:
                # This code block executes the search for all the types of data
                query.query = {'query_string': {'query': params.get('searchTerm')}}
                for d in data:
                    query.fields = data[d]
                    # Should have some limit on size to have better
                    s = es.search(query, index=schemas[d][:-5], size=1100)
                    for key, value in schemas.items():
                        if value == schemas[d]:
                            items['count'][key] = len(s['hits']['hits'])
                    for dataS in s['hits']['hits']:
                        data_highlight = dataS['fields']
                        if 'highlight' in dataS:
                            for key in dataS['highlight'].keys():
                                data_highlight['highlight'] = dataS['highlight'][key]
                        else:
                            data_highlight['highlight'] = []
                        items['results'].append(data_highlight)
                result['@graph'] = items
                return result
        else:
            return result
    else:
        index = 'biosample'
        query.query = {'match_all': {}}
    
    # We can get rid of this once we have a standard graphs for default search page
    if len(facets.keys()):
        for facet in facets:
            face = {'terms': {'field': '', 'size': 1000}}
            face['terms']['field'] = facets[facet]
            query.facets[facet] = face

    s = es.search(query, index=index, size=1100)
    facet_results = s['facets']
    
    for facet in facet_results:
        face = []
        for term in facet_results[facet]['terms']:
            face.append({term['term']: term['count'], 'field': facets[facet]})
        if facet_results[facet]['missing'] != 0:
            face.append({'other': facet_results[facet]['missing'], 'field': facets[facet]})
        if len(face):
            items['facets'][facet] = face

    if 'searchTerm' in params:
        for key, value in schemas.items():
            if value == index + '.json':
                items['count'][key] = len(s['hits']['hits'])
        for dataS in s['hits']['hits']:
            data_highlight = dataS['fields']
            if 'highlight' in dataS:
                for key in dataS['highlight'].keys():
                    data_highlight['highlight'] = dataS['highlight'][key]
            else:
                data_highlight['highlight'] = []
            items['results'].append(data_highlight)

    else:
        items['count']['biosamples'] = len(s['hits']['hits'])
    
    result['@graph'] = items
    return result
