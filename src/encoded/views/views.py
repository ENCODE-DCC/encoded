#from pyramid.security import (
#    Allow,
#    Authenticated,
#    Deny,
#    Everyone,
#)
from .download import ItemWithDocument
from ..contentbase import (
    Collection,
    location
)
from ..schema_utils import (
    load_schema,
)


@location('labs')
class Lab(Collection):
    schema = load_schema('lab.json')
    properties = {
        'title': 'Labs',
        'description': 'Listing of ENCODE DCC labs',
    }
    item_links = {
        'awards': [
            {'href': '/awards/{award_uuid}', 'templated': True,
             'repeat': 'award_uuid award_uuids'}
        ]
    }


@location('awards')
class Award(Collection):
    schema = load_schema('award.json')
    properties = {
        'title': 'Awards (Grants)',
        'description': 'Listing of awards (aka grants)',
    }
    #item_keys = ['name'] should this be unique


@location('antibody-lots')
class AntibodyLots(Collection):
    #schema = load_schema('antibody_lot.json')
    properties = {
        'title': 'Antibodies Registry',
        'description': 'Listing of ENCODE antibodies',
    }
    item_links = {
        'source': {'href': '/sources/{source_uuid}', 'templated': True},
    }
    item_embedded = set(['source'])
    item_keys = [
        {'name': 'accession', 'value': '{antibody_accession}', 'templated': True},
        {'name': '{item_type}:source_product_lot', 'value': '{source_uuid}/{product_id}/{lot_id}', 'templated': True},
    ]


@location('organisms')
class Organism(Collection):
    schema = load_schema('organism.json')
    properties = {
        'title': 'Organisms',
        'description': 'Listing of all registered organisms',
        'description': 'Listing of sources and vendors for ENCODE material',
    }


@location('sources')
class Source(Collection):
    schema = load_schema('source.json')
    properties = {
        'title': 'Sources',
        'description': 'Listing of sources and vendors for ENCODE material',
    }
    item_links = {
        'actions': [
            {'name': 'edit', 'title': 'Edit', 'profile': '/profiles/{item_type}.json', 'method': 'POST', 'href': '', 'templated': True, 'condition': 'permission:edit'},
        ],
    }


@location('donors')
class Donor(Collection):
    ## schema = load_schema('donor.json') Doesn't exist yet
    properties = {
        'title': 'Donors',
        'description': 'Listing Biosample Donors',
    }
    item_links = {
        'organism': {'href': '/organisms/{organism_uuid}', 'templated': True},
    }
    item_embedded = set(['organism'])
    item_keys = ['donor_id']


@location('treatments')
class Treatment(Collection):
    ## schema = load_schema('treatment.json') Doesn't exist yet
    properties = {
        'title': 'Treatments',
        'description': 'Listing Biosample Treatments',
    }
    item_keys = ['treatment_name']


@location('constructs')
class Construct(Collection):
    properties = {
        'title': 'Constructs',
        'description': 'Listing of Biosample Constructs',
    }
    item_links = {
        'source': {'href': '/sources/{source_uuid}', 'templated': True},
    }
    item_embedded = set(['source'])
    item_keys = ['vector_name']


@location('documents')
class Document(Collection):
    properties = {
        'title': 'Documents',
        'description': 'Listing of Biosample Documents',
    }

    class Item(ItemWithDocument):
        keys = ['document_name']
        links = {
            'submitter': {'href': '/users/{submitter_uuid}', 'templated': True},
            'lab': {'href': '/labs/{lab_uuid}', 'templated': True},
            'award': {'href': '/awards/{award_uuid}', 'templated': True},
        }
        embedded = set(['submitter', 'lab', 'award'])


