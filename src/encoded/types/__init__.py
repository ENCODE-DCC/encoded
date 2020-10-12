from snovault.attachment import ItemWithAttachment
from snovault import (
    collection,
    load_schema,
)
from .base import (
    Item,
    ALLOW_CURRENT,
    DELETED,
)


def includeme(config):
    config.scan()
    config.add_request_method(lambda request: set(), '_set_status_changed_paths', reify=True)
    config.add_request_method(lambda request: set(), '_set_status_considered_paths', reify=True)


@collection(
    name='library-protocols',
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
    STATUS_ACL = {
        'current': ALLOW_CURRENT,
        'deleted': DELETED,
        'replaced': DELETED,
        'disabled': ALLOW_CURRENT
    }
    embedded = [
        'principal_investigators',
        'collaborators'
    ]


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


@collection(
    name='documents',
    properties={
        'title': 'Documents',
        'description': 'Listing of Biosample Documents',
    })
class Document(ItemWithAttachment, Item):
    item_type = 'document'
    schema = load_schema('encoded:schemas/document.json')


@collection(
    name='antibody-lots',
    unique_key='accession',
    properties={
        'title': 'Antibody lot',
        'description': 'Listing of ENCODE antibodies',
    })
class AntibodyLot(Item):
    item_type = 'antibody_lot'
    schema = load_schema('encoded:schemas/antibody_lot.json')
    name_key = 'accession'
    rev = {}
    embedded = [
        'host_organism'
    ]
