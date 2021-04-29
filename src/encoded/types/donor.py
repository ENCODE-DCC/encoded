from snovault import (
    abstract_collection,
    calculated_property,
    collection,
    load_schema,
)
from snovault.util import Path
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
    schema = load_schema('encoded:schemas/donor.json')
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
        'lab'
    ]
    set_status_up = [
        'characterizations',
        'documents',
    ]
    set_status_down = []
    name_key = 'accession'
    rev = {
        'characterizations': ('DonorCharacterization', 'characterizes')
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
            "linkFrom": "DonorCharacterization.characterizes"
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
        'description': 'Listing Biosample Donors'
    })
class MouseDonor(Donor):
    item_type = 'mouse_donor'
    schema = load_schema('encoded:schemas/mouse_donor.json')
    embedded = Donor.embedded + [
        'genetic_modifications',
        'genetic_modifications.modified_site_by_target_id',
        'genetic_modifications.modified_site_by_target_id.genes',
        'genetic_modifications.treatments'
    ]
    embedded_with_frame = [
        Path('references', exclude=['datasets', 'publication_data']),
    ]
    set_status_up = [
        'characterizations',
        'source',
        'genetic_modifications',
        'parent_strains',
        'documents',
    ]
    set_status_down = []

    def __ac_local_roles__(self):
        # Disallow lab submitter edits
        return {Authenticated: 'role.viewing_group_member'}


@collection(
    name='fly-donors',
    unique_key='accession',
    properties={
        'title': 'Fly donors',
        'description': 'Listing Biosample Donors'
    })
class FlyDonor(Donor):
    item_type = 'fly_donor'
    schema = load_schema('encoded:schemas/fly_donor.json')
    embedded = Donor.embedded + ['organism', 
                                 'genetic_modifications',
                                 'genetic_modifications.modified_site_by_target_id',
                                 'genetic_modifications.modified_site_by_target_id.genes',
                                 'genetic_modifications.treatments', 
                                 'characterizations']
    set_status_up = [
        'characterizations',
        'source',
        'genetic_modifications',
        'parent_strains',
        'documents',
    ]
    set_status_down = []


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
    embedded = Donor.embedded + ['organism',
                                 'genetic_modifications',
                                 'genetic_modifications.modified_site_by_target_id',
                                 'genetic_modifications.modified_site_by_target_id.genes',
                                 'genetic_modifications.treatments']
    set_status_up = [
        'characterizations',
        'source',
        'genetic_modifications',
        'parent_strains',
        'documents',
    ]
    set_status_down = []


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
    embedded = Donor.embedded
    embedded_with_frame = [
        Path('references', exclude=['datasets', 'publication_data']),
    ]
    rev = {
        'children': ('HumanDonor', 'parents'),
        'characterizations': ('DonorCharacterization', 'characterizes')
    }

    @calculated_property(schema={
        "description": "Human donor(s) that have this human donor in their parent property.",
        "comment": "Do not submit. Values in the list are reverse links of a human donors that have this biosample under their parents property.",
        "title": "Children",
        "type": "array",
        "items": {
            "type": ['string', 'object'],
            "linkFrom": "HumanDonor.parents"
        },
        "notSubmittable": True,
    })
    def children(self, request, children):
        return paths_filtered_by_status(request, children)


@collection(
    name='manatee-donors',
    unique_key='accession',
    properties={
        'title': 'Manatee donors',
        'description': 'Listing Biosample Donors',
    })
class ManateeDonor(Donor):
    item_type = 'manatee_donor'
    schema = load_schema('encoded:schemas/manatee_donor.json')
    embedded = Donor.embedded + ['organism',
                                 'genetic_modifications',
                                 'genetic_modifications.modified_site_by_target_id',
                                 'genetic_modifications.modified_site_by_target_id.genes',
                                 'genetic_modifications.treatments']
    set_status_up = [
        'characterizations',
        'source',
        'genetic_modifications',
        'documents',
    ]
    set_status_down = []
