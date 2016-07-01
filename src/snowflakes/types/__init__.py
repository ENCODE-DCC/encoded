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
)


def includeme(config):
    config.scan()


@collection(
    name='labs',
    unique_key='lab:name',
    properties={
        'title': 'Labs',
        'description': 'Listing of Snowflake labs',
    })
class Lab(Item):
    item_type = 'lab'
    schema = load_schema('snowflakes:schemas/lab.json')
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
    schema = load_schema('snowflakes:schemas/award.json')
    name_key = 'name'
    embedded = ['pi']
