from snovault import (
    collection,
    load_schema,
)
from .base import (
    Item,
    ALLOW_EVERYONE_VIEW,
    ONLY_ADMIN_VIEW
)
from snovault.attachment import ItemWithAttachment


@collection(
    name='images',
    unique_key='image:filename',
    properties={
        'title': 'Image',
        'description': 'Listing of portal images',
    })
class Image(ItemWithAttachment, Item):
    item_type = 'image'
    schema = load_schema('encoded:schemas/image.json')
    schema['properties']['attachment']['properties']['type']['enum'] = [
        'image/png',
        'image/jpeg',
        'image/gif',
    ]

    STATUS_ACL = {
        'released': ALLOW_EVERYONE_VIEW,
        'in progress': ONLY_ADMIN_VIEW,
        'deleted': ONLY_ADMIN_VIEW
    }

    def unique_keys(self, properties):
        keys = super(Image, self).unique_keys(properties)
        value = properties['attachment']['download']
        keys.setdefault('image:filename', []).append(value)
        return keys
