from ..schema_utils import (
    load_schema,
)
from ..contentbase import (
    location,
)
from .base import (
    Item,
    paths_filtered_by_status,
)


class Donor(Item):
    base_types = ['donor'] + Item.base_types
    embedded = ['organism']
    name_key = 'accession'
    rev = {
        'characterizations': ('donor_characterization', 'characterizes'),
    }
    template = Item.template.copy()
    template.update({
        'characterizations': (
            lambda request, characterizations: paths_filtered_by_status(request, characterizations)
        ),
    })


@location(
    name='mouse-donors',
    acl=[],
    properties={
        'title': 'Mouse donors',
        'description': 'Listing Biosample Donors',
    })
class MouseDonor(Donor):
    item_type = 'mouse_donor'
    schema = load_schema('mouse_donor.json')

    def __ac_local_roles__(self):
        # Disallow lab submitter edits
        return {}


@location(
    name='fly-donors',
    properties={
        'title': 'Fly donors',
        'description': 'Listing Biosample Donors',
    })
class FlyDonor(Donor):
    item_type = 'fly_donor'
    schema = load_schema('fly_donor.json')
    embedded = ['organism', 'constructs', 'constructs.target']


@location(
    name='worm-donors',
    properties={
        'title': 'Worm donors',
        'description': 'Listing Biosample Donors',
    })
class WormDonor(Donor):
    item_type = 'worm_donor'
    schema = load_schema('worm_donor.json')
    embedded = ['organism', 'constructs', 'constructs.target']


@location(
    name='human-donors',
    properties={
        'title': 'Human donors',
        'description': 'Listing Biosample Donors',
    })
class HumanDonor(Donor):
    item_type = 'human_donor'
    schema = load_schema('human_donor.json')
