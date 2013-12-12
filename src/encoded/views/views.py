from pyramid.security import (
    Allow,
    Authenticated,
    Deny,
    Everyone,
)
from .download import ItemWithAttachment
from ..contentbase import (
    Collection as BaseCollection,
    location
)
from ..schema_utils import (
    load_schema,
)
from collections import OrderedDict
from pyramid.traversal import find_root

ACCESSION_KEYS = [
    {
        'name': 'accession',
        'value': '{accession}',
        '$templated': True,
        '$condition': 'accession',
    },
    {
        'name': 'accession',
        'value': '{accession}',
        '$repeat': 'accession alternate_accessions',
        '$templated': True,
    },
]

ALIAS_KEYS = [
    {
        'name': 'alias',
        'value': '{alias}',
        '$repeat': 'alias aliases',
        '$templated': True,
        '$condition': 'aliases',
    },
]


class Collection(BaseCollection):
    def __init__(self, parent, name):
        super(Collection, self).__init__(parent, name)
        if hasattr(self, '__acl__'):
            return
        if 'lab' in self.schema['properties']:
            self.__acl__ = [
                (Allow, 'group.submitter', 'add')
            ]

    class Item(BaseCollection.Item):
        STATUS_ACL = {
            'CURRENT': [
                (Allow, 'role.lab_submitter', 'edit'),
            ],
            'DELETED': [],
        }

        def __acl__(self):
            status = self.properties.get('status')
            return self.STATUS_ACL.get(status, ())

        def __ac_local_roles__(self):
            lab_uuid = self.properties.get('lab')
            if lab_uuid is None:
                return None
            lab_submitters = 'submits_for.%s' % lab_uuid
            return {lab_submitters: 'role.lab_submitter'}


@location('labs')
class Lab(Collection):
    item_type = 'lab'
    schema = load_schema('lab.json')
    properties = {
        'title': 'Labs',
        'description': 'Listing of ENCODE DCC labs',
    }
    item_name_key = 'name'
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
    item_name_key = 'name'
    unique_key = 'award:name'
    item_keys = ['name']


@location('antibody-lots')
class AntibodyLot(Collection):
    item_type = 'antibody_lot'
    schema = load_schema('antibody_lot.json')
    properties = {
        'title': 'Antibodies Registry',
        'description': 'Listing of ENCODE antibodies',
    }
    item_template = {
        'title': '{accession}',
        '$templated': True,
    }
    item_name_key = 'accession'
    item_keys = ACCESSION_KEYS + ALIAS_KEYS + [
        {
            'name': '{item_type}:source_product_lot',
            'value': '{source}/{product_id}/{lot_id}',
            '$templated': True,
        },
        {
            'name': '{item_type}:source_product_lot',
            'value': '{source}/{product_id}/{alias}',
            '$repeat': 'alias lot_id_alias',
            '$templated': True,
        },
    ]
    item_rev = {
        'characterizations': ('antibody_characterization', 'characterizes'),
    }


@location('organisms')
class Organism(Collection):
    item_type = 'organism'
    schema = load_schema('organism.json')
    properties = {
        'title': 'Organisms',
        'description': 'Listing of all registered organisms',
        'description': 'Listing of sources and vendors for ENCODE material',
    }
    item_name_key = 'name'
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
    item_template = {
        'actions': [
            {'name': 'edit', 'title': 'Edit', 'profile': '/profiles/{item_type}.json', 'method': 'PUT', 'href': '', '$templated': True, '$condition': 'permission:edit'},
        ],
    }
    item_name_key = 'name'
    unique_key = 'source:name'
    item_keys = ['name']


class DonorItem(Collection.Item):
    base_types = ['donor'] + Collection.Item.base_types
    embedded = set(['organism'])
    name_key = 'accession'
    keys = ACCESSION_KEYS + ALIAS_KEYS


@location('mouse-donors')
class MouseDonor(Collection):
    item_type = 'mouse_donor'
    schema = load_schema('mouse_donor.json')
    properties = {
        'title': 'Mouse donors',
        'description': 'Listing Biosample Donors',
    }

    class Item(DonorItem):
        pass


@location('human-donors')
class HumanDonor(Collection):
    item_type = 'human_donor'
    schema = load_schema('human_donor.json')
    properties = {
        'title': 'Human donors',
        'description': 'Listing Biosample Donors',
    }

    class Item(DonorItem):
        pass


