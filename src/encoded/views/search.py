
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
        queryTerm = '*' + queryTerm + '*'
        indexes = ['biosamples', 'antibodies', 'experiments', 'targets']
        for index in indexes:
            s = S().indexes(index).doctypes('basic').values_dict().query_raw({'query_string': {'query': queryTerm}}).all()
            items[index] = []
            for data in s:
                items[index].append(data)
    result['items'] = items
    return result
