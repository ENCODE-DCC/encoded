from ..schema_utils import (
    load_schema,
)
from ..contentbase import (
    location,
)
from .base import (
    ACCESSION_KEYS,
    ALIAS_KEYS,
    Collection,
    paths_filtered_by_status,
)


class DonorItem(Collection.Item):
    base_types = ['donor'] + Collection.Item.base_types
    embedded = set(['organism'])
    name_key = 'accession'
    keys = ACCESSION_KEYS + ALIAS_KEYS
    rev = {
        'characterizations': ('donor_characterization', 'characterizes'),
    }
    template = {
        'characterizations': (
            lambda root, characterizations: paths_filtered_by_status(root, characterizations)
        ),
    }


@location('mouse-donors')
class MouseDonor(Collection):
    item_type = 'mouse_donor'
    schema = load_schema('mouse_donor.json')
    __acl__ = []
    properties = {
        'title': 'Mouse donors',
        'description': 'Listing Biosample Donors',
    }

    class Item(DonorItem):
        def __ac_local_roles__(self):
            # Disallow lab submitter edits
            return {}


@location('fly-donors')
class FlyDonor(Collection):
    item_type = 'fly_donor'
    schema = load_schema('fly_donor.json')
    properties = {
        'title': 'Fly donors',
        'description': 'Listing Biosample Donors',
    }

    class Item(DonorItem):
        embedded = set(['organism', 'constructs', 'constructs.target'])


@location('worm-donors')
class WormDonor(Collection):
    item_type = 'worm_donor'
    schema = load_schema('worm_donor.json')
    properties = {
        'title': 'Worm donors',
        'description': 'Listing Biosample Donors',
    }

    class Item(DonorItem):
        embedded = set(['organism', 'constructs', 'constructs.target'])


@location('human-donors')
class HumanDonor(Collection):
    item_type = 'human_donor'
    schema = load_schema('human_donor.json')
    properties = {
        'title': 'Human donors',
        'description': 'Listing Biosample Donors',
    }

    class Item(DonorItem):
        pass