@location('treatments')
class Treatment(Collection):
    item_type = 'treatment'
    schema = load_schema('treatment.json')
    properties = {
        'title': 'Treatments',
        'description': 'Listing Biosample Treatments',
    }
    item_keys = ALIAS_KEYS  # ['treatment_name']


@location('constructs')
class Construct(Collection):
    item_type = 'construct'
    schema = load_schema('construct.json')
    properties = {
        'title': 'Constructs',
        'description': 'Listing of Biosample Constructs',
    }
    item_keys = ALIAS_KEYS  # ['vector_name']
    item_rev = {
        'characterizations': ('construct_characterization', 'characterizes'),
    }


class Characterization(Collection):
    class Item(ItemWithAttachment, Collection.Item):
        base_types = ['characterization'] + Collection.Item.base_types
        embedded = set(['lab', 'award', 'submitted_by'])
        keys = ALIAS_KEYS


@location('construct-characterizations')
class ConstructCharacterization(Characterization):
    item_type = 'construct_characterization'
    schema = load_schema('construct_characterization.json')
    properties = {
        'title': 'Constructs characterizations',
        'description': 'Listing of biosample construct characterizations',
    }


@location('documents')
class Document(Collection):
    item_type = 'document'
    schema = load_schema('document.json')
    properties = {
        'title': 'Documents',
        'description': 'Listing of Biosample Documents',
    }

    class Item(ItemWithAttachment, Collection.Item):
        embedded = set(['lab', 'award', 'submitted_by'])
        keys = ALIAS_KEYS
        

@location('biosamples')
class Biosample(Collection):
    item_type = 'biosample'
    schema = load_schema('biosample.json')
    properties = {
        'title': 'Biosamples',
        'description': 'Biosamples used in the ENCODE project',
    }
    columns = OrderedDict([
        ('accession', 'Accession'),
        ('biosample_term_name', 'Term'),
        ('biosample_type', 'Type'),
        ('organism.name', 'Species'),
        ('source.title', 'Source'),
        ('lab.title', 'Submitter'),
        ('life_stage', 'Life stage'),
        ('treatments.length', 'Treatments length'),
        ('constructs.length', 'Constructs')
    ])

    class Item(Collection.Item):
        template = {
            'organ_slims': [
                {'$value': '{slim}', '$repeat': 'slim organ_slims', '$templated': True}
            ],
            'system_slims': [
                {'$value': '{slim}', '$repeat': 'slim system_slims', '$templated': True}
            ],
            'developmental_slims': [
                {'$value': '{slim}', '$repeat': 'slim developmental_slims', '$templated': True}
            ],
        }
        embedded = set([
            'donor.organism',
            'submitted_by',
            'lab',
            'award',
            'source',
            'treatments.protocols.submitted_by',
            'treatments.protocols.lab',
            'treatments.protocols.award',
            'constructs.documents.submitted_by',
            'constructs.documents.award',
            'constructs.documents.lab',
            'constructs.target',
            'protocol_documents.lab',
            'protocol_documents.award',
            'protocol_documents.submitted_by',
            'derived_from',
            'pooled_from',
            'characterizations',
            'rnais.target.organism',
            'rnais.source',
            'rnais.documents.submitted_by',
            'rnais.documents.award',
            'rnais.documents.lab',
            'organism',
        ])
        name_key = 'accession'

        keys = ACCESSION_KEYS + ALIAS_KEYS
        rev = {
            'characterizations': ('biosample_characterization', 'characterizes'),
        }

        def template_namespace(self, request=None):
            ns = Collection.Item.template_namespace(self, request)
            if request is None:
                return ns
            terms = request.registry['ontology']
            if 'biosample_term_id' in ns:
                if ns['biosample_term_id'] in terms:
                    ns['organ_slims'] = terms[ns['biosample_term_id']]['organs']
                    ns['system_slims'] = terms[ns['biosample_term_id']]['systems']
                    ns['developmental_slims'] = terms[ns['biosample_term_id']]['developmental']
                else:
                    ns['organ_slims'] = ns['system_slims'] = ns['developmental_slims'] = []
            else:
                ns['organ_slims'] = ns['system_slims'] = ns['developmental_slims'] = []
            return ns


