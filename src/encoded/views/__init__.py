from pyramid.view import view_config
from random import randint
from ..contentbase import (
    Root,
    location_root,
)


def includeme(config):
    # Random processid so etags are invalidated after restart.
    config.registry['encoded.processid'] = randint(0, 2 ** 32)
    config.scan()


@location_root
class EncodedRoot(Root):
    properties = {
        'title': 'Home',
        'portal_title': 'ENCODE 3',
    }


@view_config(context=Root, request_method='GET')
def home(context, request):
    result = context.__json__(request)
    result.update({
        '@id': request.resource_path(context),
        '@type': ['portal'],
        # 'login': {'href': request.resource_path(context, 'login')},
    })
    return result
