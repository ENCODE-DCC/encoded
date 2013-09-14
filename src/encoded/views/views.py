#from pyramid.security import (
#    Allow,
#    Authenticated,
#    Deny,
#    Everyone,
#)
from .download import ItemWithAttachment
from ..contentbase import (
    Collection,
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
    },
]


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
    item_embedded = set(['source', 'host_organism'])
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
    item_name_key = 'accession'
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
    item_embedded = set(['source', 'documents', 'characterizations', 'target'])
    # item_keys = ['vector_name']
    item_rev = {
        'characterizations': ('construct_characterization', 'characterizes'),
    }


@location('construct-characterizations')
class ConstructCharacterization(Collection):
    item_type = 'construct_characterization'
    schema = load_schema('construct_characterization.json')
    properties = {
        'title': 'Constructs characterizations',
        'description': 'Listing of biosample construct characterizations',
    }

    class Item(ItemWithAttachment):
        embedded = ['submitted_by', 'lab', 'award']


@location('documents')
class Document(Collection):
    item_type = 'document'
    schema = load_schema('document.json')
    properties = {
        'title': 'Documents',
        'description': 'Listing of Biosample Documents',
    }

    class Item(ItemWithAttachment):
        keys = ALIAS_KEYS
        embedded = set(['submitted_by', 'lab', 'award'])


@location('biosamples')
class Biosample(Collection):
    item_type = 'biosample'
    schema = load_schema('biosample.json')
    properties = {
        'title': 'Biosamples',
        'description': 'Biosamples used in the ENCODE project',
    }
    item_embedded = set(['donor', 'submitted_by', 'lab', 'award', 'source', 'treatments', 'constructs', 'protocol_documents', 'derived_from', 'characterizations'])
    item_name_key = 'accession'
    item_keys = ACCESSION_KEYS + ALIAS_KEYS
    item_rev = {
        'characterizations': ('biosample_characterization', 'characterizes'),
    }
    columns = OrderedDict([
        ('accession', 'Accession'),
        ('biosample_term_name', 'Term'),
        ('biosample_type', 'Type'),
        ('donor.organism.name', 'Species'),
        ('source.title', 'Source'),
        ('lab.title', 'Submitter'),
        ('treatments.length', 'Treatments'),
        ('constructs.length', 'Constructs')
    ])


@location('biosample-characterizations')
class BiosampleCharacterization(Collection):
    item_type = 'biosample_characterization'
    schema = load_schema('biosample_characterization.json')
    properties = {
        'title': 'Biosample characterizations',
        'description': 'Listing of biosample characterizations',
    }

    class Item(ItemWithAttachment):
        embedded = ['submitted_by', 'lab', 'award']


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
        embedded = set(['organism', 'submitted_by', 'lab', 'award'])
        keys =  ALIAS_KEYS + [
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
class AntibodyCharacterization(Collection):
    item_type = 'antibody_characterization'
    schema = load_schema('antibody_characterization.json')
    properties = {
        'title': 'Antibody characterizations',
        'description': 'Listing of antibody characterization documents',
    }

    class Item(ItemWithAttachment):
        embedded = ['submitted_by', 'lab', 'award', 'target']


@location('antibodies')
class AntibodyApproval(Collection):
    schema = load_schema('antibody_approval.json')
    item_type = 'antibody_approval'
    properties = {
        'title': 'Antibody Approvals',
        'description': 'Listing of characterization approvals for ENCODE antibodies',
    }
    item_embedded = set(['antibody', 'target', 'characterizations'])
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
    item_embedded = set(['biosample', 'documents'])
    item_name_key = 'accession'
    item_keys = ACCESSION_KEYS + ALIAS_KEYS


@location('replicates')
class Replicates(Collection):
    item_type = 'replicate'
    schema = load_schema('replicate.json')
    properties = {
        'title': 'Replicates',
        'description': 'Listing of Replicates',
    }
    item_embedded = set(['library', 'platform', 'antibody'])
    item_keys = [
        {
            'name': '{item_type}:experiment_biological_technical',
            'value': '{experiment}/{biological_replicate_number}/{technical_replicate_number}',
            '$templated': True,
        },
    ]


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
    item_embedded = set(['submitted_by', 'lab', 'award', 'replicate'])
    item_name_key = 'accession'
    item_keys = ACCESSION_KEYS  # + ALIAS_KEYS


@location('experiments')
class Experiments(Collection):
    item_type = 'experiment'
    schema = load_schema('experiment.json')
    properties = {
        'title': 'Experiments',
        'description': 'Listing of Experiments',
    }
    item_embedded = set(['files', 'replicates', 'submitted_by', 'lab', 'award', 'possible_controls', 'target'])
    item_rev = {
        'replicates': ('replicate', 'experiment'),
    }
    item_name_key = 'accession'
    item_keys = ACCESSION_KEYS + ALIAS_KEYS
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


@location('rnais')
class RNAi(Collection):
    item_type = 'rnai'
    schema = load_schema('rnai.json')
    properties = {
        'title': 'RNAi',
        'description': 'Listing of RNAi',
    }
    item_embedded = set(['source', 'documents', 'characterizations'])
    item_rev = {
        'characterizations': ('rnai_characterization', 'characterizes'),
    }


@location('rnai-characterizations')
class RNAiCharacterization(Collection):
    item_type = 'rnai_characterization'
    schema = load_schema('rnai_characterization.json')
    properties = {
        'title': 'RNAi characterizations',
        'description': 'Listing of biosample RNAi characterizations',
    }

    class Item(ItemWithAttachment):
        embedded = ['submitted_by', 'lab', 'award']


@location('dataset')
class Dataset(Collection):
    item_type = 'dataset'
    schema = load_schema('dataset.json')
    properties = {
        'title': 'Datasets',
        'description': 'Listing of datasets',
    }
    item_keys = ALIAS_KEYS