@location('biosample-characterizations')
class BiosampleCharacterization(Characterization):
    item_type = 'biosample_characterization'
    schema = load_schema('biosample_characterization.json')
    properties = {
        'title': 'Biosample characterizations',
        'description': 'Listing of biosample characterizations',
    }


@location('targets')
class Target(Collection):
    item_type = 'target'
    schema = load_schema('target.json')
    properties = {
        'title': 'Targets',
        'description': 'Listing of ENCODE3 targets',
    }
    unique_key = 'target:name'
    columns = OrderedDict([
        ('label', 'Target'),
        ('organism.name', 'Species'),
        ('dbxref', 'External resources'),
    ])

    class Item(Collection.Item):
        template = {
            'name': {'$value': '{label}-{organism_name}', '$templated': True},
            'title': {'$value': '{label} ({organism_name})', '$templated': True},
        }
        embedded = set(['organism'])
        keys = ALIAS_KEYS + [
            {'name': '{item_type}:name', 'value': '{label}-{organism_name}', '$templated': True},
        ]

        def template_namespace(self, request=None):
            ns = Collection.Item.template_namespace(self, request)
            root = find_root(self)
            organism = root.get_by_uuid(self.properties['organism'])
            ns['organism_name'] = organism.properties['name']
            return ns

        @property
        def __name__(self):
            ns = self.template_namespace()
            return u'{label}-{organism_name}'.format(**ns)


# The following should really be child collections.
@location('antibody-characterizations')
class AntibodyCharacterization(Characterization):
    item_type = 'antibody_characterization'
    schema = load_schema('antibody_characterization.json')
    properties = {
        'title': 'Antibody characterizations',
        'description': 'Listing of antibody characterization documents',
    }

    class Item(Characterization.Item):
        embedded = ['submitted_by', 'lab', 'award', 'target']


@location('antibodies')
class AntibodyApproval(Collection):
    schema = load_schema('antibody_approval.json')
    item_type = 'antibody_approval'
    properties = {
        'title': 'Antibody Approvals',
        'description': 'Listing of characterization approvals for ENCODE antibodies',
    }
    item_embedded = set(['antibody.source', 'antibody.host_organism', 'target.organism', 'characterizations.target.organism', 'characterizations.award', 'characterizations.submitted_by', 'characterizations.lab'])
    item_keys = [
        {'name': '{item_type}:lot_target', 'value': '{antibody}/{target}', '$templated': True}
    ]
    columns = OrderedDict([
        ('antibody.accession', 'Accession'),
        ('target.label', 'Target'),
        ('target.organism.name', 'Species'),
        ('antibody.source.title', 'Source'),
        ('antibody.product_id', 'Product ID'),
        ('antibody.lot_id', 'Lot ID'),
        ('characterizations.length', 'Characterizations'),
        ('status', 'Status')
    ])


@location('platforms')
class Platform(Collection):
    item_type = 'platform'
    schema = load_schema('platform.json')
    properties = {
        'title': 'Platforms',
        'description': 'Listing of Platforms',
    }
    item_template = {
        'title': '{term_name}',
        '$templated': True,
    }
    item_keys = ALIAS_KEYS


@location('libraries')
class Library(Collection):
    item_type = 'library'
    schema = load_schema('library.json')
    properties = {
        'title': 'Libraries',
        'description': 'Listing of Libraries',
    }
    item_embedded = set(['biosample'])
    item_name_key = 'accession'
    item_keys = ACCESSION_KEYS + ALIAS_KEYS
    columns = OrderedDict([
        ('accession', 'Accession'),
        ('award', 'Award'),
        ('lab', 'Lab'),
        ('biosample.biosample_term_name', 'Biosample'),
        ('biosample.organism.name', 'Species'),
        ('nucleic_acid_term_name', 'Nucleic Acid Term Name'),
    ])


