from ..contentbase import (
    location
)
from ..schema_utils import (
    load_schema,
)
from .base import (
    Item,
    paths_filtered_by_status,
)
from .download import ItemWithAttachment


def includeme(config):
    config.scan()


@location(
    name='labs',
    unique_key='lab:name',
    properties={
        'title': 'Labs',
        'description': 'Listing of ENCODE DCC labs',
    })
class Lab(Item):
    item_type = 'lab'
    schema = load_schema('lab.json')
    name_key = 'name'


@location(
    name='awards',
    unique_key='award:name',
    properties={
        'title': 'Awards (Grants)',
        'description': 'Listing of awards (aka grants)',
    })
class Award(Item):
    item_type = 'award'
    schema = load_schema('award.json')
    name_key = 'name'


@location(
    name='organisms',
    unique_key='organism:name',
    properties={
        'title': 'Organisms',
        'description': 'Listing of all registered organisms',
    })
class Organism(Item):
    item_type = 'organism'
    schema = load_schema('organism.json')
    name_key = 'name'


@location(
    name='sources',
    unique_key='source:name',
    properties={
        'title': 'Sources',
        'description': 'Listing of sources and vendors for ENCODE material',
    })
class Source(Item):
    item_type = 'source'
    schema = load_schema('source.json')
    name_key = 'name'


@location(
    name='treatments',
    properties={
        'title': 'Treatments',
        'description': 'Listing Biosample Treatments',
    })
class Treatment(Item):
    item_type = 'treatment'
    schema = load_schema('treatment.json')
    # XXX 'treatment_name' as key?


@location(
    name='constructs',
    properties={
        'title': 'Constructs',
        'description': 'Listing of Biosample Constructs',
    })
class Construct(Item):
    item_type = 'construct'
    schema = load_schema('construct.json')
    # XXX 'vector_name' as key?
    rev = {
        'characterizations': ('construct_characterization', 'characterizes'),
    }
    template = {
        'characterizations': (
            lambda request, characterizations: paths_filtered_by_status(request, characterizations)
        ),
    }
    embedded = ['target']


@location(
    name='talens',
    unique_key='talen:name',
    properties={
        'title': 'TALENs',
        'description': 'Listing of TALEN Constructs',
    })
class Talen(Item):
    item_type = 'talen'
    schema = load_schema('talen.json')
    name_key = 'name'
    rev = {
        'characterizations': ('construct_characterization', 'characterizes'),
    }
    template = {
        'characterizations': (
            lambda request, characterizations: paths_filtered_by_status(request, characterizations)
        ),
    }
    embedded = ['lab', 'submitted_by']


@location(
    name='documents',
    properties={
        'title': 'Documents',
        'description': 'Listing of Biosample Documents',
    })
class Document(ItemWithAttachment, Item):
    item_type = 'document'
    schema = load_schema('document.json')
    embedded = ['lab', 'award', 'submitted_by']


@location(
    name='platforms',
    unique_key='platform:term_id',
    properties={
        'title': 'Platforms',
        'description': 'Listing of Platforms',
    })
class Platform(Item):
    item_type = 'platform'
    schema = load_schema('platform.json')
    template = {
        'title': '{term_name}',
        '$templated': True,
    }
    name_key = 'term_id'


@location(
    name='libraries',
    properties={
        'title': 'Libraries',
        'description': 'Listing of Libraries',
    })
class Library(Item):
    item_type = 'library'
    schema = load_schema('library.json')
    embedded = ['biosample']
    name_key = 'accession'


@location(
    name='rnais',
    properties={
        'title': 'RNAi',
        'description': 'Listing of RNAi',
    })
class RNAi(Item):
    item_type = 'rnai'
    schema = load_schema('rnai.json')
    embedded = ['source', 'documents', 'target']
    rev = {
        'characterizations': ('rnai_characterization', 'characterizes'),
    }
    template = {
        'characterizations': (
            lambda request, characterizations: paths_filtered_by_status(request, characterizations)
        ),
    }


@location(
    name='publications',
    unique_key='publication:title',
    properties={
        'title': 'Publications',
        'description': 'Publication pages',
    })
class Publication(Item):
    item_type = 'publication'
    schema = load_schema('publication.json')
    template = {
        'publication_year': {
            '$value': lambda date_published: date_published.partition(' ')[0],
            '$condition': 'date_published',
        },
    }
    embedded = ['datasets']

    # XXX the references mixin is only a key for this type
    # Should probably become 'identifiers' for publication
    template_keys = [
        {
            'name': '{item_type}:reference',
            'value': '{reference}',
            '$repeat': 'reference references',
            '$templated': True,
            '$condition': 'references',
        },
    ]


@location(
    name='software',
    unique_key='software:name',
    properties={
        'title': 'Software',
        'description': 'Software pages',
    })
class Software(Item):
    item_type = 'software'
    schema = load_schema('software.json')
    name_key = 'name'
    embedded = ['references']
