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
        '$condition': 'alternate_accessions',
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


ALLOW_EVERYONE_VIEW = [
    (Allow, Everyone, ['view', 'list', 'traverse']),
]

ALLOW_SUBMITTER_ADD = [
    (Allow, 'group.submitter', 'add')
]

ALLOW_LAB_SUBMITTER_EDIT = [
    (Allow, 'role.lab_submitter', 'edit'),
    # (Allow, 'role.lab_submitter', 'view_raw'),
]

ALLOW_CURRENT = ALLOW_LAB_SUBMITTER_EDIT + [
    (Allow, 'role.viewer', 'view'),
]

ENCODE2_AWARDS = frozenset([
    '1a4d6443-8e29-4b4a-99dd-f93e72d42418',
    '1f3cffd4-457f-4105-9b3c-3e9119abfcf0',
    '2528d08a-7e67-48f1-b9ad-dc1c29cb926c',
    '2a27a363-6bb5-43cc-99c4-d58bf06d3d8e',
    '2eb561ab-96de-4286-8afd-5479e7ba909d',
    '2f35506f-0b00-4b56-9d65-6c0be5f304b2',
    '366388ac-685d-415c-b0bb-834ffafdf094',
    '60a6088f-b3c8-46eb-8e27-51ef9cda31e0',
    '7fd6664b-17f5-4bfe-9fdf-ed7481cf4d24',
    '9623f1c0-e619-44bc-b430-8cc7176c766c',
    'a7ba7c03-d93f-4503-8116-63db88a1390c',
    'c68bafc1-dda3-41a9-b889-ec756f0368e1',
    'c7ff037b-05ab-4fe0-bded-dd30999e2b3f',
    'cd51d709-b8d1-4ba6-b756-45adcaa38fb9',
    'dd7fb99a-cb0b-407e-9635-16454f0066c1',
    'df972196-c3c7-4a58-a852-94baa87f9b71',
    # Unattributed
    'f06a0db4-b388-48d9-b414-37d83859cad0',
    # ENCODE2-Mouse
    '95839ec3-9b83-44d9-a98a-026a9fd01bda',
    '124b9d72-22bd-4fcc-8e2b-052677c4e3f2',
    '2cda932c-07d5-4740-a024-d585635f5650',
    '5a009305-4ddc-4dba-bbf3-7327ceda3702',
])


class Collection(BaseCollection):
    def __init__(self, parent, name):
        super(Collection, self).__init__(parent, name)
        if hasattr(self, '__acl__'):
            return
        if 'lab' in self.schema['properties']:
            self.__acl__ = ALLOW_SUBMITTER_ADD

    class Item(BaseCollection.Item):
        STATUS_ACL = {
            'CURRENT': ALLOW_CURRENT,
            'DELETED': [],
        }

        def __acl__(self):
            properties = self.properties.copy()
            ns = self.template_namespace(properties)
            properties.update(ns)
            status = ns.get('status')
            return self.STATUS_ACL.get(status, ())

        def __ac_local_roles__(self):
            roles = {}
            properties = self.properties.copy()
            ns = self.template_namespace(properties)
            properties.update(ns)
            if 'lab' in properties:
                lab_submitters = 'submits_for.%s' % properties['lab']
                roles[lab_submitters] = 'role.lab_submitter'
            if properties.get('award') in ENCODE2_AWARDS:
                roles[Everyone] = 'role.viewer'
            return roles


@location('labs')
class Lab(Collection):
    item_type = 'lab'
    schema = load_schema('lab.json')
    __acl__ = ALLOW_EVERYONE_VIEW
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
    __acl__ = ALLOW_EVERYONE_VIEW
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
        'approvals': ('antibody_approval', 'antibody'),
    }


@location('organisms')
class Organism(Collection):
    item_type = 'organism'
    schema = load_schema('organism.json')
    __acl__ = ALLOW_EVERYONE_VIEW
    properties = {
        'title': 'Organisms',
        'description': 'Listing of all registered organisms',
    }
    item_name_key = 'name'
    unique_key = 'organism:name'
    item_keys = ['name']


@location('sources')
class Source(Collection):
    item_type = 'source'
    schema = load_schema('source.json')
    __acl__ = ALLOW_EVERYONE_VIEW
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
    item_keys =  ALIAS_KEYS + ['name']


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
    __acl__ = ALLOW_EVERYONE_VIEW + ALLOW_SUBMITTER_ADD
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
    item_embedded = set(['target'])


class Characterization(Collection):
    class Item(ItemWithAttachment, Collection.Item):
        STATUS_ACL = {
            'IN PROGRESS': ALLOW_LAB_SUBMITTER_EDIT,
            'PENDING DCC REVIEW': ALLOW_LAB_SUBMITTER_EDIT,
            'COMPLIANT': ALLOW_CURRENT,
            'NOT COMPLIANT': ALLOW_CURRENT,
            'NOT REVIEWED': ALLOW_CURRENT,
            'NOT SUBMITTED FOR REVIEW BY LAB': ALLOW_CURRENT,
        }
        base_types = ['characterization'] + Collection.Item.base_types
        embedded = set(['lab', 'award', 'submitted_by'])
        keys = ALIAS_KEYS