@location('replicates')
class Replicates(Collection):
    item_type = 'replicate'
    schema = load_schema('replicate.json')
    __acl__ = [
        (Allow, 'group.submitter', 'add'),
    ]
    properties = {
        'title': 'Replicates',
        'description': 'Listing of Replicates',
    }
    columns = OrderedDict([
        ('uuid', 'UUID'),
        ('library.accession', 'Library Accession'),
        ('platform.title', 'Platform'),
        ('experiment', 'Experiment'),
        ('technical_replicate_number', 'Technical Replicate Number'),
        ('biological_replicate_number', 'Biological Replicate Number'),
    ])

    class Item(Collection.Item):
        keys = ALIAS_KEYS + [
            {
                'name': '{item_type}:experiment_biological_technical',
                'value': '{experiment}/{biological_replicate_number}/{technical_replicate_number}',
                '$templated': True,
            },
        ]
        embedded = set(['library', 'platform'])

        def __ac_local_roles__(self):
            root = find_root(self)
            experiment = root.get_by_uuid(self.properties['experiment'])
            lab_uuid = experiment.properties.get('lab')
            if lab_uuid is None:
                return None
            lab_submitters = 'submits_for.%s' % lab_uuid
            return {lab_submitters: 'role.lab_submitter'}


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
    item_name_key = 'accession'
    item_keys = ACCESSION_KEYS  # + ALIAS_KEYS
    columns = OrderedDict([
        ('accession', 'Accession'),
        ('dataset', 'Dataset'),
        ('file_format', 'File Format'),
        ('md5sum', 'MD5 Sum'),
        ('output_type', 'Output Type'),
    ])


@location('experiments')
class Experiments(Collection):
    item_type = 'experiment'
    schema = load_schema('experiment.json')
    properties = {
        'title': 'Experiments',
        'description': 'Listing of Experiments',
    }
    columns = OrderedDict([
        ('accession', 'Accession'),
        ('assay_term_name', 'Assay type'),
        ('target.label', 'Target'),
        ('biosample_term_name', 'Biosample'),
        ('replicates.length', 'Replicates'),
        ('files.length', 'Files'),
        ('lab.title', 'Lab'),
        ('award.rfa', 'Project'),
    ])
    
    class Item(Collection.Item):
        template = {
            'organ_slims': [
                {'$value': '{slim}', '$repeat': 'slim organ_slims', '$templated': True}
            ],
            'system_slims': [
                {'$value': '{slim}', '$repeat': 'slim system_slims', '$templated': True}
            ],
            'developmental_slims': [
                {'$value': '{slim}', '$repeat': 'slim developmental_slims', '$templated': True}
            ],
        }
        embedded = set(['files', 'replicates.antibody', 'replicates.library.documents.lab', 'replicates.library.documents.submitted_by', 'replicates.library.documents.award', 'replicates.library.biosample.submitted_by', 'replicates.library.biosample.organism', 'replicates.library.biosample.donor.organism', 'submitted_by', 'lab', 'award', 'possible_controls', 'target.organism', 'documents.lab', 'documents.award', 'documents.submitted_by'])
        rev = {
            'replicates': ('replicate', 'experiment'),
        }
        name_key = 'accession'
        keys = ACCESSION_KEYS + ALIAS_KEYS

        def template_namespace(self, request=None):
            ns = Collection.Item.template_namespace(self, request)
            if request is None:
                return ns
            terms = request.registry['ontology']
            if 'biosample_term_id' in ns:
                if ns['biosample_term_id'] in terms:
                    ns['organ_slims'] = terms[ns['biosample_term_id']]['organs']
                    ns['system_slims'] = terms[ns['biosample_term_id']]['systems']
                    ns['developmental_slims'] = terms[ns['biosample_term_id']]['developmental']
                else:
                    ns['organ_slims'] = ns['system_slims'] = ns['developmental_slims'] = []
            else:
                ns['organ_slims'] = ns['system_slims'] = ns['developmental_slims'] = []
            return ns


@location('rnais')
class RNAi(Collection):
    item_type = 'rnai'
    schema = load_schema('rnai.json')
    properties = {
        'title': 'RNAi',
        'description': 'Listing of RNAi',
    }
    item_embedded = set(['source', 'documents'])
    item_rev = {
        'characterizations': ('rnai_characterization', 'characterizes'),
    }


@location('rnai-characterizations')
class RNAiCharacterization(Characterization):
    item_type = 'rnai_characterization'
    schema = load_schema('rnai_characterization.json')
    properties = {
        'title': 'RNAi characterizations',
        'description': 'Listing of biosample RNAi characterizations',
    }


@location('datasets')
class Dataset(Collection):
    item_type = 'dataset'
    schema = load_schema('dataset.json')
    properties = {
        'title': 'Datasets',
        'description': 'Listing of datasets',
    }
    item_keys = ACCESSION_KEYS + ALIAS_KEYS
