from pyramid.view import (
    view_config,
)
from pyramid.security import (
    Allow,
    Deny,
    Everyone,
)
from pyramid.traversal import find_root
from snovault import (
    calculated_property,
    collection,
    load_schema,
)
from .base import (
    Item,
    SharedItem,
    paths_filtered_by_status,
)
from snovault.resource_views import item_view_object
from snovault.util import expand_path
from collections import defaultdict


ONLY_ADMIN_VIEW_DETAILS = [
    (Allow, 'group.admin', ['view', 'view_details', 'edit']),
    (Allow, 'group.read-only-admin', ['view', 'view_details']),
    (Allow, 'remoteuser.INDEXER', ['view']),
    (Allow, 'remoteuser.EMBED', ['view']),
    (Deny, Everyone, ['view', 'view_details', 'edit']),
]

USER_ALLOW_CURRENT = [
    (Allow, Everyone, 'view'),
] + ONLY_ADMIN_VIEW_DETAILS

USER_DELETED = [
    (Deny, Everyone, 'visible_for_edit')
] + ONLY_ADMIN_VIEW_DETAILS


def group_values_by_lab(request, labs):
    values_by_key = defaultdict(list)
    for path in labs:
        properties = request.embed(path, '@@object?skip_calculated=true')
        values_by_key[properties.get('lab')].append(properties)
    return dict(values_by_key)


def group_values_by_vital(request, vitals):
    values_by_key = defaultdict(list)
    for path in vitals:
        properties = request.embed(path, '@@object?skip_calculated=true')
        values_by_key[properties.get('vital')].append(properties)
    return dict(values_by_key)


def supportive_med_frequency(request, supportive_medication):
    frequency_by_key = defaultdict(list)
    supportive_meds = []
    for path in supportive_medication:
        properties = request.embed(path, '@@object?skip_calculated=true')
        start_date = properties.get('start_date')
        frequency_by_key[properties.get('name')].append(start_date)

    for k, v in frequency_by_key.items():
        med_freq = {}
        med_freq['name'] = k
        med_freq['start_date'] = min(v)
        med_freq['frequency'] = len(v)
        supportive_meds.append(med_freq)
    return supportive_meds


@collection(
     name='patients',
     unique_key='accession',
     properties={
         'title': 'Patients',
         'description': 'Listing Patients',
})
class Patient(Item):
    item_type = 'patient'
    schema = load_schema('encoded:schemas/patient.json')
    name_key = 'accession'
    embedded = [
        'labs',
        'vitals',
        'germline',
        'consent',
        'radiation',
        'medical_imaging',
        'medications',
        'supportive_medications'
    ]
    rev = {
        'labs': ('LabResult', 'patient'),
        'vitals': ('VitalResult', 'patient'),
        'germline': ('Germline', 'patient'),
        'consent': ('Consent', 'patient'),
        'radiation': ('Radiation', 'patient'),
        'medical_imaging': ('MedicalImaging', 'patient'),
        'medication': ('Medication', 'patient'),
        'supportive_medication': ('SupportiveMedication', 'patient'),
    }
    set_status_up = []
    set_status_down = []

    @calculated_property( schema={
        "title": "Labs",
        "type": "array",
        "items": {
            "type": "string",
            "linkTo": "LabResult",
        },
    })
    def labs(self, request, labs):
        return group_values_by_lab(request, labs)

    @calculated_property( schema={
        "title": "Vitals",
        "type": "array",
        "items": {
            "type": "string",
            "linkTo": "VitalResult",
        },
    })
    def vitals(self, request, vitals):
        return group_values_by_vital(request, vitals)

    @calculated_property(schema={
        "title": "Germline Mutations",
        "type": "array",
        "items": {
            "type": 'string',
            "linkTo": "Germline"
        },
    })
    def germline(self, request, germline):
        return paths_filtered_by_status(request, germline)

    @calculated_property(condition='germline', schema={
        "title": "Positive Germline Mutations",
        "type": "array",
        "items": {
            "type": "string",
        },
    })
    def germline_summary(self, request, germline):
        germline_summary = []
        for mutation in germline:
            mutatation_object = request.embed(mutation, '@@object')
            if mutatation_object['significance'] in ['Positive', 'Variant', 'Positive and Variant']:
                mutation_summary = mutatation_object['target']
                germline_summary.append(mutation_summary)
        return germline_summary


    @calculated_property(schema={
        "title": "Radiation Treatment",
        "type": "array",
        "items": {
            "type": 'string',
            "linkTo": "Radiation"
        },
    })
    def radiation(self, request, radiation):
        return paths_filtered_by_status(request, radiation)

    @calculated_property(schema={
        "title": "Medical Imaging",
        "type": "array",
        "items": {
            "type": 'string',
            "linkTo": "MedicalImaging"
        },
    })
    def medical_imaging(self, request, medical_imaging):
        return paths_filtered_by_status(request, medical_imaging)


    @calculated_property(schema={
        "title": "Consent",
        "type": "array",
        "items": {
            "type": 'string',
            "linkTo": "Consent"
        },
    })
    def consent(self, request, consent):
        return paths_filtered_by_status(request, consent)

    @calculated_property( schema={
        "title": "Medications",
        "type": "array",
        "items": {
            "type": "string",
            "linkTo": "Medication",
        },
    })
    def medications(self, request, medication):
        return paths_filtered_by_status(request, medication)

    @calculated_property( schema={
        "title": "Supportive Medications",
        "type": "array",
        "items": {
            "type": "string",
            "linkTo": "SupportiveMedication",
        },
    })
    def supportive_medications(self, request, supportive_medication):
        return supportive_med_frequency(request, supportive_medication)


