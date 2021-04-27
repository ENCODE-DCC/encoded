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
        'organism'
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
    def age_display(self, request, age=None, age_units=None, gestational_age=None, gestational_age_units=None):
        if age != None and age_units !=None:
            if age == 'unknown':
                return 'unknown'
            else:
                return u'{}'.format(pluralize(age, age_units))
        elif gestational_age != None and gestational_age_units !=None:
            if gestational_age == 'unknown':
                return 'unknown'
            else:
                return u'{} (gestational)'.format(pluralize(gestational_age, gestational_age_units))
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


    @calculated_property(condition='life_stage', schema={
        "title": "Life stage term ID",
        "description": "The ontology term ID for the life stage of the donor.",
        "comment": "Do not submit. This is a calculated property",
        "type": "string",
    })
    def life_stage_term_id(self, request, life_stage):
        term_lookup = {
            'embryonic': 'MmusDv:0000002',
            'fetal': 'MmusDv:0000031',
            'newborn': 'MmusDv:0000036',
            'premature': 'MmusDv:0000112',
            'adult': 'MmusDv:0000110'
        }
        term_id = None
        if life_stage in term_lookup:
            term_id = term_lookup.get(life_stage)
        return term_id


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


    @calculated_property(condition='life_stage', schema={
        "title": "Life stage term ID",
        "description": "The ontology term ID for the life stage of the donor.",
        "comment": "Do not submit. This is a calculated property",
        "type": "string",
    })
    def life_stage_term_id(self, request, life_stage):
        term_lookup = {
            'embryonic': 'HsapDv:0000002',
            'fetal': 'HsapDv:0000037',
            'newborn': 'HsapDv:0000082',
            'infant': 'HsapDv:0000083',
            'child': 'HsapDv:0000081',
            'adolescent': 'HsapDv:0000086',
            'adult': 'HsapDv:0000087'
        }
        term_id = None
        if life_stage in term_lookup:
            term_id = term_lookup.get(life_stage)
        return term_id


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
