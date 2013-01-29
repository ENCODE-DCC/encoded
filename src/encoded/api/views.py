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


@CollectionViews.config()
class Organisms(CollectionViews):
    collection = 'organisms'
    item_type = 'organism'
    properties = {
        'title': 'Organisms',
        'description': 'Listing of organisms returned from server',
        }


@CollectionViews.config()
class Sources(CollectionViews):
    collection = 'sources'
    item_type = 'source'
    properties = {
        'title': 'Antibody sources',
        'description': 'Listing of sources returned from server',
        }


@CollectionViews.config()
class Targets(CollectionViews):
    collection = 'targets'
    item_type = 'target'
    properties = {
        'title': 'Antibody targets',
        'description': 'Listing of targets returned from server',
        }


# The following should really be child collections.
@CollectionViews.config()
class Validations(CollectionViews):
    collection = 'validations'
    item_type = 'validation'
    properties = {
        'title': 'Antibody validations',
        'description': 'Listing of validations returned from server',
        }


@CollectionViews.config()
class Approvals(CollectionViews):
    collection = 'approvals'
    item_type = 'approval'
    properties = {
        'title': 'Antibody approvals',
        'description': 'Listing of approvals returned from server',
        }
