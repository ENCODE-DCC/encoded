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
        'documents',
        'documents.submitted_by'
    ]
    set_status_up = [
        'documents',
    ]
    set_status_down = []
    name_key = 'accession'
    rev = {}

    def unique_keys(self, properties):
        keys = super(Donor, self).unique_keys(properties)
        if properties.get('status') != 'replaced':
            if 'external_ids' in properties:
                keys.setdefault('alias', []).extend(properties['external_ids'])
        return keys


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
    embedded = Donor.embedded + ['genetic_modifications',
                                 'genetic_modifications.modified_site_by_target_id',
                                 'genetic_modifications.modified_site_by_target_id.genes',
                                 'genetic_modifications.treatments']
    set_status_up = [
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
    name='human-donors',
    unique_key='accession',
    properties={
        'title': 'Human donors',
        'description': 'Listing Biosample Donors',
    })
class HumanDonor(Donor):
    item_type = 'human_donor'
    schema = load_schema('encoded:schemas/human_donor.json')
    embedded = Donor.embedded + []
    rev = {
        'children': ('HumanDonor', 'parents')
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


    @calculated_property(define=True,
                        schema={
                        "title": "Age display",
                        "type": "string"})
    def age_display(self, request, age=None, age_units=None):
        if age != None and age_units !=None:
            if age == 'unknown':
                return 'unknown'
            else:
                return u'{}'.format(pluralize(age, age_units))
        else:
            return None


def pluralize(value, value_units):
    try:
        if float(value) == 1:
            return str(value) + ' ' + value_units
        else:
            return str(value) + ' ' + value_units + 's'
    except:
        return str(value) + ' ' + value_units + 's'