@location('construct-characterizations')
class ConstructCharacterization(Characterization):
    item_type = 'construct_characterization'
    schema = load_schema('construct_characterization.json')
    properties = {
        'title': 'Construct characterizations',
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
            'part_of',
            'pooled_from',
            'characterizations.submitted_by',
            'characterizations.award',
            'characterizations.lab',
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

        def template_namespace(self, properties, request=None):
            ns = Collection.Item.template_namespace(self, properties, request)
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
    __acl__ = ALLOW_EVERYONE_VIEW
    properties = {
        'title': 'Targets',
        'description': 'Listing of ENCODE3 targets',
    }
    unique_key = 'target:name'

    class Item(Collection.Item):
        template = {
            'name': {'$value': '{label}-{organism_name}', '$templated': True},
            'title': {'$value': '{label} ({organism_name})', '$templated': True},
        }
        embedded = set(['organism'])
        keys = ALIAS_KEYS + [
            {'name': '{item_type}:name', 'value': '{label}-{organism_name}', '$templated': True},
        ]

        def template_namespace(self, properties, request=None):
            ns = Collection.Item.template_namespace(self, properties, request)
            root = find_root(self)
            # self.properties as we need uuid here
            organism = root.get_by_uuid(self.properties['organism'])
            ns['organism_name'] = organism.properties['name']
            return ns

        @property
        def __name__(self):
            ns = self.template_namespace(self.properties.copy())
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
        embedded = ['submitted_by', 'lab', 'award', 'target', 'target.organism']


@location('antibodies')
class AntibodyApproval(Collection):
    schema = load_schema('antibody_approval.json')
    item_type = 'antibody_approval'
    properties = {
        'title': 'Antibody Approvals',
        'description': 'Listing of characterization approvals for ENCODE antibodies',
    }

    class Item(Collection.Item):
        STATUS_ACL = {
            'ELIGIBLE FOR NEW DATA': ALLOW_CURRENT,
            'NOT ELIGIBLE FOR NEW DATA': ALLOW_CURRENT,
            'NOT PURSUED': ALLOW_CURRENT,
        }
        embedded = [
            'antibody.host_organism',
            'antibody.source',
            'characterizations.award',
            'characterizations.lab',
            'characterizations.submitted_by',
            'characterizations.target.organism',
            'target.organism',
        ]
        keys = [
            {'name': '{item_type}:lot_target', 'value': '{antibody}/{target}', '$templated': True}
        ]


@location('platforms')
class Platform(Collection):
    item_type = 'platform'
    schema = load_schema('platform.json')
    __acl__ = ALLOW_EVERYONE_VIEW
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

    class Item(Collection.Item):
        parent_property = 'experiment'
        namespace_from_path = {
            'lab': 'experiment.lab',
            'award': 'experiment.award',
        }
        keys = ALIAS_KEYS + [
            {
                'name': '{item_type}:experiment_biological_technical',
                'value': '{experiment}/{biological_replicate_number}/{technical_replicate_number}',
                '$templated': True,
            },
        ]
        embedded = set(['library', 'platform'])


@location('software')
class Software(Collection):
    item_type = 'software'
    schema = load_schema('software.json')
    properties = {
        'title': 'Software',
        'description': 'Listing of software',
    }


@location('files')
class File(Collection):
    item_type = 'file'
    schema = load_schema('file.json')
    properties = {
        'title': 'Files',
        'description': 'Listing of Files',
    }

    item_name_key = 'accession'
    item_keys = ACCESSION_KEYS  # + ALIAS_KEYS
    item_namespace_from_path = {
        'lab': 'dataset.lab',
        'award': 'dataset.award',
    }


@location('datasets')
class Dataset(Collection):
    item_type = 'dataset'
    schema = load_schema('dataset.json')
    properties = {
        'title': 'Datasets',
        'description': 'Listing of datasets',
    }
    
    class Item(Collection.Item):
        template = {
            'files': [
                {'$value': '{file}', '$repeat': 'file original_files', '$templated': True},
                {'$value': '{file}', '$repeat': 'file related_files', '$templated': True},
            ],
        }
        template_type = {
            'files': 'file',
        }
        embedded = [
            'files',
            'files.replicate',
            'files.replicate.experiment',
            'files.replicate.experiment.lab',
            'files.replicate.experiment.target',
            'files.submitted_by',
            'submitted_by',
            'lab',
            'award',
            'documents.lab',
            'documents.award',
            'documents.submitted_by',
        ]
        name_key = 'accession'
        keys = ACCESSION_KEYS + ALIAS_KEYS
        rev = {
            'original_files': ('file', 'dataset'),
        }


@location('experiments')
class Experiment(Dataset):
    item_type = 'experiment'
    schema = load_schema('experiment.json')
    properties = {
        'title': 'Experiments',
        'description': 'Listing of Experiments',
    }
    
    class Item(Dataset.Item):
        base_types = [Dataset.item_type] + Dataset.Item.base_types
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
        embedded = Dataset.Item.embedded + [
            'replicates.antibody',
            # 'replicates.antibody.approvals',
            'replicates.library.documents.lab',
            'replicates.library.documents.submitted_by',
            'replicates.library.documents.award',
            'replicates.library.biosample.submitted_by',
            'replicates.library.biosample.source',
            'replicates.library.biosample.organism',
            'replicates.library.biosample.donor.organism',
            'replicates.library.treatments',
            'replicates.platform',
            'possible_controls',
            'target.organism',
        ]
        rev = {
            'replicates': ('replicate', 'experiment'),
        }

        def template_namespace(self, properties, request=None):
            ns = super(Experiment.Item, self).template_namespace(properties, request)
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
    item_keys = ALIAS_KEYS


@location('rnai-characterizations')
class RNAiCharacterization(Characterization):
    item_type = 'rnai_characterization'
    schema = load_schema('rnai_characterization.json')
    properties = {
        'title': 'RNAi characterizations',
        'description': 'Listing of biosample RNAi characterizations',
    }
