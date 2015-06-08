from contentbase.schema_utils import (
    load_schema,
)
from contentbase import (
    calculated_property,
    collection,
)
from pyramid.security import Authenticated
from .base import (
    Item,
    paths_filtered_by_status,
)


class Donor(Item):
    item_type = 'donor'
    base_types = ['donor'] + Item.base_types
    embedded = ['organism']
    name_key = 'accession'
    rev = {
        'characterizations': ('donor_characterization', 'characterizes'),
    }

    @calculated_property(schema={
        "title": "Characterizations",
        "type": "array",
        "items": {
            "type": ['string', 'object'],
            "linkFrom": "donor_characterization.characterizes",
        },
    })
    def characterizations(self, request, characterizations):
        return paths_filtered_by_status(request, characterizations)


@collection(
    name='human-donors',
    properties={
        'title': 'Human donors',
        'description': 'Listing Biosample Donors',
    })
class HumanDonor(Donor):
    item_type = 'human_donor'
    schema = load_schema('clincoded:schemas/human_donor.json')
