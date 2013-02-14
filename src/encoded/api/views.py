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


@CollectionViews.config(
#    permission='admin'  ## this prevents loading of users via post_json
)
class Users(CollectionViews):
    collection = 'users'
    item_type = 'user'
    properties = {
        'title': 'ENCODE DCC Users',
        'description': 'List of current ENCODE DCC Users',
        }


@CollectionViews.config()
class Labs(CollectionViews):
    collection = 'labs'
    item_type = 'lab'
    properties = {
        'title': 'Labs',
        'description': 'Listing of labs returned from server',
        }


@CollectionViews.config()
class Awards(CollectionViews):
    collection = 'awards'
    item_type = 'award'
    properties = {
        'title': 'Awards (Grants)',
        'description': 'Listing of awards (aka grants) returned from server',
        }


@CollectionViews.config()
class AntibodyLots(CollectionViews):
    collection = 'antibody-lots'
    item_type = 'antibody_lot'
    properties = {
        'title': 'Antibodies registry',
        'description': 'Listing of antibodies returned from server',
        }
    links = {
        'source': {'href': '/sources/{source_uuid}', 'templated': True},
        }
    embedded = set(['source'])


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
        'title': 'Sources',
        'description': 'Listing of sources returned from server',
        }


@CollectionViews.config()
class Biosamples(CollectionViews):
    collection = 'biosamples'
    item_type = 'biosample'
    properties = {
        'title': 'Biosamples',
        'description': 'Listing of biosamples returned from server',
        }


@CollectionViews.config()
class Targets(CollectionViews):
    collection = 'targets'
    item_type = 'target'
    properties = {
        'title': 'Antibody targets',
        'description': 'Listing of targets returned from server',
        }
    links = {
        'organism': {'href': '/organisms/{organism_uuid}', 'templated': True, 'embedded': True},
        }
    embedded = set(['organism'])


# The following should really be child collections.
@CollectionViews.config()
class Validations(CollectionViews):
    collection = 'validations'
    item_type = 'validation'
    properties = {
        'title': 'Antibody validations',
        'description': 'Listing of validations returned from server',
        }
    links = {
        'antibody_lot': {'href': '/antibody-lots/{antibody_lot_uuid}', 'templated': True, 'embedded': True},
        'target': {'href': '/targets/{target_uuid}', 'templated': True, 'embedded': True},
        }
    embedded = set(['antibody_lot', 'target'])


@CollectionViews.config()
class AntibodyApprovals(CollectionViews):
    collection = 'antibodies'
    item_type = 'antibody_approval'
    properties = {
        'title': 'Antibody approvals',
        'description': 'Listing of approvals returned from server',
        }
    links = {
        'antibody_lot': {'href': '/antibody-lots/{antibody_lot_uuid}', 'templated': True, 'embedded': True},
        'target': {'href': '/targets/{target_uuid}', 'templated': True, 'embedded': True},
        'validations': [
            {'href': '/validations/{validation_uuid}', 'templated': True, 'repeat': 'validation_uuid validation_uuids'},
            ],
        }
    embedded = set(['antibody_lot', 'target'])
