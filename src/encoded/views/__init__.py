from pyramid.view import view_config
from ..contentbase import (
    Root,
    acl_from_settings,
)


def includeme(config):
    config.scan()
    config.set_root_factory(root)
    root.__acl__ = acl_from_settings(config.registry.settings) + root.__acl__


root = Root(title='Home', portal_title='ENCODE 3')


@view_config(context=Root, request_method='GET')
def home(context, request):
    result = context.__json__(request)
    result['_links'] = {
        'self': {'href': request.resource_path(context)},
        'profile': {'href': '/profiles/portal'},
        # 'login': {'href': request.resource_path(context, 'login')},
    }
    return result
