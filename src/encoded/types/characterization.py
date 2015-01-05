from ..schema_utils import (
    load_schema,
)
from ..contentbase import (
    location,
)
from .base import (
    Item,
)
from .download import ItemWithAttachment


class Characterization(ItemWithAttachment, Item):
    base_types = ['characterization'] + Item.base_types
    embedded = ['lab', 'award', 'submitted_by']


@location(
    name='construct-characterizations',
    properties={
        'title': 'Construct characterizations',
        'description': 'Listing of biosample construct characterizations',
    })
class ConstructCharacterization(Characterization):
    item_type = 'construct_characterization'
    schema = load_schema('construct_characterization.json')


@location(
    name='rnai-characterizations',
    properties={
        'title': 'RNAi characterizations',
        'description': 'Listing of biosample RNAi characterizations',
    })
class RNAiCharacterization(Characterization):
    item_type = 'rnai_characterization'
    schema = load_schema('rnai_characterization.json')


@location(
    name='donor-characterizations',
    properties={
        'title': 'Donor characterizations',
        'description': 'Listing of model organism donor (strain) construct characterizations',
    })
class DonorCharacterization(Characterization):
    item_type = 'donor_characterization'
    schema = load_schema('donor_characterization.json')


@location(
    name='biosample-characterizations',
    properties={
        'title': 'Biosample characterizations',
        'description': 'Listing of biosample characterizations',
    })
class BiosampleCharacterization(Characterization):
    item_type = 'biosample_characterization'
    schema = load_schema('biosample_characterization.json')


@location(
    name='antibody-characterizations',
    properties={
        'title': 'Antibody characterizations',
        'description': 'Listing of antibody characterization documents',
    })
class AntibodyCharacterization(Characterization):
    item_type = 'antibody_characterization'
    schema = load_schema('antibody_characterization.json')
    embedded = [
        'submitted_by',
        'lab',
        'award',
        'target',
        'target.organism',
        'documents',
        'characterizes.targets',
    ]
    namespace_from_path = {
        'characterization_method': [
            'primary_characterization_method',
            'secondary_characterization_method',
        ],
    }
    template = {
        'characterization_method': {
            '$value': '{characterization_method}',
            '$condition': 'characterization_method',
        },
    }
