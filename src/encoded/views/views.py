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
from ordereddict import OrderedDict


@location('labs')
class Lab(Collection):
    item_type = 'lab'
    schema = load_schema('lab.json')
    properties = {
        'title': 'Labs',
        'description': 'Listing of ENCODE DCC labs',
    }
    item_links = {
        'awards': [
            {'$value': '/awards/{award_uuid}', '$templated': True,
             '$repeat': 'award_uuid award_uuids'}
        ]
    }


@location('awards')
class Award(Collection):
    item_type = 'award'
    schema = load_schema('award.json')
    properties = {
        'title': 'Awards (Grants)',
        'description': 'Listing of awards (aka grants)',
    }
    #item_keys = ['name'] should this be unique


@location('antibody-lots')
class AntibodyLots(Collection):
    item_type = 'antibody_lot'
    #schema = load_schema('antibody_lot.json')
    properties = {
        'title': 'Antibodies Registry',
        'description': 'Listing of ENCODE antibodies',
    }
    item_links = {
        'source': {'$value': '/sources/{source_uuid}', '$templated': True},
    }
    item_embedded = set(['source'])
    item_keys = [
        {'name': 'accession', 'value': '{antibody_accession}', '$templated': True},
        {'name': '{item_type}:source_product_lot', 'value': '{source_uuid}/{product_id}/{lot_id}', '$templated': True},
    ]


@location('organisms')
class Organism(Collection):
    item_type = 'organism'
    schema = load_schema('organism.json')
    properties = {
        'title': 'Organisms',
        'description': 'Listing of all registered organisms',
        'description': 'Listing of sources and vendors for ENCODE material',
    }


@location('sources')
class Source(Collection):
    item_type = 'source'
    schema = load_schema('source.json')
    properties = {
        'title': 'Sources',
        'description': 'Listing of sources and vendors for ENCODE material',
    }
    item_links = {
        'actions': [
            {'name': 'edit', 'title': 'Edit', 'profile': '/profiles/{item_type}.json', 'method': 'POST', 'href': '', '$templated': True, '$condition': 'permission:edit'},
        ],
    }


@location('donors')
class Donor(Collection):
    item_type = 'donor'
    ## schema = load_schema('donor.json') Doesn't exist yet
    properties = {
        'title': 'Donors',
        'description': 'Listing Biosample Donors',
    }
    item_links = {
        'organism': {'$value': '/organisms/{organism_uuid}', '$templated': True},
    }
    item_embedded = set(['organism'])
    item_keys = ['donor_id']


@location('treatments')
class Treatment(Collection):
    item_type = 'biosample_treatment'
    ## schema = load_schema('treatment.json') Doesn't exist yet
    properties = {
        'title': 'Treatments',
        'description': 'Listing Biosample Treatments',
    }
    item_keys = ['treatment_name']


@location('constructs')
class Construct(Collection):
    item_type = 'biosample_construct'
    properties = {
        'title': 'Constructs',
        'description': 'Listing of Biosample Constructs',
    }
    item_links = {
        'source': {'$value': '/sources/{source_uuid}', '$templated': True},
        'documents': [
            {'$value': '/documents/{document_uuid}', '$templated': True, '$repeat': 'document_uuid document_uuids'},
        ],
    }
    item_embedded = set(['source', 'documents'])
    item_keys = ['vector_name']


@location('documents')
class Document(Collection):
    item_type = 'biosample_document'
    properties = {
        'title': 'Documents',
        'description': 'Listing of Biosample Documents',
    }

    class Item(ItemWithDocument):
        keys = ['document_name']
        links = {
            'submitter': {'$value': '/users/{submitter_uuid}', '$templated': True},
            'lab': {'$value': '/labs/{lab_uuid}', '$templated': True},
            'award': {'$value': '/awards/{award_uuid}', '$templated': True},
        }
        embedded = set(['submitter', 'lab', 'award'])


