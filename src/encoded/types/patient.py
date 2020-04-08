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
from datetime import datetime
import math


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
        'ihc',
        'consent',
        'radiation',
        'medical_imaging',
        'medications',
        'supportive_medications',
        'surgery',
        'surgery.surgery_procedure',
        'surgery.pathology_report',
        'biospecimen']
    rev = {
        'labs': ('LabResult', 'patient'),
        'vitals': ('VitalResult', 'patient'),
        'germline': ('Germline', 'patient'),
        'ihc': ('Ihc', 'patient'),
        'consent': ('Consent', 'patient'),
        'radiation': ('Radiation', 'patient'),
        'medical_imaging': ('MedicalImaging', 'patient'),
        'medication': ('Medication', 'patient'),
        'supportive_medication': ('SupportiveMedication', 'patient'),
        'surgery': ('Surgery', 'patient'),
        'biospecimen': ('Biospecimen', 'patient')
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
        "title":"IHC result",
        "type":"array",
        "items":{
            "type":'string',
            "linkTo":'ihc'
        }
    })

    def ihc(self,request,ihc):
        return paths_filtered_by_status(request,ihc)


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

    @calculated_property(define=True, schema={
        "title": "Radiation Treatment Summary",
        "type": "string",
    })
    def radiation_summary(self, request, radiation=None):
        if len(radiation) > 0:
            radiation_summary = "Treatment Received"
        else:
            radiation_summary = "No Treatment Received"
        return radiation_summary

    @calculated_property(condition='radiation', schema={
        "title": "Dose per Fraction",
        "type": "array",
        "items": {
            "type": "string",
        },
    })
    def dose_range(self, request, radiation):
        dose_range = []
        for treatment in radiation:
            treatment_object = request.embed(treatment, '@@object')
            if treatment_object['dose']/treatment_object['fractions'] < 2000:
                dose_range.append("200 - 2000")
            elif treatment_object['dose']/treatment_object['fractions'] < 4000:
                dose_range.append("2000 - 4000")
            else:
                dose_range.append("4000 - 6000")
        return dose_range

    @calculated_property(condition='radiation', schema={
        "title": "Radiation Fractions",
        "type": "array",
        "items": {
            "type": "string",
        },
    })
    def fractions_range(self, request, radiation):
        fractions_range = []
        for treatment in radiation:
            treatment_object = request.embed(treatment, '@@object')
            if treatment_object['fractions'] < 5:
                fractions_range.append("1 - 5")
            elif treatment_object['fractions'] < 10:
                fractions_range.append("5 - 10")
            elif treatment_object['fractions'] < 15:
                fractions_range.append("10 - 15")
            else:
                fractions_range.append("15 and up")
        return fractions_range


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

    @calculated_property(condition='medication', schema={
        "title": "Medication duration",
        "type": "array",
        "items": {
            "type": "string",
        },
    })
    def medication_range(self, request, medication):

        for med in medication:
            medication_object = request.embed(med, '@@object')
            date_format="%Y-%m-%d"
            start_date=datetime.strptime(medication_object['start_date'],date_format )
            end_date=datetime.strptime(medication_object['end_date'],date_format )
            medication_duration=(end_date-start_date).days/30

            medication_range=[]
            if 0<=medication_duration<3:
                medication_range.append("0-3 months")
            elif 3<=medication_duration<6:
                medication_range.append("3-6 months")
            elif 6<=medication_duration<9:
                medication_range.append("6-9 months")
            elif 9<=medication_duration<12:
                medication_range.append("9-12 months")
            elif 12<=medication_duration<18:
                medication_range.append("12-18 months")
            elif 18<=medication_duration<24:
                medication_range.append("18-24 months")
            elif 24<=medication_duration<30:
                medication_range.append("24-30 months")
            elif 30<=medication_duration<36:
                medication_range.append("30-36 months")
            elif 36<=medication_duration<48:
                medication_range.append("36-48 months")
            else :
                medication_range.append("48+ months")
        return medication_range


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


    @calculated_property(schema={
        "title": "Biospecimen",
        "type": "array",
        "items": {
            "type": 'string',
            "linkTo": "Biospecimen"
        },
    })

    def biospecimen(self, request, biospecimen):
        return paths_filtered_by_status(request, biospecimen)


    @calculated_property( schema={
        "title": "Surgeries",
        "type": "array",
        "items": {
            "type": "string",
            "linkTo": "Surgery",
        },
    })

    def surgery(self, request, surgery):
        return paths_filtered_by_status(request, surgery)


    @calculated_property(define=True, schema={
            "title": "Surgery Treatment Summary",
            "type": "string",
        })
    def surgery_summary(self, request, surgery=None):
            if len(surgery) > 0:
                surgery_summary = "Treatment Received"
            else:
                surgery_summary = "No Treatment Received"
            return surgery_summary

    @calculated_property(schema={
        "title": "Diagnosis Date",
        "type": "string",
    })
    def diagnosis_date(self, request, surgery, radiation, medication):
        nephrectomy_dates = []
        non_nephrectomy_dates = []
        diagnosis_date = "not available"
        if len(surgery) > 0:
            for surgery_record in surgery:
                surgery_object = request.embed(surgery_record, '@@object')
                surgery_procedure = surgery_object['surgery_procedure']
                for procedure_record in surgery_procedure:
                    procedure_obj = request.embed(procedure_record, '@@object')
                    if procedure_obj['procedure_type'] == "Nephrectomy":
                        nephrectomy_dates.append(surgery_object['date'])
                    elif  procedure_obj['procedure_type'] == "Biopsy" or procedure_obj['procedure_type'] == "Metastectomy":
                        non_nephrectomy_dates.append(surgery_object['date'])
        if len(nephrectomy_dates) > 0 :
            nephrectomy_dates.sort(key = lambda date: datetime.strptime(date, '%Y-%m-%d')) 
            diagnosis_date = nephrectomy_dates[0]
        else:
            if len(radiation) > 0:
                # add radiation dates
                for radiation_record in radiation:
                    radiation_object = request.embed(radiation_record, '@@object')
                    non_nephrectomy_dates.append(radiation_object['start_date'])
            if len(medication) > 0:
                # add medication dates
                for medication_record in medication:
                    radiation_object = request.embed(medication_record, '@@object')
                    non_nephrectomy_dates.append(radiation_object['start_date'])

            if len(non_nephrectomy_dates) > 0:
                non_nephrectomy_dates.sort(key = lambda date: datetime.strptime(date, '%Y-%m-%d')) 
                diagnosis_date = non_nephrectomy_dates[0]
        return diagnosis_date

    matrix = {
        'y': {
            'facets': [
                'status',
                'gender',
                'race',
                'ethnicity',
                'surgery_summary',
                'radiation_summary',
                'medications.name',
                'surgery.surgery_procedure.surgery_type',
                'surgery.hospital_location',
                'sur_path_tumor_size',
                'surgery.pathology_report.t_stage',
                'germline_summary',
                'ihc.antibody',
                'ihc.result',
                
            ],
            'group_by': ['race', 'gender'],
            'label': 'race',
        },
        'x': {
            'facets': [
                
                'surgery.pathology_report.histology',
            ],
            'group_by': 'surgery.pathology_report.histology',
            'label': 'histology',
        },
    }

    summary_data = {
        'y': {
            'facets': [

                'status',
                'gender',
                'race',
                'radiation_summary',

            ],
            'group_by': ['gender', 'radiation_summary'],
            'label': 'Gender',
        },
        'x': {
            'facets': [
                'race',
            ],
            'group_by': 'race',
            'label': 'Race',
        },
        'grouping': ['gender', 'status'],
    }



    @calculated_property(condition='surgery', schema={
        "title": "surgery procedure nephrectomy robotic assist",
        "type": "array",
        "items": {
            "type": "string",
        },
    })

    def sur_nephr_robotic_assist(self, request, surgery):


        sp_obj_array = []
        array=[]
        if surgery is not None:
            for so in surgery:
                so_object = request.embed(so, "@@object")
                sp_obj_array = so_object.get("surgery_procedure")

                if sp_obj_array is not None:
                    for spo in sp_obj_array:
                        sp_obj = request.embed(spo, "@@object")
                        sp_proc_type=sp_obj.get("procedure_type")
                        if sp_proc_type=="Nephrectomy":
                            sp_nephr_robotic=sp_obj.get("nephrectomy_details").get("robotic_assist")
                            array.append(sp_nephr_robotic)
                        else:
                            continue

        robotic_assist=[]

        for logic in array:
            if  logic is True:
                robotic_assist.append("True")
            else:
                robotic_assist.append("False")
        return robotic_assist

    @calculated_property(condition='surgery', schema={
        "title": "surgery pathology tumor size calculation",
        "type": "array",
        "items": {
            "type": "string",
        },
    })

    def sur_path_tumor_size(self, request, surgery):
        
        
        sp_obj_array = []
        array=[]
        if surgery is not None:
            for so in surgery:
                so_object = request.embed(so, "@@object")
                sp_obj_array = so_object.get("pathology_report")

                if sp_obj_array is not None:
                    for spo in sp_obj_array:
                        sp_obj = request.embed(spo, "@@object")
                        sp_tumor_size=sp_obj.get("tumor_size")

                        array.append(sp_tumor_size)

        tumor_size_range = []
        for tumor_size in array:
            if 0 <= tumor_size < 3:
                tumor_size_range.append("0-3 cm")
            elif 3 <= tumor_size < 7:
                tumor_size_range.append("3-7 cm")
            elif 7 <= tumor_size < 10:
                tumor_size_range.append("7-10 cm")
            else:
                tumor_size_range.append("10+ cm")
        return tumor_size_range                   

   

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
    name='ihc',
    properties={
        'title': 'IHC results',
        'description': 'IHC results pages',
    })
class Ihc(Item):
    item_type = 'ihc'
    schema = load_schema('encoded:schemas/ihc.json')
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


@property
def __name__(self):
    return self.name()


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
    for key in ['@id', '@type', 'accession', 'uuid', 'gender', 'ethnicity', 'race', 'age', 'age_units', 'diagnosis_date', 'status',  'ihc','labs', 'vitals', 'germline', 'germline_summary','radiation', 'radiation_summary', 'dose_range', 'fractions_range', 'medical_imaging',
                'medications','medication_range', 'supportive_medications', 'biospecimen', 'surgery_summary','sur_nephr_robotic_assist']:
        try:
            filtered[key] = properties[key]
        except KeyError:
            pass
    return filtered


