from snovault.attachment import ItemWithAttachment
from snovault import (
    calculated_property,
    collection,
    load_schema,
)
from pyramid.traversal import find_root
from .base import (
    Item,
    paths_filtered_by_status,
    ALLOW_CURRENT,
    DELETED,
)


def includeme(config):
    config.scan()
    config.add_request_method(lambda request: set(), '_set_status_changed_paths', reify=True)
    config.add_request_method(lambda request: set(), '_set_status_considered_paths', reify=True)


@collection(
    name='library_protocols',
    unique_key='library_protocol:name',
    properties={
        'title': 'Library protocols',
        'description': 'Listing of Library protocols',
    })
class LibraryProtocol(Item):
    item_type = 'library_protocol'
    schema = load_schema('encoded:schemas/library_protocol.json')
    name_key = 'name'


@collection(
    name='labs',
    unique_key='lab:name',
    properties={
        'title': 'Labs',
        'description': 'Listing of ENCODE DCC labs',
    })
class Lab(Item):
    item_type = 'lab'
    schema = load_schema('encoded:schemas/lab.json')
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
    schema = load_schema('encoded:schemas/award.json')
    name_key = 'name'
    embedded = []
    STATUS_ACL = {
        'current': ALLOW_CURRENT,
        'deleted': DELETED,
        'replaced': DELETED,
        'disabled': ALLOW_CURRENT
    }


@collection(
    name='organisms',
    unique_key='organism:name',
    properties={
        'title': 'Organisms',
        'description': 'Listing of all registered organisms',
    })
class Organism(Item):
    item_type = 'organism'
    schema = load_schema('encoded:schemas/organism.json')
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
    schema = load_schema('encoded:schemas/source.json')
    name_key = 'name'


@collection(
    name='treatments',
    properties={
        'title': 'Treatments',
        'description': 'Listing Biosample Treatments',
    })
class Treatment(Item):
    item_type = 'treatment'
    schema = load_schema('encoded:schemas/treatment.json')
    embedded = []
    set_status_up = [
        'biosamples_used',
        'antibodies_used',
    ]
    set_status_down = []


@collection(
    name='analysis_step',
    properties={
        'title': 'Analysis Steps',
        'description': 'Listing of Analysis Steps',
    })
class AnalysisStep(Item):
    item_type = 'analysis_step'
    schema = load_schema('encoded:schemas/analysis_step.json')
    embedded = []


@collection(
    name='documents',
    properties={
        'title': 'Documents',
        'description': 'Listing of Biosample Documents',
    })
class Document(ItemWithAttachment, Item):
    item_type = 'document'
    schema = load_schema('encoded:schemas/document.json')
    embedded = ['submitted_by']


@collection(
    name='platforms',
    unique_key='platform:term_id',
    properties={
        'title': 'Platforms',
        'description': 'Listing of Platforms',
    })
class Platform(Item):
    item_type = 'platform'
    schema = load_schema('encoded:schemas/platform.json')
    name_key = 'term_id'

    @calculated_property(schema={
        "title": "Title",
        "type": "string",
    })
    def title(self, term_name):
        return term_name


@collection(
    name='publications',
    unique_key='publication:identifier',
    properties={
        'title': 'Publications',
        'description': 'Publication pages',
    })
class Publication(Item):
    item_type = 'publication'
    schema = load_schema('encoded:schemas/publication.json')
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
    schema = load_schema('encoded:schemas/software.json')
    name_key = 'name'
    embedded = [
        'references',
        'versions'
    ]
    rev = {
        'versions': ('SoftwareVersion', 'software')
    }

    @calculated_property(schema={
        "title": "Versions",
        "type": "array",
        "items": {
            "type": "string",
            "linkTo": "SoftwareVersion",
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
    schema = load_schema('encoded:schemas/software_version.json')
    embedded = ['software', 'software.references']

    def __ac_local_roles__(self):
        # Use lab/award from parent software object for access control.
        properties = self.upgrade_properties()
        root = find_root(self)
        software = root.get_by_uuid(properties['software'])
        return software.__ac_local_roles__()