@location('biosamples')
class Biosample(Collection):
    item_type = 'biosample'
    #schema = load_schema('biosample.json')
    properties = {
        'title': 'Biosamples',
        'description': 'Biosamples used in the ENCODE project',
    }
    item_links = {
        'submitter': {'$value': '/users/{submitter_uuid}', '$templated': True},
        'source': {'$value': '/sources/{source_uuid}', '$templated': True},
        'lab': {'$value': '/labs/{lab_uuid}', '$templated': True},
        'award': {'$value': '/awards/{award_uuid}', '$templated': True},
        'donor': {'$value': '/donors/{donor_uuid}', '$templated': True},
        'documents': [
            {'$value': '/documents/{document_uuid}', '$templated': True, '$repeat': 'document_uuid document_uuids'},
        ],
        'treatments': [
            {'$value': '/treatments/{treatment_uuid}', '$templated': True, '$repeat': 'treatment_uuid treatment_uuids'},
        ],
        'constructs': [
            {'$value': '/constructs/{construct_uuid}', '$templated': True, '$repeat': 'construct_uuid construct_uuids'},
        ],
    }
    item_embedded = set(['donor', 'submitter', 'lab', 'award', 'source', 'treatments', 'constructs', 'documents'])
    item_keys = [{'name': 'accession', 'value': '{accession}', '$templated': True}]
    columns = OrderedDict([
        ('accession', 'Accession'),
        ('biosample_term_name', 'Term'),
        ('biosample_type', 'Type'),
        ('donor.organism.organism_name', 'Species'),
        ('source.alias', 'Source'),
        ('lab.name', 'Submitter'),
        ('treatments.length', 'Treatments'),
        ('constructs.length', 'Constructs')
    ])


@location('targets')
class Target(Collection):
    item_type = 'target'
    #schema = load_schema('target.json')
    properties = {
        'title': 'Targets',
        'description': 'Listing of ENCODE3 targets',
    }
    item_links = {
        'organism': {'$value': '/organisms/{organism_uuid}', '$templated': True},
        'submitter': {'$value': '/users/{submitter_uuid}', '$templated': True},
        'lab': {'$value': '/labs/{lab_uuid}', '$templated': True},
        'award': {'$value': '/awards/{award_uuid}', '$templated': True},
    }
    item_embedded = set(['organism', 'submitter', 'lab', 'award'])
    #   item_keys = [('target_label', 'organism_name')] multi columns not implemented yet
    columns = OrderedDict([
        ('target_label', 'Target'),
        ('organism.organism_name', 'Species'),
        ('dbxref.uniprot', 'External Resources'),
        ('project', 'Project')
    ])


# The following should really be child collections.
@location('validations')
class AntibodyValidation(Collection):
    item_type = 'antibody_validation'
    #schema = load_schema('validation.json')
    properties = {
        'title': 'Antibody Validations',
        'description': 'Listing of antibody validation documents',
    }

    class Item(ItemWithDocument):
        links = {
            'antibody_lot': {'$value': '/antibody-lots/{antibody_lot_uuid}', '$templated': True},
            'target': {'$value': '/targets/{target_uuid}', '$templated': True},
            'submitter': {'$value': '/users/{submitter_uuid}', '$templated': True},
            'lab': {'$value': '/labs/{lab_uuid}', '$templated': True},
            'award': {'$value': '/awards/{award_uuid}', '$templated': True},
        }
        embedded = set(['antibody_lot', 'target', 'submitter', 'lab', 'award'])


@location('antibodies')
class AntibodyApproval(Collection):
    #schema = load_schema('antibody_approval.json')
    item_type = 'antibody_approval'
    properties = {
        'title': 'Antibody Approvals',
        'description': 'Listing of validation approvals for ENCODE antibodies',
    }
    item_links = {
        'antibody_lot': {'$value': '/antibody-lots/{antibody_lot_uuid}', '$templated': True},
        'target': {'$value': '/targets/{target_uuid}', '$templated': True},
        'validations': [
            {'$value': '/validations/{validation_uuid}', '$templated': True, '$repeat': 'validation_uuid validation_uuids'},
        ],
    }
    item_embedded = set(['antibody_lot', 'target', 'validations'])
    item_keys = [
        {'name': '{item_type}:lot_target', 'value': '{antibody_lot_uuid}/{target_uuid}', '$templated': True}
    ]
    columns = OrderedDict([
        ('antibody_lot.antibody_accession', 'Accession'),
        ('target.target_label', 'Target'),
        ('target.organism.organism_name', 'Species'),
        ('antibody_lot.source.source_name', 'Source'),
        ('antibody_lot.product_id', 'Product ID'),
        ('antibody_lot.lot_id', 'Lot ID'),
        ('validations.length', 'Validations'),
        ('approval_status', 'Status')
    ])


