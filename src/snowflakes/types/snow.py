from snovault import (
    abstract_collection,
    calculated_property,
    collection,
    load_schema,
)
from .base import (
    Item,
    paths_filtered_by_status,
)


import datetime


def item_is_revoked(request, path):
    return request.embed(path, '@@object').get('status') == 'revoked'


@abstract_collection(
    name='snowsets',
    unique_key='accession',
    properties={
        'title': "Snowsets",
        'description': 'Abstract class describing different collections of snowflakes.',
    })
class Snowset(Item):
    base_types = ['Snowset'] + Item.base_types
    embedded = [
        'snowflakes',
        'snowflakes.submitted_by',
        'snowflakes.lab',
        'submitted_by',
        'lab',
        'award',
    ]
    audit_inherit = [
        'snowflakes',
        'submitted_by',
        'lab',
        'award',
    ]
    name_key = 'accession'
    rev = {
        'snowflakes': ('Snowflake', 'snowset'),
    }

    @calculated_property(condition='date_released', schema={
        "title": "Month released",
        "type": "string",
    })
    def month_released(self, date_released):
        return datetime.datetime.strptime(date_released, '%Y-%m-%d').strftime('%B, %Y')

    @calculated_property(schema={
        "title": "snowflakes",
        "type": "array",
        "items": {
            "type": ['string', 'object'],
            "linkFrom": "Snowflake.snowset",
        },
    })
    def snowflakes(self, request, snowflakes):
        return paths_filtered_by_status(request, snowflakes)


@collection(
    name='snowballs',
    unique_key='accession',
    properties={
        'title': "Snowball style snowset",
        'description': 'A set of snowflakes packed into a snowball.',
    })
class Snowball(Snowset):
    item_type = 'snowball'
    schema = load_schema('snowflakes:schemas/snowball.json')


@collection(
    name='snowforts',
    unique_key='accession',
    properties={
        'title': "Snowfort style snowset",
        'description': 'A set of snowflakes packed into a snowfort.',
    })
class Snowfort(Snowset):
    item_type = 'snowfort'
    schema = load_schema('snowflakes:schemas/snowfort.json')


@collection(
    name='snowflakes',
    unique_key='accession',
    properties={
        'title': 'Snowflakes',
        'description': 'Listing of Snowflakes',
    })
class Snowflake(Item):
    item_type = 'snowflake'
    schema = load_schema('snowflakes:schemas/snowflake.json')
    name_key = 'accession'

    embedded = [
        'lab',
        'submitted_by',

    ]
    audit_inherit = [
        'lab',
        'submitted_by',

    ]
