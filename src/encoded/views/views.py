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
from collections import OrderedDict


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
            {'$value': '/awards/{award}', '$templated': True,
             '$repeat': 'award awards'}
        ]
    }
    unique_key = 'lab:name'
    item_keys = [
        {'name': '{item_type}:name', 'value': '{name}', '$templated': True},
        {'name': '{item_type}:name', 'value': '{title}', '$templated': True},
    ]


@location('awards')
class Award(Collection):
    item_type = 'award'
    schema = load_schema('award.json')
    properties = {
        'title': 'Awards (Grants)',
        'description': 'Listing of awards (aka grants)',
    }
    unique_key = 'award:name'
    item_keys = ['name']


@location('antibody-lots')
class AntibodyLots(Collection):
    item_type = 'antibody_lot'
    schema = load_schema('antibody_lot.json')
    properties = {
        'title': 'Antibodies Registry',
        'description': 'Listing of ENCODE antibodies',
    }
    item_links = {
        'source': {'$value': '/sources/{source}', '$templated': True},
    }
    item_embedded = set(['source'])
    unique_key = 'accession'
    item_keys = [
        {'name': 'accession', 'value': '{accession}', '$templated': True},
        {'name': '{item_type}:source_product_lot', 'value': '{source}/{product_id}/{lot_id}', '$templated': True},
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
    unique_key = 'organism:name'
    item_keys = ['name']


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
    unique_key = 'source:name'
    item_keys = ['name']


@location('donors')
class Donor(Collection):
    item_type = 'donor'
    schema = load_schema('donor.json')
    properties = {
        'title': 'Donors',
        'description': 'Listing Biosample Donors',
    }
    item_links = {
        'organism': {'$value': '/organisms/{organism}', '$templated': True},
    }
    item_embedded = set(['organism'])
    item_keys = ['accession']


@location('treatments')
class Treatment(Collection):
    item_type = 'treatment'
    schema = load_schema('treatment.json')
    properties = {
        'title': 'Treatments',
        'description': 'Listing Biosample Treatments',
    }
    item_keys = ['treatment_name']


@location('constructs')
class Construct(Collection):
    item_type = 'construct'
    schema = load_schema('construct.json')
    properties = {
        'title': 'Constructs',
        'description': 'Listing of Biosample Constructs',
    }
    item_links = {
        'source': {'$value': '/sources/{source}', '$templated': True},
        'documents': [
            {'$value': '/documents/{document}', '$templated': True, '$repeat': 'document documents'},
        ],
    }
    item_embedded = set(['source', 'documents'])
    item_keys = ['vector_name']


@location('construct-validations')
class ConstructValidation(Collection):
    item_type = 'construct_validation'
    schema = load_schema('construct_validation.json')
    properties = {
        'title': 'Constructs Validations',
        'description': 'Listing of biosample construct validations',
    }


@location('documents')
class Document(Collection):
    item_type = 'document'
    schema = load_schema('document.json')
    properties = {
        'title': 'Documents',
        'description': 'Listing of Biosample Documents',
    }

    class Item(ItemWithDocument):
        keys = ['document_name']
        links = {
            'submitter': {'$value': '/users/{submitter}', '$templated': True},
            'lab': {'$value': '/labs/{lab}', '$templated': True},
            'award': {'$value': '/awards/{award}', '$templated': True},
        }
        embedded = set(['submitter', 'lab', 'award'])


@location('biosamples')
class Biosample(Collection):
    item_type = 'biosample'
    schema = load_schema('biosample.json')
    properties = {
        'title': 'Biosamples',
        'description': 'Biosamples used in the ENCODE project',
    }
    item_links = {
        'submitter': {'$value': '/users/{submitter}', '$templated': True},
        'source': {'$value': '/sources/{source}', '$templated': True},
        'lab': {'$value': '/labs/{lab}', '$templated': True},
        'award': {'$value': '/awards/{award}', '$templated': True},
        'donor': {'$value': '/donors/{donor}', '$templated': True},
        'documents': [
            {'$value': '/documents/{document}', '$templated': True, '$repeat': 'document documents'},
        ],
        'treatments': [
            {'$value': '/treatments/{treatment}', '$templated': True, '$repeat': 'treatment treatments'},
        ],
        'constructs': [
            {'$value': '/constructs/{construct}', '$templated': True, '$repeat': 'construct constructs'},
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
    schema = load_schema('target.json')
    properties = {
        'title': 'Targets',
        'description': 'Listing of ENCODE3 targets',
    }
    item_links = {
        'organism': {'$value': '/organisms/{organism}', '$templated': True},
        'submitter': {'$value': '/users/{submitter}', '$templated': True},
        'lab': {'$value': '/labs/{lab}', '$templated': True},
        'award': {'$value': '/awards/{award}', '$templated': True},
        'name': {'$value': '{label}-{organism.name}', '$templated': True},
    }
    item_embedded = set(['organism', 'submitter', 'lab', 'award'])
    #   item_keys = [('target_label', 'organism_name')] multi columns not implemented yet
    unique_key = 'target:name'
    item_keys = ['name']
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
    schema = load_schema('antibody_validation.json')
    properties = {
        'title': 'Antibody Validations',
        'description': 'Listing of antibody validation documents',
    }

    class Item(ItemWithDocument):
        links = {
            'antibody': {'$value': '/antibody-lots/{antibody}', '$templated': True},
            'target': {'$value': '/targets/{target}', '$templated': True},
            'submitter': {'$value': '/users/{submitter}', '$templated': True},
            'lab': {'$value': '/labs/{lab}', '$templated': True},
            'award': {'$value': '/awards/{award}', '$templated': True},
        }
        embedded = set(['antibody', 'target', 'submitter', 'lab', 'award'])


@location('antibodies')
class AntibodyApproval(Collection):
    schema = load_schema('antibody_approval.json')
    item_type = 'antibody_approval'
    properties = {
        'title': 'Antibody Approvals',
        'description': 'Listing of validation approvals for ENCODE antibodies',
    }
    item_links = {
        'antibody': {'$value': '/antibody-lots/{antibody}', '$templated': True},
        'target': {'$value': '/targets/{target}', '$templated': True},
        'validations': [
            {'$value': '/validations/{validation}', '$templated': True, '$repeat': 'validation validations'},
        ],
    }
    item_embedded = set(['antibody', 'target', 'validations'])
    item_keys = [
        {'name': '{item_type}:lot_target', 'value': '{antibody}/{target}', '$templated': True}
    ]
    columns = OrderedDict([
        ('antibody.accession', 'Accession'),
        ('target.target_label', 'Target'),
        ('target.organism.organism_name', 'Species'),
        ('antibody.source.source_name', 'Source'),
        ('antibody.product_id', 'Product ID'),
        ('antibody.lot_id', 'Lot ID'),
        ('validations.length', 'Validations'),
        ('approval_status', 'Status')
    ])


@location('platforms')
class Platform(Collection):
    item_type = 'platform'
    schema = load_schema('platform.json')
    properties = {
        'title': 'Platforms',
        'description': 'Listing of Platforms',
    }


@location('libraries')
class Library(Collection):
    item_type = 'library'
    schema = load_schema('library.json')
    properties = {
        'title': 'Libraries',
        'description': 'Listing of Libraries',
    }
    item_links = {
        'biosample': {'$value': '/biosamples/{biosample}', '$templated': True},
        'documents': [
            {'$value': '/documents/{document}', '$templated': True, '$repeat': 'document documents'},
        ],
    }
    item_embedded = set(['biosample', 'documents'])
    item_keys = [{'name': 'accession', 'value': '{accession}', '$templated': True}]



@location('replicates')
class Replicates(Collection):
    item_type = 'replicate'
    schema = load_schema('replicate.json')
    properties = {
        'title': 'Replicates',
        'description': 'Listing of Replicates',
    }
    item_links = {
        'library': {'$value': '/libraries/{library}', '$templated': True},
        'platform': {'$value': '/platforms/{platform}', '$templated': True},
        'assay': {'$value': '/assays/{assay}', '$templated': True},
    }
    item_embedded = set(['library', 'platform', 'assay'])


@location('software')
class Software(Collection):
    item_type = 'software'
    schema = load_schema('software.json')
    properties = {
        'title': 'Software',
        'description': 'Listing of software',
    }


@location('files')
class Files(Collection):
    item_type = 'file'
    schema = load_schema('file.json')
    properties = {
        'title': 'Files',
        'description': 'Listing of Files',
    }
    item_links = {
        'submitter': {'$value': '/users/{submitter}', '$templated': True},
        'lab': {'$value': '/labs/{lab}', '$templated': True},
        'award': {'$value': '/awards/{award}', '$templated': True},
    }
    item_embedded = set(['submitter', 'lab', 'award'])


@location('experiments')
class Experiments(Collection):
    item_type = 'experiment'
    schema = load_schema('experiment.json')
    properties = {
        'title': 'Experiments',
        'description': 'Listing of Experiments',
    }
    item_links = {
        'submitter': {'$value': '/users/{submitter}', '$templated': True},
        'lab': {'$value': '/labs/{lab}', '$templated': True},
        'award': {'$value': '/awards/{award}', '$templated': True},
        'files': [
            {'$value': '/files/{file}', '$templated': True, '$repeat': 'file files'},
        ],
        'replicates': [
            {'$value': '/replicates/{replicate}', '$templated': True, '$repeat': 'replicate replicates'},
        ],
        'controls': [
            {'$value': '/experiments/{experiment_control}', '$templated': True, '$repeat': 'experiment_control experiment_controls'},
        ],
    }
    item_embedded = set(['files', 'replicates', 'submitter', 'lab', 'award', 'controls'])
    item_keys = [{'name': 'accession', 'value': '{accession}', '$templated': True}]
    columns = OrderedDict([
        ('accession', 'Accession'),
        ('replicates.0.assay.assay_name', 'Assay Type'),
        ('replicates.0.target', 'Target'),
        ('replicates.0.library.biosample.biosample_term_name', 'Biosample'),
        ('replicates.length', 'Biological Replicates'),
        ('files.length', 'Files'),
        ('lab.name', 'Lab'),
        ('project', 'Project')
    ])


@location('rnai')
class RNAi(Collection):
    item_type = 'rnai'
    schema = load_schema('rnai.json')
    properties = {
        'title': 'RNAi',
        'description': 'Listing of RNAi',
    }


@location('dataset')
class Dataset(Collection):
    item_type = 'dataset'
    schema = load_schema('dataset.json')
    properties = {
        'title': 'Datasets',
        'description': 'Listing of datasets',
    }
