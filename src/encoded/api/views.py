from pyramid.view import view_config
from . import CollectionViews


@view_config(route_name='home', request_method='GET')
def home(request):
    result = {
        'title': 'Home',
        'portal_title': 'ENCODE 3',
        '_links': {
            'self': {'href': request.route_path('home')},
            'profile': {'href': '/profiles/portal'},
            # 'login': {'href': request.route_path('login')},
            },
        }
    return result


@CollectionViews.config()
class Antibodies(CollectionViews):
    collection = 'antibodies'
    item_type = 'antibody'
    properties = {
        'title': 'Antibodies registry',
        'description': 'Listing of antibodies returned from server',
        }
