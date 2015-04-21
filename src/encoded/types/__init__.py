from ..contentbase import (
    calculated_property,
    collection,
)
from ..schema_utils import (
    load_schema,
)
from .base import (
    Item,
    paths_filtered_by_status,
)
from .download import ItemWithAttachment
from pyramid.traversal import (
    find_root,
)


def includeme(config):
    config.scan()


@collection(
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


@collection(
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


@collection(
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


@collection(
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


@collection(
    name='treatments',
    properties={
        'title': 'Treatments',
        'description': 'Listing Biosample Treatments',
    })
class Treatment(Item):
    item_type = 'treatment'
    schema = load_schema('treatment.json')
    # XXX 'treatment_name' as key?


@collection(
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
    embedded = ['target']

    @calculated_property(schema={
        "title": "Characterizations",
        "type": "array",
        "items": {
            "type": "string",
            "linkTo": "construct_characterization",
        },
    })
    def characterizations(self, request, characterizations):
        return paths_filtered_by_status(request, characterizations)


@collection(
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
    embedded = ['lab', 'submitted_by']

    @calculated_property(schema={
        "title": "Characterizations",
        "type": "array",
        "items": {
            "type": "string",
            "linkTo": "construct_characterization",
        },
    })
    def characterizations(self, request, characterizations):
        return paths_filtered_by_status(request, characterizations)


@collection(
    name='documents',
    properties={
        'title': 'Documents',
        'description': 'Listing of Biosample Documents',
    })
class Document(ItemWithAttachment, Item):
    item_type = 'document'
    schema = load_schema('document.json')
    embedded = ['lab', 'award', 'submitted_by']


@collection(
    name='platforms',
    unique_key='platform:term_id',
    properties={
        'title': 'Platforms',
        'description': 'Listing of Platforms',
    })
class Platform(Item):
    item_type = 'platform'
    schema = load_schema('platform.json')
    name_key = 'term_id'

    @calculated_property(schema={
        "title": "Title",
        "type": "string",
    })
    def title(self, term_name):
        return term_name


@collection(
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


@collection(
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

    @calculated_property(schema={
        "title": "Characterizations",
        "type": "array",
        "items": {
            "type": "string",
            "linkTo": "rnai_characterization",
        },
    })
    def characterizations(self, request, characterizations):
        return paths_filtered_by_status(request, characterizations)


@collection(
    name='publications',
    unique_key='publication:identifier',
    properties={
        'title': 'Publications',
        'description': 'Publication pages',
    })
class Publication(Item):
    item_type = 'publication'
    schema = load_schema('publication.json')
    embedded = ['datasets']

    def unique_keys(self, properties):
        keys = super(Publication, self).unique_keys(properties)
        if properties.get('identifiers'):
            keys.setdefault('alias', []).extend(properties['identifiers'])
        return keys

    @calculated_property(condition='date_published', schema={
        "title": "Publication year",
        "type": "string",
    })
    def publication_year(self, date_published):
        return date_published.partition(' ')[0]


@collection(
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
    embedded = [
        'references',
        'versions'
    ]
    rev = {
        'versions': ('software_version', 'software')
    }

    @calculated_property(schema={
        "title": "Versions",
        "type": "array",
        "items": {
            "type": "string",
            "linkTo": "software_version",
        },
    })
    def versions(self, request, versions):
        return paths_filtered_by_status(request, versions)


@collection(
    name='software-versions',
    properties={
        'title': 'Software version',
        'description': 'Software version pages',
    })
class SoftwareVersion(Item):
    item_type = 'software_version'
    schema = load_schema('software_version.json')
    embedded = ['software', 'software.references']
