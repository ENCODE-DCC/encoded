#from pyramid.security import (
#    Allow,
#    Authenticated,
#    Deny,
#    Everyone,
#)
from . import root
from ..contentbase import (
    Collection,
)
from ..schema_utils import (
    load_schema,
)
from ..storage import (
    DBSession,
    UserMap,
)


#    permission='admin'  ## this prevents loading of users via post_json
@root.location('users')
class User(Collection):
    schema = load_schema('colleague.json')
    properties = {
        'title': 'DCC Users',
        'description': 'Listing of current ENCODE DCC users',
    }
    links = {
        'labs': [
            {'href': '/labs/{lab_uuid}', 'templated': True,
             'repeat': 'lab_uuid lab_uuids'}
        ]
    }

#    __acl__ = [
#        (Allow, Authenticated, 'traverse'),
#        (Deny, Everyone, 'traverse'),
#        ]

    def after_add(self, item):
        email = item.model.statement.object.get('email')
        if email is None:
            return
        session = DBSession()
        login = 'mailto:' + email
        user_map = UserMap(login=login, userid=item.model.rid)
        session.add(user_map)


@root.location('labs')
class Lab(Collection):
    schema = load_schema('lab.json')
    properties = {
        'title': 'Labs',
        'description': 'Listing of ENCODE DCC labs',
    }
    links = {
        'awards': [
            {'href': '/awards/{award_uuid}', 'templated': True,
             'repeat': 'award_uuid award_uuids'}
        ]
    }


@root.location('awards')
class Award(Collection):
    schema = load_schema('award.json')
    properties = {
        'title': 'Awards (Grants)',
        'description': 'Listing of awards (aka grants)',
    }


@root.location('antibody-lots')
class AntibodyLots(Collection):
    #schema = load_schema('antibody_lot.json')
    properties = {
        'title': 'Antibodies Registry',
        'description': 'Listing of ENCODE antibodies',
    }
    links = {
        'source': {'href': '/sources/{source_uuid}', 'templated': True},
    }
    embedded = set(['source'])


@root.location('organisms')
class Organism(Collection):
    schema = load_schema('organism.json')
    properties = {
        'title': 'Organisms',
        'description': 'Listing of all registered organisms',
    }


@root.location('sources')
class Source(Collection):
    schema = load_schema('source.json')
    properties = {
        'title': 'Sources',
        'description': 'Listing of sources and vendors for ENCODE material',
    }
    links = {
        'actions': [
            {'name': 'edit', 'title': 'Edit', 'profile': '/profiles/{item_type}.json', 'method': 'POST', 'href': '', 'templated': True},
        ],
    }


@root.location('donors')
class Donor(Collection):
    ## schema = load_schema('donor.json') Doesn't exist yet
    properties = {
        'title': 'Donors',
        'description': 'Listing Biosample Donors',
    }
    links = {
        'organism': {'href': '/organisms/{organism_uuid}', 'templated': True},
    }
    embedded = set(['organism'])


@root.location('treatments')
class Treatment(Collection):
    ## schema = load_schema('treatment.json') Doesn't exist yet
    properties = {
        'title': 'Treatments',
        'description': 'Listing Biosample Treatments',
    }


@root.location('constructs')
class Construct(Collection):
    properties = {
        'title': 'Constructs',
        'description': 'Listing of Biosample Constructs',
    }
    links = {
        'source': {'href': '/sources/{source_uuid}', 'templated': True},
    }
    embedded = set(['source'])


@root.location('documents')
class Document(Collection):
    properties = {
        'title': 'Documents',
        'description': 'Listing of Biosample Documents',
    }
    links = {
        'submitter': {'href': '/users/{submitter_uuid}', 'templated': True},
        'lab': {'href': '/labs/{lab_uuid}', 'templated': True},
        'award': {'href': '/awards/{award_uuid}', 'templated': True},
    }
    embedded = set(['submitter', 'lab', 'award'])


@root.location('biosamples')
class Biosample(Collection):
    #schema = load_schema('biosample.json')
    properties = {
        'title': 'Biosamples',
        'description': 'Biosamples used in the ENCODE project',
    }
    links = {
        'submitter': {'href': '/users/{submitter_uuid}', 'templated': True},
        'source': {'href': '/sources/{source_uuid}', 'templated': True},
        'lab': {'href': '/labs/{lab_uuid}', 'templated': True},
        'award': {'href': '/awards/{award_uuid}', 'templated': True},
        'donor': {'href': '/donors/{donor_uuid}', 'templated': True},
        'documents': [
            {'href': '/documents/{document_uuid}', 'templated': True, 'repeat': 'document_uuid document_uuids'},
        ],
        'treatments': [
            {'href': '/treatments/{treatment_uuid}', 'templated': True, 'repeat': 'treatment_uuid treatment_uuids'},
        ],
        'constructs': [
            {'href': '/constructs/{construct_uuid}', 'templated': True, 'repeat': 'construct_uuid construct_uuids'},
        ],
    }
    embedded = set(['donor', 'submitter', 'lab', 'award', 'source', 'treatments', 'constructs'])


@root.location('targets')
class Target(Collection):
    #schema = load_schema('target.json')
    properties = {
        'title': 'Targets',
        'description': 'Listing of ENCODE3 targets',
    }
    links = {
        'organism': {'href': '/organisms/{organism_uuid}', 'templated': True},
        'submitter': {'href': '/users/{submitter_uuid}', 'templated': True},
        'lab': {'href': '/labs/{lab_uuid}', 'templated': True},
        'award': {'href': '/awards/{award_uuid}', 'templated': True},
    }
    embedded = set(['organism', 'submitter', 'lab', 'award'])


# The following should really be child collections.
@root.location('validations')
class Validation(Collection):
    #schema = load_schema('validation.json')
    properties = {
        'title': 'Antibody Validations',
        'description': 'Listing of antibody validation documents',
    }
    links = {
        'antibody_lot': {'href': '/antibody-lots/{antibody_lot_uuid}', 'templated': True},
        'target': {'href': '/targets/{target_uuid}', 'templated': True},
        'submitter': {'href': '/users/{submitter_uuid}', 'templated': True},
        'lab': {'href': '/labs/{lab_uuid}', 'templated': True},
        'award': {'href': '/awards/{award_uuid}', 'templated': True},
    }
    embedded = set(['antibody_lot', 'target', 'submitter', 'lab', 'award'])


@root.location('antibodies')
class AntibodyApproval(Collection):
    #schema = load_schema('antibody_approval.json')
    item_type = 'antibody_approval'
    properties = {
        'title': 'Antibody Approvals',
        'description': 'Listing of validation approvals for ENCODE antibodies',
    }
    links = {
        'antibody_lot': {'href': '/antibody-lots/{antibody_lot_uuid}', 'templated': True},
        'target': {'href': '/targets/{target_uuid}', 'templated': True},
        'validations': [
            {'href': '/validations/{validation_uuid}', 'templated': True, 'repeat': 'validation_uuid validation_uuids'},
        ],
    }
    embedded = set(['antibody_lot', 'target'])


@root.location('platforms')
class Platform(Collection):
    #schema = load_schema('award.json')
    properties = {
        'title': 'Platforms',
        'description': 'Listing of Platforms',
    }
