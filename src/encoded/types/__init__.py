from ..contentbase import (
    location
)
from ..schema_utils import (
    load_schema,
)
from .base import (
    ACCESSION_KEYS,
    ALIAS_KEYS,
    Collection,
)
from .download import ItemWithAttachment


def includeme(config):
    config.scan()


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


@location('organisms')
class Organism(Collection):
    item_type = 'organism'
    schema = load_schema('organism.json')
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
    properties = {
        'title': 'Sources',
        'description': 'Listing of sources and vendors for ENCODE material',
    }
    item_name_key = 'name'
    unique_key = 'source:name'
    item_keys = ALIAS_KEYS + ['name']


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
    item_embedded = set(['target'])


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
    unique_key = 'platform:term_id'
    item_name_key = 'term_id'
    item_keys = ALIAS_KEYS + [
        {'name': '{item_type}:term_id', 'value': '{term_id}', '$templated': True},
        {'name': '{item_type}:term_id', 'value': '{term_name}', '$templated': True},
    ]


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


@location('rnais')
class RNAi(Collection):
    item_type = 'rnai'
    schema = load_schema('rnai.json')
    properties = {
        'title': 'RNAi',
        'description': 'Listing of RNAi',
    }
    item_embedded = set(['source', 'documents', 'target'])
    item_rev = {
        'characterizations': ('rnai_characterization', 'characterizes'),
    }
    item_keys = ALIAS_KEYS


@location('publications')
class Publication(Collection):
    item_type = 'publication'
    schema = load_schema('publication.json')
    properties = {
        'title': 'Publications',
        'description': 'Publication pages',
    }
    unique_key = 'publication:title'

    class Item(Collection.Item):
        template = {
            'publication_year': {
                '$value': '{publication_year}',
                '$templated': True,
                '$condition': 'publication_year',
            },
        }

        keys = ALIAS_KEYS + [
            {'name': '{item_type}:title', 'value': '{title}', '$templated': True},
            {
                'name': '{item_type}:reference',
                'value': '{reference}',
                '$repeat': 'reference references',
                '$templated': True,
                '$condition': 'reference',
            },
        ]

        def template_namespace(self, properties, request=None):
            ns = Collection.Item.template_namespace(self, properties, request)
            if 'date_published' in ns:
                ns['publication_year'] = ns['date_published'].partition(' ')[0]
            return ns


@location('software')
class Software(Collection):
    item_type = 'software'
    schema = load_schema('software.json')
    properties = {
        'title': 'Software',
        'description': 'Software pages',
    }
    item_name_key = "name"
    unique_key = "software:name"
    item_embedded = set(['references'])
    item_keys = ALIAS_KEYS + [
        {'name': '{item_type}:name', 'value': '{name}', '$templated': True},
    ]
