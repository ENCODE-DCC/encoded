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
    set_status_up = []
    set_status_down = []
    name_key = 'accession'
    rev = {}

    def unique_keys(self, properties):
        keys = super(Donor, self).unique_keys(properties)
        if properties.get('status') != 'replaced':
            if 'external_ids' in properties:
                keys.setdefault('alias', []).extend(properties['external_ids'])
        return keys


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


@abstract_collection(
    name='mouse-donors',
    unique_key='accession',
    properties={
        'title': 'Mouse donors',
        'description': 'Listing Biosample Donors'
    })
class MouseDonor(Donor):
    item_type = 'mouse_donor'
    base_types = ['MouseDonor'] + Donor.base_types
    schema = load_schema('encoded:schemas/mouse_donor.json')
    embedded = Donor.embedded + []


@abstract_collection(
    name='human-donors',
    unique_key='accession',
    properties={
        'title': 'Human donors',
        'description': 'Listing Biosample Donors',
    })
class HumanDonor(Donor):
    item_type = 'human_donor'
    base_types = ['HumanDonor'] + Donor.base_types
    schema = load_schema('encoded:schemas/human_donor.json')
    embedded = Donor.embedded + []


@collection(
    name='mouse-prenatal-donors',
    unique_key='accession',
    properties={
        'title': 'Mouse prenatal donors',
        'description': 'Listing Biosample Donors'
    })
class MousePrenatalDonor(MouseDonor):
    item_type = 'mouse_prenatal_donor'
    schema = load_schema('encoded:schemas/mouse_prenatal_donor.json')
    embedded = Donor.embedded + []


@collection(
    name='mouse-postnatal-donors',
    unique_key='accession',
    properties={
        'title': 'Mouse postnatal donors',
        'description': 'Listing Biosample Donors'
    })
class MousePostnatalDonor(MouseDonor):
    item_type = 'mouse_postnatal_donor'
    schema = load_schema('encoded:schemas/mouse_postnatal_donor.json')
    embedded = Donor.embedded + []


@collection(
    name='human-prenatal-donors',
    unique_key='accession',
    properties={
        'title': 'Human prenatal donors',
        'description': 'Listing Biosample Donors'
    })
class HumanPrenatalDonor(HumanDonor):
    item_type = 'human_prenatal_donor'
    schema = load_schema('encoded:schemas/human_prenatal_donor.json')
    embedded = Donor.embedded + []


@collection(
    name='human-postnatal-donors',
    unique_key='accession',
    properties={
        'title': 'Human postnatal donors',
        'description': 'Listing Biosample Donors'
    })
class HumanPostnatalDonor(HumanDonor):
    item_type = 'human_postnatal_donor'
    schema = load_schema('encoded:schemas/human_postnatal_donor.json')
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


def pluralize(value, value_units):
    try:
        if float(value) == 1:
            return str(value) + ' ' + value_units
        else:
            return str(value) + ' ' + value_units + 's'
    except:
        return str(value) + ' ' + value_units + 's'