@location('biosamples')
class Biosample(Collection):
    #schema = load_schema('biosample.json')
    properties = {
        'title': 'Biosamples',
        'description': 'Biosamples used in the ENCODE project',
    }
    item_links = {
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
    item_embedded = set(['donor', 'submitter', 'lab', 'award', 'source', 'treatments', 'constructs'])
    item_keys = [{'name': 'accession', 'value': '{accession}', 'templated': True}]


@location('targets')
class Target(Collection):
    #schema = load_schema('target.json')
    properties = {
        'title': 'Targets',
        'description': 'Listing of ENCODE3 targets',
    }
    item_links = {
        'organism': {'href': '/organisms/{organism_uuid}', 'templated': True},
        'submitter': {'href': '/users/{submitter_uuid}', 'templated': True},
        'lab': {'href': '/labs/{lab_uuid}', 'templated': True},
        'award': {'href': '/awards/{award_uuid}', 'templated': True},
    }
    item_embedded = set(['organism', 'submitter', 'lab', 'award'])
    #   item_keys = [('target_label', 'organism_name')] multi columns not implemented yet


# The following should really be child collections.
@location('validations')
class Validation(Collection):
    #schema = load_schema('validation.json')
    properties = {
        'title': 'Antibody Validations',
        'description': 'Listing of antibody validation documents',
    }

    class Item(ItemWithDocument):
        links = {
            'antibody_lot': {'href': '/antibody-lots/{antibody_lot_uuid}', 'templated': True},
            'target': {'href': '/targets/{target_uuid}', 'templated': True},
            'submitter': {'href': '/users/{submitter_uuid}', 'templated': True},
            'lab': {'href': '/labs/{lab_uuid}', 'templated': True},
            'award': {'href': '/awards/{award_uuid}', 'templated': True},
        }
        embedded = set(['antibody_lot', 'target', 'submitter', 'lab', 'award'])
        keys = [
            {'name': '{item_type}:lot_target', 'value': '{antibody_lot_uuid}/{target_uuid}', 'templated': True}
        ]


@location('antibodies')
class AntibodyApproval(Collection):
    #schema = load_schema('antibody_approval.json')
    item_type = 'antibody_approval'
    properties = {
        'title': 'Antibody Approvals',
        'description': 'Listing of validation approvals for ENCODE antibodies',
    }
    item_links = {
        'antibody_lot': {'href': '/antibody-lots/{antibody_lot_uuid}', 'templated': True},
        'target': {'href': '/targets/{target_uuid}', 'templated': True},
        'validations': [
            {'href': '/validations/{validation_uuid}', 'templated': True, 'repeat': 'validation_uuid validation_uuids'},
        ],
    }
    item_embedded = set(['antibody_lot', 'target'])


@location('platforms')
class Platform(Collection):
    properties = {
        'title': 'Platforms',
        'description': 'Listing of Platforms',
    }


@location('libraries')
class Library(Collection):
    properties = {
        'title': 'Libraries',
        'description': 'Listing of Libraries',
    }
    item_links = {
        'biosample': {'href': '/biosamples/{biosample_uuid}', 'templated': True},
        'documents': [
            {'href': '/documents/{document_uuid}', 'templated': True, 'repeat': 'document_uuid document_uuids'},
        ],
    }
    item_embedded = set(['biosample'])
    item_keys = [{'name': 'accession', 'value': '{accession}', 'templated': True}]


@location('assays')
class Assays(Collection):
    properties = {
        'title': 'Assays',
        'description': 'Listing of Assays',
    }


@location('replicates')
class Replicates(Collection):
    properties = {
        'title': 'Replicates',
        'description': 'Listing of Replicates',
    }
    item_links = {
        'library': {'href': '/libraries/{library_uuid}', 'templated': True},
        'platform': {'href': '/platforms/{platform_uuid}', 'templated': True},
        'assay': {'href': '/assays/{assay_uuid}', 'templated': True},
    }
    item_embedded = set(['library', 'platform', 'assay'])


@location('files')
class Files(Collection):
    properties = {
        'title': 'Files',
        'description': 'Listing of Files',
    }
    item_links = {
        'submitter': {'href': '/users/{submitter_uuid}', 'templated': True},
        'lab': {'href': '/labs/{lab_uuid}', 'templated': True},
        'award': {'href': '/awards/{award_uuid}', 'templated': True},
    }
    item_embedded = set(['submitter', 'lab', 'award'])


@location('experiments')
class Experiments(Collection):
    properties = {
        'title': 'Experiments',
        'description': 'Listing of Experiments',
    }
    item_links = {
        'submitter': {'href': '/users/{submitter_uuid}', 'templated': True},
        'lab': {'href': '/labs/{lab_uuid}', 'templated': True},
        'award': {'href': '/awards/{award_uuid}', 'templated': True},
        'files': [
            {'href': '/files/{file_uuid}', 'templated': True, 'repeat': 'file_uuid file_uuids'},
        ],
        'replicates': [
            {'href': '/replicates/{replicate_uuid}', 'templated': True, 'repeat': 'replicate_uuid replicate_uuids'},
        ],
        'experiments': [
            {'href': '/experiments/{experiment_control_uuid}', 'templated': True, 'repeat': 'experiment_control_uuid experiment_control_uuids'},
        ],
    }
    item_embedded = set(['files', 'replicates', 'submitter', 'lab', 'award', 'experiments'])
    item_keys = [{'name': 'accession', 'value': '{dataset_accession}', 'templated': True}]
