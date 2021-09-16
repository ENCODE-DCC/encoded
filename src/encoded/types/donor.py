from snovault import (
    abstract_collection,
    calculated_property,
    collection,
    load_schema,
)
from .base import (
    Item,
    paths_filtered_by_status,
)
from .shared_calculated_properties import (
    CalculatedTreatmentSummary,
)


@abstract_collection(
    name='donors',
    unique_key='accession',
    properties={
        'title': "Donors",
        'description': 'Listing of all types of donor.',
    })
class Donor(Item, CalculatedTreatmentSummary):
    base_types = ['Donor'] + Item.base_types
    embedded = [
        'diseases',
        'organism',
        'development_ontology'
    ]
    name_key = 'accession'

    def unique_keys(self, properties):
        keys = super(Donor, self).unique_keys(properties)
        if properties.get('status') != 'replaced':
            if 'external_ids' in properties:
                keys.setdefault('alias', []).extend(properties['external_ids'])
        return keys


    @calculated_property(define=True,
                        schema={
                        "title": "Age display",
                        "description": "The age and age units of the donor.",
                        "comment": "Do not submit. This is a calculated property",
                        "type": "string"})
    def age_display(self, request, age=None, age_units=None, conceptional_age=None, conceptional_age_units=None):
        if age == 'unknown' or conceptional_age == 'unknown':
            return 'unknown'
        elif age != None:
            return u'{}'.format(pluralize(age, age_units))
        elif conceptional_age != None:
            return u'{} (post-conception)'.format(pluralize(conceptional_age, conceptional_age_units))
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


    @calculated_property(schema={
        "title": "Organism",
        "description": "Common name of donor organism.",
        "comment": "Do not submit. This is a calculated property",
        "permission": "import_items",
        "type": "string",
        "linkTo": "Organism"
    })
    def organism(self):
        return "/organism/mouse"


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
    embedded = Donor.embedded + ['ethnicity']


    @calculated_property(schema={
        "title": "Organism",
        "description": "Common name of donor organism.",
        "comment": "Do not submit. This is a calculated property",
        "permission": "import_items",
        "type": "string",
        "linkTo": "Organism"
    })
    def organism(self):
        return "/organism/human"


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
    embedded = MouseDonor.embedded + []


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
    embedded = MouseDonor.embedded + []


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
    embedded = HumanDonor.embedded + []


    @calculated_property(schema={
        "title": "Age development stage redunancy",
        "description": "If true, the development_ontology term exactly defines the age.",
        "comment": "Do not submit. This is a calculated property",
        "permission": "import_items",
        "type": "boolean"
    })
    def age_development_stage_redundancy(self):
        return False


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
    embedded = HumanDonor.embedded + []
    rev = {
        'children': ('HumanDonor', 'parents')
    }

    @calculated_property(schema={
        "description": "Whether or not there is a family history of breast cancer for this Donor.",
        "comment": "Do not submit. This is a calculated property",
        "title": "Family history breast cancer",
        "type": "boolean",
        "notSubmittable": True,
    })
    def family_history_breast_cancer(self, request, family_members_history_breast_cancer=None):
        if family_members_history_breast_cancer:
            if family_members_history_breast_cancer == ["none"]:
                return False
            else:
                return True


    @calculated_property(schema={
        "title": "Age development stage redunancy",
        "description": "If true, the development_ontology term exactly defines the age.",
        "comment": "Do not submit. This is a calculated property",
        "permission": "import_items",
        "type": "boolean"
    })
    def age_development_stage_redundancy(self, age, age_units=None):
        if age != 'unknown' and '-' not in age and '>' not in age:
            if age_units == 'year':
                return True
            elif age_units == 'month' and int(age) > 24:
                return True

        return False


    @calculated_property(schema={
        "description": "Human donor(s) that have this human donor in their parent property.",
        "comment": "Do not submit. This is a calculated property",
        "title": "Children",
        "type": "array",
        "items": {
            "type": ['string', 'object'],
            "linkFrom": "HumanDonor.parents"
        },
        "notSubmittable": True,
    })
    def children(self, request, children=None):
        if children:
            return paths_filtered_by_status(request, children)


def pluralize(value, value_units):
    try:
        if float(value) == 1:
            return str(value) + ' ' + value_units
        else:
            return str(value) + ' ' + value_units + 's'
    except:
        return str(value) + ' ' + value_units + 's'
