
from pyramid.view import view_config
from ..contentbase import (
    Root
)
from elasticutils import S


@view_config(name='search', context=Root, request_method='GET')
def search(context, request):
    result = context.__json__(request)
    result.update({
        '@id': '/search/',
        '@type': ['search'],
        'title': 'ElasticSearch View',
        'items': {}
    })
    items = {}
    queryTerm = request.params.get('searchTerm')
    if queryTerm:
        indexes = ['biosamples', 'antibodies', 'experiments', 'targets']

        for index in indexes:
            items[index] = {}

            basic_s = S().indexes(index).doctypes('basic').values_dict()
            if index == 'biosamples':
                s = basic_s.facet('biosample_type', 'organ_slims', 'system_slims')
            elif index == 'experiments':
                s = basic_s.facet('lab.name', 'project')
            elif index == 'antibodies':
                s = basic_s.facet('target.organism.organism_name', 'approval_status', 'antibody_lot.source.source_name')
            elif index == 'targets':
                s = basic_s.facet('organism.organism_name', 'lab.name')

            items[index]['facets'] = s.query_raw({'query_string': {'query': queryTerm}}).facet_counts()
            s1 = s.query_raw({'query_string': {'query': queryTerm}})
            items[index]['results'] = []
            for data in s1:
                items[index]['results'].append(data)

    result['items'] = items
    return result
