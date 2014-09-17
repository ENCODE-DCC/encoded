from ..schema_utils import (
    load_schema,
)
from ..contentbase import (
    location,
)
from .base import (
    ADD_ACTION,
    Collection,
)
from .download import ItemWithAttachment


@location('images')
class Image(Collection):
    item_type = 'image'
    schema = load_schema('image.json')
    schema['properties']['attachment']['properties']['type']['enum'] = [
        'image/png',
        'image/jpeg',
        'image/gif',
    ]
    properties = {
        'title': 'Image',
        'description': 'Listing of portal images',
    }
    unique_key = 'image:filename'
    template = {
        'actions': [ADD_ACTION],
    }

    class Item(ItemWithAttachment, Collection.Item):
        embedded = ['submitted_by']
        keys = [
            {
                'name': 'image:filename',
                'value': "{attachment[download]}",
                '$templated': True,
            },
        ]
