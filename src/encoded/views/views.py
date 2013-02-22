from cornice import Service
from cornice.resource import resource
from . import CollectionViews

# renderer = None here to use our default registered renderer
# cornice's json support predates the pyramid 1.4 stuff.
home = Service(name='home', path='', renderer=None)


@home.get()
def get_home(request):
    result = {
        'title': 'Home',
        'portal_title': 'ENCODE 3',
        '_links': {
            'self': {'href': request.route_path(home.path)},  # See http://git.io/_OKINA
            'profile': {'href': '/profiles/portal'},
            # 'login': {'href': request.route_path('login')},
            },
        }
    return result


#    permission='admin'  ## this prevents loading of users via post_json
@resource(path='/users/{path_segment}', collection_path='/users/', renderer=None)
class Users(CollectionViews):
    collection = 'users'
    item_type = 'user'
    properties = {
        'title': 'DCC Users',
        'description': 'Listing of current ENCODE DCC users',
        }


@resource(path='/labs/{path_segment}', collection_path='/labs/', renderer=None)
class Labs(CollectionViews):
    collection = 'labs'
    item_type = 'lab'
    properties = {
        'title': 'Labs',
        'description': 'Listing of ENCODE DCC labs',
        }


@resource(path='/awards/{path_segment}', collection_path='/awards/', renderer=None)
class Awards(CollectionViews):
    collection = 'awards'
    item_type = 'award'
    properties = {
        'title': 'Awards (Grants)',
        'description': 'Listing of awards (aka grants)',
        }


@resource(path='/antibody-lots/{path_segment}', collection_path='/antibody-lots/', renderer=None)
class AntibodyLots(CollectionViews):
    collection = 'antibody-lots'
    item_type = 'antibody_lot'
    properties = {
        'title': 'Antibodies Registry',
        'description': 'Listing of ENCODE antibodies',
        }
    links = {
        'source': {'href': '/sources/{source_uuid}', 'templated': True},
        }
    embedded = set(['source'])


@resource(path='/organisms/{path_segment}', collection_path='/organisms/', renderer=None)
class Organisms(CollectionViews):
    collection = 'organisms'
    item_type = 'organism'
    properties = {
        'title': 'Organisms',
        'description': 'Listing of all registered organisms',
        }


@resource(path='/sources/{path_segment}', collection_path='/sources/', renderer=None)
class Sources(CollectionViews):
    collection = 'sources'
    item_type = 'source'
    properties = {
        'title': 'Sources',
        'description': 'Listing of sources and vendors for ENCODE material',
        }


@resource(path='/biosamples/{path_segment}', collection_path='/biosamples/', renderer=None)
class Biosamples(CollectionViews):
    collection = 'biosamples'
    item_type = 'biosample'
    properties = {
        'title': 'Biosamples',
        'description': 'Listing of ENCODE3 biosamples',
        }


@resource(path='/targets/{path_segment}', collection_path='/targets/', renderer=None)
class Targets(CollectionViews):
    collection = 'targets'
    item_type = 'target'
    properties = {
        'title': 'Targets',
        'description': 'Listing of ENCODE3 targets',
        }
    links = {
        'organism': {'href': '/organisms/{organism_uuid}', 'templated': True, 'embedded': True},
        }
    embedded = set(['organism'])


# The following should really be child collections.
@resource(path='/validations/{path_segment}', collection_path='/validations/', renderer=None)
class Validations(CollectionViews):
    collection = 'validations'
    item_type = 'validation'
    properties = {
        'title': 'Antibody Validations',
        'description': 'Listing of antibody validation documents',
        }
    links = {
        'antibody_lot': {'href': '/antibody-lots/{antibody_lot_uuid}', 'templated': True, 'embedded': True},
        'target': {'href': '/targets/{target_uuid}', 'templated': True, 'embedded': True},
        }
    embedded = set(['antibody_lot', 'target'])


@resource(path='/antibodies/{path_segment}', collection_path='/antibodies/', renderer=None)
class AntibodyApprovals(CollectionViews):
    collection = 'antibodies'
    item_type = 'antibody_approval'
    properties = {
        'title': 'Antibody Approvals',
        'description': 'cricket needs to give a sentence',
        }
    links = {
        'antibody_lot': {'href': '/antibody-lots/{antibody_lot_uuid}', 'templated': True, 'embedded': True},
        'target': {'href': '/targets/{target_uuid}', 'templated': True, 'embedded': True},
        'validations': [
            {'href': '/validations/{validation_uuid}', 'templated': True, 'repeat': 'validation_uuid validation_uuids'},
            ],
        }
    embedded = set(['antibody_lot', 'target'])
