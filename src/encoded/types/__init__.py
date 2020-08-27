from snovault.attachment import ItemWithAttachment
from snovault import (
    CONNECTION,
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
    name='publications',
    unique_key='publication:identifier',
    properties={
        'title': 'Publications',
        'description': 'Publication pages',
    })
class Publication(Item):
    item_type = 'publication'
    schema = load_schema('encoded:schemas/publication.json')
    embedded = []

    def unique_keys(self, properties):
        keys = super(Publication, self).unique_keys(properties)
        if properties.get('identifiers'):
            keys.setdefault('alias', []).extend(properties['identifiers'])
        return keys


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


@collection(
    name='sequencing-runs',
    properties={
        'title': 'Sequencing Runs',
        'description': 'Listing Sequuencing runs',
    })
class SequencingRun(Item):
    item_type = 'sequencing_run'
    schema = load_schema('encoded:schemas/sequencing_run.json')
    rev = {
        'files': ('RawSequenceFile', 'derived_from')
    }

    @calculated_property(schema={
        "title": "Files",
        "type": "array",
        "items": {
            "type": "string",
            "linkTo": "RawSequenceFile",
        },
    })
    def files(self, request, files):
        return paths_filtered_by_status(request, files)

    @calculated_property(schema={
            "title": "Read 1 file",
            "type": "string",
            "linkFrom": "RawSequenceFile.derived_from",
            "notSubmittable": True,
    })
    def read_1_file(self, request, registry, files):
        conn = registry[CONNECTION]
        for file_id in files:
            file_obj = request.embed(file_id, '@@object')
            read_type = file_obj.get('read_type')
            if read_type == 'Read 1':
                return file_obj['accession']

    @calculated_property(schema={
            "title": "Read 2 file",
            "type": "string",
            "linkFrom": "RawSequenceFile.derived_from",
            "notSubmittable": True,
    })
    def read_2_file(self, request, registry, files):
        conn = registry[CONNECTION]
        for file_id in files:
            file_obj = request.embed(file_id, '@@object')
            read_type = file_obj.get('read_type')
            if read_type == 'Read 2':
                return file_obj['accession']

    @calculated_property(schema={
            "title": "Read 1N file",
            "type": "string",
            "linkFrom": "RawSequenceFile.derived_from",
            "notSubmittable": True,
    })
    def read_1N_file(self, request, registry, files):
        conn = registry[CONNECTION]
        for file_id in files:
            file_obj = request.embed(file_id, '@@object')
            read_type = file_obj.get('read_type')
            if read_type == 'Read 1N':
                return file_obj['accession']

    @calculated_property(schema={
            "title": "Read 2N file",
            "type": "string",
            "linkFrom": "RawSequenceFile.derived_from",
            "notSubmittable": True,
    })
    def read_2N_file(self, request, registry, files):
        conn = registry[CONNECTION]
        for file_id in files:
            file_obj = request.embed(file_id, '@@object')
            read_type = file_obj.get('read_type')
            if read_type == 'Read 2N':
                return file_obj['accession']

    @calculated_property(schema={
            "title": "i5 index file",
            "type": "string",
            "linkFrom": "RawSequenceFile.derived_from",
            "notSubmittable": True,
    })
    def i5_index_file(self, request, registry, files):
        conn = registry[CONNECTION]
        for file_id in files:
            file_obj = request.embed(file_id, '@@object')
            read_type = file_obj.get('read_type')
            if read_type == 'i5 index':
                return file_obj['accession']

    @calculated_property(schema={
            "title": "i7 index file",
            "type": "string",
            "linkFrom": "RawSequenceFile.derived_from",
            "notSubmittable": True,
    })
    def i7_index_file(self, request, registry, files):
        conn = registry[CONNECTION]
        for file_id in files:
            file_obj = request.embed(file_id, '@@object')
            read_type = file_obj.get('read_type')
            if read_type == 'i7 index':
                return file_obj['accession']
