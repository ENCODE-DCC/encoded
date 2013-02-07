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
class AntibodyLots(CollectionViews):
    collection = 'antibody-lots'
    item_type = 'antibody_lot'
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
class AntibodyApprovals(CollectionViews):
    collection = 'antibodies'
    item_type = 'antibody_approval'
    properties = {
        'title': 'Antibody approvals',
        'description': 'Listing of approvals returned from server',
        }
    links = {
        'self': {'href': '/approvals/{_uuid}', 'templated': True},
        'antibody_lot': {'href': '/antibodies/{antibody_uuid}', 'templated': True},
        'target': {'href': '/targets/{target_uuid}', 'templated': True},
        'validations': [],
        }

    def embedded(self, model, item):
        embedded = {}
        expand = {
            'antibody_lot': '/antibody-lots/{antibody_lot_uuid}',
            'target': '/targets/{target_uuid}',
            }
        for rel, path in expand.items():
            subreq = self.request.copy()
            subreq.override_renderer = 'null_renderer'
            subreq.path_info = path.format(**item)
            response = self.request.invoke_subrequest(subreq)
            embedded[rel] = response
        return embedded

    _embedded = {
        'antibody_lot': {'href': '/antibodies/{antibody_uuid}', 'templated': True},
        'target': {'href': '/targets/{target_uuid}', 'templated': True},
        }
