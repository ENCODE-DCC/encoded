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
    embedded = ['awards']


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
    embedded = ['pi.lab']
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
    embedded = [
        'lab',
    ]


@collection(
    name='constructs',
    properties={
        'title': 'Constructs',
        'description': 'Listing of Biosample Constructs',
    })
class Construct(Item):
    item_type = 'construct'
    schema = load_schema('encoded:schemas/construct.json')
    # XXX 'vector_name' as key?
    embedded = ['target']


@collection(
    name='talens',
    unique_key='talen:name',
    properties={
        'title': 'TALENs',
        'description': 'Listing of TALEN Constructs',
    })
class TALEN(Item):
    item_type = 'talen'
    schema = load_schema('encoded:schemas/talen.json')
    name_key = 'name'
    rev = {
        'characterizations': ('ConstructCharacterization', 'characterizes'),
    }
    embedded = [
        'lab',
        'submitted_by',
        'documents',
        'documents.award',
        'documents.lab',
        'documents.submitted_by'
    ]

    @calculated_property(schema={
        "title": "Characterizations",
        "type": "array",
        "items": {
            "type": "string",
            "linkTo": "ConstructCharacterization",
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
    schema = load_schema('encoded:schemas/document.json')
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
    schema = load_schema('encoded:schemas/platform.json')
    name_key = 'term_id'

    @calculated_property(schema={
        "title": "Title",
        "type": "string",
    })
    def title(self, term_name):
        return term_name


@collection(
    name='libraries',
    unique_key='accession',
    properties={
        'title': 'Libraries',
        'description': 'Listing of Libraries',
    })
class Library(Item):
    item_type = 'library'
    schema = load_schema('encoded:schemas/library.json')
    name_key = 'accession'
    embedded = [
        'biosample',
        'biosample.donor',
        'biosample.donor.organism',
    ]

    @calculated_property(condition='nucleic_acid_term_name', schema={
        "title": "nucleic_acid_term_id",
        "type": "string",
    })
    def nucleic_acid_term_id(self, request, nucleic_acid_term_name):
        term_lookup = {
            'DNA': 'SO:0000352',
            'RNA': 'SO:0000356',
            'polyadenylated mRNA': 'SO:0000871',
            'miRNA': 'SO:0000276',
            'protein': 'SO:0000104'
        }
        term_id = None
        if nucleic_acid_term_name in term_lookup:
            term_id = term_lookup.get(nucleic_acid_term_name)
        return term_id

    @calculated_property(condition='depleted_in_term_name', schema={
        "title": "depleted_in_term_id",
        "type": "string",
    })
    def depleted_in_term_id(self, request, depleted_in_term_name):
        term_lookup = {
            'rRNA': 'SO:0000252',
            'polyadenylated mRNA': 'SO:0000871',
            'capped mRNA': 'SO:0000862'
        }
        term_id = list()
        for term_name in depleted_in_term_name:
            if term_name in term_lookup:
                term_id.append(term_lookup.get(term_name))
            else:
                term_id.append('Term ID unknown')
        return term_id


@collection(
    name='rnais',
    properties={
        'title': 'RNAi',
        'description': 'Listing of RNAi',
    })
class RNAi(Item):
    item_type = 'rnai'
    schema = load_schema('encoded:schemas/rnai.json')
    embedded = ['source', 'documents', 'target']


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