@location('platforms')
class Platform(Collection):
    item_type = 'platform'
    properties = {
        'title': 'Platforms',
        'description': 'Listing of Platforms',
    }


@location('libraries')
class Library(Collection):
    item_type = 'library'
    properties = {
        'title': 'Libraries',
        'description': 'Listing of Libraries',
    }
    item_links = {
        'biosample': {'$value': '/biosamples/{biosample_uuid}', '$templated': True},
        'documents': [
            {'$value': '/documents/{document_uuid}', '$templated': True, '$repeat': 'document_uuid document_uuids'},
        ],
    }
    item_embedded = set(['biosample', 'documents'])
    item_keys = [{'name': 'accession', 'value': '{accession}', '$templated': True}]


@location('assays')
class Assays(Collection):
    item_type = 'assay'
    properties = {
        'title': 'Assays',
        'description': 'Listing of Assays',
    }


@location('replicates')
class Replicates(Collection):
    item_type = 'replicate'
    properties = {
        'title': 'Replicates',
        'description': 'Listing of Replicates',
    }
    item_links = {
        'library': {'$value': '/libraries/{library_uuid}', '$templated': True},
        'platform': {'$value': '/platforms/{platform_uuid}', '$templated': True},
        'assay': {'$value': '/assays/{assay_uuid}', '$templated': True},
    }
    item_embedded = set(['library', 'platform', 'assay'])


@location('files')
class Files(Collection):
    item_type = 'file'
    properties = {
        'title': 'Files',
        'description': 'Listing of Files',
    }
    item_links = {
        'submitter': {'$value': '/users/{submitter_uuid}', '$templated': True},
        'lab': {'$value': '/labs/{lab_uuid}', '$templated': True},
        'award': {'$value': '/awards/{award_uuid}', '$templated': True},
    }
    item_embedded = set(['submitter', 'lab', 'award'])


@location('experiments')
class Experiments(Collection):
    item_type = 'experiment'
    properties = {
        'title': 'Experiments',
        'description': 'Listing of Experiments',
    }
    item_links = {
        'submitter': {'$value': '/users/{submitter_uuid}', '$templated': True},
        'lab': {'$value': '/labs/{lab_uuid}', '$templated': True},
        'award': {'$value': '/awards/{award_uuid}', '$templated': True},
        'files': [
            {'$value': '/files/{file_uuid}', '$templated': True, '$repeat': 'file_uuid file_uuids'},
        ],
        'replicates': [
            {'$value': '/replicates/{replicate_uuid}', '$templated': True, '$repeat': 'replicate_uuid replicate_uuids'},
        ],
        'controls': [
            {'$value': '/experiments/{experiment_control_uuid}', '$templated': True, '$repeat': 'experiment_control_uuid experiment_control_uuids'},
        ],
    }
    item_embedded = set(['files', 'replicates', 'submitter', 'lab', 'award', 'controls'])
    item_keys = [{'name': 'accession', 'value': '{dataset_accession}', '$templated': True}]
    columns = OrderedDict([
        ('dataset_accession', 'Accession'),
        ('replicates.0.assay.assay_name', 'Assay Type'),
        ('replicates.0.target', 'Target'),
        ('replicates.0.library.biosample.biosample_term_name', 'Biosample'),
        ('replicates.length', 'Biological Replicates'),
        ('files.length', 'Files'),
        ('lab.name', 'Lab'),
        ('project', 'Project')
    ])
