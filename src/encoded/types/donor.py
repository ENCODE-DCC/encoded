from snovault import (
    abstract_collection,
    calculated_property,
    collection,
    load_schema,
)
from pyramid.security import Authenticated
from .base import (
    Item,
    paths_filtered_by_status,
)


@abstract_collection(
    name='donors',
    unique_key='accession',
    properties={
        'title': "Donors",
        'description': 'Listing of all types of donor.',
    })
class Donor(Item):
    base_types = ['Donor'] + Item.base_types
    embedded = [
        'organism',
        'characterizations',
        'characterizations.award',
        'characterizations.lab',
        'characterizations.submitted_by',
        'documents',
        'documents.award',
        'documents.lab',
        'documents.submitted_by',
        'genetic_modifications',
        'genetic_modifications.award',
        'genetic_modifications.lab',
        'genetic_modifications.modification_techniques',
        'genetic_modifications.treatments',
        'genetic_modifications.modified_target_id'
    ]
    name_key = 'accession'
    rev = {
        'characterizations': ('DonorCharacterization', 'characterizes'),
    }

    def unique_keys(self, properties):
        keys = super(Donor, self).unique_keys(properties)
        if properties.get('status') != 'replaced':
            if 'external_ids' in properties:
                keys.setdefault('alias', []).extend(properties['external_ids'])
        return keys

    @calculated_property(schema={
        "title": "Characterizations",
        "type": "array",
        "items": {
            "type": ['string', 'object'],
            "linkFrom": "DonorCharacterization.characterizes",
        },
    })
    def characterizations(self, request, characterizations):
        return paths_filtered_by_status(request, characterizations)


@collection(
    name='mouse-donors',
    unique_key='accession',
    acl=[],
    properties={
        'title': 'Mouse donors',
        'description': 'Listing Biosample Donors',
    })
class MouseDonor(Donor):
    item_type = 'mouse_donor'
    schema = load_schema('encoded:schemas/mouse_donor.json')
    embedded = Donor.embedded + ['references']

    def __ac_local_roles__(self):
        # Disallow lab submitter edits
        return {Authenticated: 'role.viewing_group_member'}


@collection(
    name='fly-donors',
    unique_key='accession',
    properties={
        'title': 'Fly donors',
        'description': 'Listing Biosample Donors',
    })
class FlyDonor(Donor):
    item_type = 'fly_donor'
    schema = load_schema('encoded:schemas/fly_donor.json')
    embedded = Donor.embedded + ['organism', 'constructs', 'constructs.target', 'characterizations']


@collection(
    name='worm-donors',
    unique_key='accession',
    properties={
        'title': 'Worm donors',
        'description': 'Listing Biosample Donors',
    })
class WormDonor(Donor):
    item_type = 'worm_donor'
    schema = load_schema('encoded:schemas/worm_donor.json')
    embedded = Donor.embedded + ['organism', 'constructs', 'constructs.target']


@collection(
    name='human-donors',
    unique_key='accession',
    properties={
        'title': 'Human donors',
        'description': 'Listing Biosample Donors',
    })
class HumanDonor(Donor):
    item_type = 'human_donor'
    schema = load_schema('encoded:schemas/human_donor.json')
    embedded = Donor.embedded + ['references']
