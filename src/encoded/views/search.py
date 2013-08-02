
from pyramid.view import view_config
from ..contentbase import (
    Root
)
from elasticutils import S
from collections import OrderedDict


facets = {}
facets['biosamples'] = ['biosample_type']
facets['antibodies'] = ['target.organism.organism_name']
facets['targets'] = ['organism.organism_name']
facets['experiments'] = ['project']


def getFacets(index):
    '''  Stupidest Method ever '''

    face = ''
    count = 0
    for facet in facets[index]:
        if count == 0:
            face = face + facet
        else:
            face = face + ', ' + facet
    return face


@view_config(name='search', context=Root, request_method='GET')
def search(context, request):
    result = context.__json__(request)
    result.update({
        '@id': '/search/',
        '@type': ['search'],
        'title': 'ElasticSearch View',
        'items': OrderedDict()
    })
    items = OrderedDict()
    queryTerm = request.params.get('searchTerm')
    if queryTerm:
        indexes = ['biosamples', 'antibodies', 'experiments', 'targets']
        for index in indexes:
            s = S().indexes(index).doctypes('basic').values_dict()
            s1 = s.query_raw({'query_string': {'query': queryTerm}}).facet(getFacets(index))
            items[index] = {}
            items[index]['results'] = []
            if len(s):
                items[index]['facets'] = s1.facet_counts()
            for data in s1:
                items[index]['results'].append(data)
    result['items'] = items
    return result
