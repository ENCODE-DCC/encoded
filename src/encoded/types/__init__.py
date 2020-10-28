from snovault.attachment import ItemWithAttachment
from snovault import (
    calculated_property,
    collection,
    load_schema,
)
from snovault.util import Path
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
    ]
    set_status_up = [
        'biosamples_used',
        'antibodies_used',
    ]
    set_status_down = []


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
        'biosample.biosample_ontology'
    ]
    set_status_up = [
        'biosample',
        'documents',
        'source',
        'treatments',
    ]
    set_status_down = []
    rev = {'replicates': ('Replicate', 'library')}

    @calculated_property(condition='nucleic_acid_term_name', schema={
        "title": "Nucleic acid term ID",
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
        "title": "Depleted in term ID",
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

    @calculated_property(schema={
        "title": "Replicates",
        "type": "array",
        "uniqueItems": True,
        "items": {
            "type": ['string', 'object'],
            "linkFrom": "Replicate.library",
        },
    })
    def replicates(self, request, replicates):
        return paths_filtered_by_status(request, replicates)

    @calculated_property(condition='replicates', schema={
        "title": "Antibodies",
        "description": "For Immunoprecipitation assays, the antibody used.",
        "comment": "See antibody_lot.json for available identifiers.",
        "type": "array",
        "uniqueItems": True,
        "items": {
            "type": "string",
            "linkTo": "AntibodyLot"
        }
    })
    def antibodies(self, request, replicates):
        antibodies = []
        for rep_id in replicates:
            rep = request.embed(rep_id, '@@object?skip_calculated=true')
            if 'antibody' in rep:
                antibodies.append(rep['antibody'])
        return antibodies or None


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
    rev = {
        'publication_data': ('PublicationData', 'references'),
        'datasets': ('Dataset', 'references')
    }

    def unique_keys(self, properties):
        keys = super(Publication, self).unique_keys(properties)
        if properties.get('identifiers'):
            keys.setdefault('alias', []).extend(properties['identifiers'])
        return keys

    @calculated_property(condition='date_published', schema={
        "title": "Publication year",
        "type": "integer",
    })
    def publication_year(self, date_published):
        likely_year = date_published[:4]
        if likely_year.isdigit():
            return int(date_published[:4])
        else:
            return None

    @calculated_property(schema={
        "title": "Publication Data",
        "type": "array",
        "uniqueItems": True,
        "items": {
            "type": ['string', 'object'],
            "linkFrom": "PublicationData.references",
        },
    })
    def publication_data(self, request, publication_data):
        return paths_filtered_by_status(request, publication_data)

    @calculated_property(condition='datasets', schema={
        "title": "Datasets",
        "description": "The datasets referred to by the publication.",
        "comment": "Do not submit, this is calculated using the references property on dataset objects.",
        "type": "array",
        "uniqueItems": True,
        "notSubmittable": True,
        "items": {
            "type": ['string', 'object'],
            "linkFrom":
                "Dataset.references"
        },
    })
    def datasets(self, request, datasets):
        allowed_dataset_types = ["/experiments/",
                                 "/functional-characterization-experiments/",
                                 "/annotations/", "/references/"]
        filtered = set()
        for d in datasets:
            if d.startswith(tuple(allowed_dataset_types)):
                filtered.add(d)
        return paths_filtered_by_status(request, filtered)


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
        'versions'
    ]
    embedded_with_frame = [
        Path('references', exclude=['datasets', 'publication_data']),
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
    embedded = ['software']
    embedded_with_frame = [
        Path('software.references', exclude=['datasets', 'publication_data']),
    ]
    set_status_up = [
        'software',
    ]
    set_status_down = []

    def __ac_local_roles__(self):
        # Use lab/award from parent software object for access control.
        properties = self.upgrade_properties()
        root = find_root(self)
        software = root.get_by_uuid(properties['software'])
        return software.__ac_local_roles__()
