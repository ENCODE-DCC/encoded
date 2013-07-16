from .contentbase import Root
from pyramid.view import view_config
from elasticutils import S


def includeme(config):
    config.scan(__name__)


@view_config(name='get_collection', context=Root, subpath_segments=0, request_method='GET')
def getCollection(collection):
    #collection = 'biosamples'
    s = S().indexes('biosamples').doctypes('basic').values_dict('@id').all()
    context = {}
    items = []
    for result in s:
        items.append(result)
    context['items'] = items
    return context