@collection(
    name='lab-results',
    properties={
        'title': 'Lab results',
        'description': 'Lab results pages',
    })
class LabResult(Item):
    item_type = 'lab_results'
    schema = load_schema('encoded:schemas/lab_results.json')
    embeded = []


@collection(
    name='vital-results',
    properties={
        'title': 'Vital results',
        'description': 'Vital results pages',
    })
class VitalResult(Item):
    item_type = 'vital_results'
    schema = load_schema('encoded:schemas/vital_results.json')
    embeded = []


@collection(
    name='germline',
    properties={
        'title': 'Germline Mutations',
        'description': 'Germline Mutation results pages',
    })
class Germline(Item):
    item_type = 'germline'
    schema = load_schema('encoded:schemas/germline.json')
    embeded = []

@collection(
    name='consent',
    properties={
        'title': 'Consent',
        'description': 'Consent results pages',
    })
class Consent(Item):
    item_type = 'consent'
    schema = load_schema('encoded:schemas/consent.json')
    embeded = []


@collection(
    name='radiation',
    properties={
        'title': 'Radiation treatment',
        'description': 'Radiation treatment results pages',
    })
class Radiation(Item):
    item_type = 'radiation'
    schema = load_schema('encoded:schemas/radiation.json')
    embeded = []

    @calculated_property(condition='dose', schema={
        "title": "Dosage per Fraction",
        "type": "number",
    })
    def dose_per_fraction(self, request, dose, fractions):
        dose_per_fraction = dose/fractions
        return dose_per_fraction


@collection(
    name='medical_imaging',
    properties={
        'title': 'Medical imaging',
        'description': 'Medical imaging results pages',
    })
class MedicalImaging(Item):
    item_type = 'medical-imaging'
    schema = load_schema('encoded:schemas/medical_imaging.json')
    embeded = []

@property
def __name__(self):
    return self.name()


@collection(
    name='medication',
    properties={
        'title': 'Medications',
        'description': 'Medication results pages',
    })
class Medication(Item):
    item_type = 'medication'
    schema = load_schema('encoded:schemas/medication.json')
    embeded = []


@collection(
    name='supportive-medication',
    properties={
        'title': 'Supportive Medications',
        'description': 'Supportive Medication results pages',
    })
class SupportiveMedication(Item):
    item_type = 'supportive_medication'
    schema = load_schema('encoded:schemas/supportive_medication.json')
    embeded = []


@view_config(context=Patient, permission='view', request_method='GET', name='page')
def patient_page_view(context, request):
    if request.has_permission('view_details'):
        properties = item_view_object(context, request)
    else:
        item_path = request.resource_path(context)
        properties = request.embed(item_path, '@@object')
    for path in context.embedded:
        expand_path(request, properties, path)
    return properties


@view_config(context=Patient, permission='view', request_method='GET',
             name='object')
def patient_basic_view(context, request):
    properties = item_view_object(context, request)
    filtered = {}
    for key in ['@id', '@type', 'accession', 'uuid', 'gender', 'ethnicity', 'race', 'age', 'age_units', 'status', 'labs', 'vitals', 'germline', 'germline_summary','radiation', 'medical_imaging', 'medications', 'supportive_medications']:
    # for key in ['@id', '@type', 'accession', 'uuid', 'gender', 'ethnicity', 'race', 'age', 'age_units', 'status', 'labs', 'vitals', 'radiation', 'medical_imaging']:
        try:
            filtered[key] = properties[key]
        except KeyError:
            pass
    return filtered
