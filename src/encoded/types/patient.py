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

    @calculated_property(schema={
        "title": "Last Follow-up Date",
        "description": "Calculated last follow-up date,format as YYYY-MM-DD",
        "type": "string",
    })
    def last_follow_up_date(self, request, labs, vitals, germline,ihc, consent,radiation,medical_imaging,medication,supportive_medication,surgery):

        all_traced_dates=[]
        last_follow_up_date="Not available"
        if len(vitals) > 0:
            for obj in vitals:
                v_obj = request.embed(obj, "@@object")
                vital_dates=v_obj.get("date")
                all_traced_dates.append(vital_dates)
        if len(labs) > 0:
            for obj in labs:
                l_obj = request.embed(obj, "@@object")
                lab_dates=l_obj.get("date")
                all_traced_dates.append(lab_dates)
        if len(surgery) > 0:
            for obj in surgery:
                s_obj = request.embed(obj, "@@object")
                sur_dates=s_obj.get("date")
                all_traced_dates.append(sur_dates)
        if len(germline) > 0:
            for obj in germline:
                g_obj = request.embed(obj, "@@object")
                ger_dates=g_obj.get("service_date")
                all_traced_dates.append(ger_dates)
        if len(ihc) > 0:
            for obj in ihc:
                ihc_obj = request.embed(obj, "@@object")
                ihc_dates=ihc_obj.get("service_date")
                all_traced_dates.append(ihc_dates)
        if len(radiation) > 0:
            for obj in radiation:
                r_obj = request.embed(obj, "@@object")
                if 'end_date' in r_obj:
                    rad_dates=r_obj.get("end_date")
                else:
                    rad_dates=r_obj.get("start_date")
                all_traced_dates.append(rad_dates)
        if len(medical_imaging) > 0:
            for obj in medical_imaging:
                mi_obj = request.embed(obj, "@@object")
                med_img_dates=mi_obj.get("procedure_date")
                all_traced_dates.append(med_img_dates)
        if len(medication) > 0:
            for obj in medication:
                m_obj = request.embed(obj, "@@object")
                med_dates=m_obj.get("end_date")
                all_traced_dates.append(med_dates)
        if len(supportive_medication) > 0:
            for obj in supportive_medication:
                sm_obj = request.embed(obj, "@@object")
                sup_med_dates=sm_obj.get("start_date")
                all_traced_dates.append(sup_med_dates)

        if len(all_traced_dates) > 0:
            all_traced_dates.sort(key = lambda date: datetime.strptime(date, "%Y-%m-%d"))
            last_follow_up_date = all_traced_dates[-1]
        return last_follow_up_date

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

    @calculated_property(define=True, schema={
        "title": "Metastasis status ",
        "type": "string",
    })
    def metastasis_status(self, request, radiation=None, surgery=None):
        status = "No"
        if len(radiation) > 0:
            
            for radiation_record in radiation:
                radiation_object = request.embed(radiation_record, '@@object') 
                #site mapping
                if radiation_object['site_general'] != "Kidney, right" and radiation_object['site_general'] != "Kidney, thrombus" and radiation_object['site_general'] != "Kidney, left" and radiation_object['site_general'] != "Retroperitoneum / renal bed, left" and radiation_object['site_general'] != "Retroperitoneum / renal bed, right":
                    status = "Yes"
        else:
            if len(surgery) > 0:               
                for surgery_record in surgery:
                    surgery_object = request.embed(surgery_record, '@@object')
                    path_reports = surgery_object['pathology_report']               
                    if len(path_reports) > 0:                
                        for path_report in path_reports:
                            path_report_obj = request.embed(path_report, '@@object')                        
                            if path_report_obj['path_source_procedure'] == 'path_metasis':                           
                                status = "Yes"                            
        return status

    @calculated_property(define=True, schema={
        "title": "Vital Status",
        "type": "string",
    })
    def vital_status(self, request, death_date=None):
        if death_date is None:
            vital_status = "Alived"
        else:
            vital_status = "Deceased"
        return vital_status



    


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
        "title": "Diagnosis",
        "description": "Infomation related to diagnosis",
        "type": "object",
        "additionalProperties": False,
        "properties":{
            "diagnosis_date": {
                "title": "Diagnosis Date",
                "description": "Date of Diagnosis",
                "type": "string",
            },
            "age": {
                "title": "Diagnosis age",
                "description": "The age of diagnosis.",
                "type": "string",
                "pattern": "^((unknown)|([1-8]?\\d)|(90 or above))$"
            },
            "age_unit": {
                "title": "Diagnosis age unit",
                "type": "string",
                "default": "year",
                "enum": [
                    "year"
                ]
            },
            "age_range": {
                "title": "Age at Diagnosis",
                "type": "string"

            }

        },
    })
    def diagnosis(self, request, surgery, radiation, medication):
        nephrectomy_dates = []
        non_nephrectomy_dates = []
        diagnosis_date = "Not available"
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
                    medication_object = request.embed(medication_record, '@@object')
                    non_nephrectomy_dates.append(medication_object['start_date'])

            if len(non_nephrectomy_dates) > 0:
                non_nephrectomy_dates.sort(key = lambda date: datetime.strptime(date, '%Y-%m-%d'))
                diagnosis_date = non_nephrectomy_dates[0]
        age_range = "Unknown"
        ageString = "Unknown"
        if diagnosis_date != "Not available":
            birth_date = datetime.strptime("1800-01-01", "%Y-%m-%d")
            end_date = datetime.strptime(diagnosis_date, "%Y-%m-%d")
            age = end_date.year - birth_date.year -  ((end_date.month, end_date.day) < (birth_date.month, birth_date.day))
            ageString = str(age)
            if age >= 90:
                ageString = "90 or above"


            if age >= 80:
                age_range = "80+"
            elif age >= 60:
                age_range = "60 - 79"
            elif age >= 40:
                age_range = "40 - 59"
            elif age >= 20:
                age_range = "20 - 39"
            else:
                age_range = "0 - 19"

        diagnosis = dict()
        diagnosis['diagnosis_date'] = diagnosis_date
        diagnosis['age'] = ageString
        diagnosis['age_unit'] = "year"
        diagnosis['age_range'] = age_range

        return diagnosis

    @calculated_property(schema={
        "title": "Metastasis",
        "description": "Infomation related to Metastasis",
        "type": "array",
        "items": {
            "title": "Metastasis Record",
            "type": "object",
            "additionalProperties": False,
            "properties":{
                "date": {
                    "title": "Date of Metastasis Record",
                    "description": "Date of Metastasis Record",
                    "type": "string"
                },
                "histology_proven": {
                    "title": "Histology Proven",
                    "type": "string"
                },
                "source": {
                    "title": "Source",
                    "description": "Source of the record",
                    "type": "string",
                    "enum": [
                        "Pathology report",
                        "Radiation treatment"
                    ]
                },
                "site": {
                    "title": "Metastasis Site",
                    "type": "string",
                    "enum": [
                        "Adrenal",
                        "Bone",
                        "Brain",
                        "Liver",
                        "Lung and pleura",
                        "Lymph node",
                        "Other"
                    ]
                }

            },
        }
    })
    def metastasis(self, request, surgery, radiation):
        records = []
        if len(surgery) > 0:
            for surgery_record in surgery:
                surgery_object = request.embed(surgery_record, '@@object')
                path_reports = surgery_object['pathology_report']               
                if len(path_reports) > 0:                
                    for path_report in path_reports:
                        path_report_obj = request.embed(path_report, '@@object')                        
                        if path_report_obj['path_source_procedure'] == 'path_metasis':                           
                            record = {
                                'date': path_report_obj['date'],
                                'source': 'Pathology report',
                                'site': path_report_obj['metasis_details']['site'],
                                'histology_proven': 'Yes'
                            }
                            if record not in records:
                                records.append(record)               
        if len(radiation) > 0 :
            for radiation_record in radiation:
                radiation_object = request.embed(radiation_record, '@@object') 
                #site mapping
                if radiation_object['site_general'] == "Adrenal gland, left" or radiation_object['site_general'] == "Adrenal gland, right":
                    radiation_site = "Adrenal"
                elif radiation_object['site_general'] == "Spine" or radiation_object['site_general'] == "Bone":
                    radiation_site = "Bone"
                elif radiation_object['site_general'] == "Brain" or radiation_object['site_general'] == "Liver":
                    radiation_site = radiation_object['site_general']
                elif radiation_object['site_general'] == "Connective, subcutaneous and other soft tissues, NOS" or radiation_object['site_general'] == "Retroperitoneum & peritoneum" or radiation_object['site_general'] == "Connective, subcutaneous and other soft tissue, abdomen" or radiation_object['site_general'] == "Gastrointestine/ digestive system & spleen" or radiation_object['site_general'] == "Salivary gland":
                    radiation_site = "Other"
                elif radiation_object['site_general'] == "Lung, right" or radiation_object['site_general'] == "Lung, left" or radiation_object['site_general'] == "Lung":
                    radiation_site = "Lung and pleura"
                elif radiation_object['site_general'] == "Lymph node, NOS" or radiation_object['site_general'] == "Lymph node, intrathoracic" or radiation_object['site_general'] == "Lymph node, intra abdominal":
                    radiation_site = "Lymph Node"

                record = {
                    'date': radiation_object['start_date'],
                    'source': 'Radiation treatment',
                    'site': radiation_site,
                    'histology_proven': 'No'
                }
                if record not in records:
                    records.append(record)

        return records


    matrix = {
        'y': {
            'facets': [
                'status',
                'sex',
                'race',
                'ethnicity',
                'surgery_summary',
                'radiation_summary',
                'medications.name',
                'surgery.surgery_procedure.surgery_type',
                'surgery.hospital_location',
                'sur_path_tumor_size',
                'surgery.pathology_report.ajcc_p_stage',
                'surgery.pathology_report.n_stage',
                'surgery.pathology_report.m_stage',
                'surgery.pathology_report.ajcc_tnm_stage',
                'germline_summary',
                'ihc.antibody',
                'ihc.result',

            ],
            'group_by': ['race', 'sex'],
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
                'sex',
                'race',
                'radiation_summary',

            ],
            'group_by': ['sex', 'radiation_summary'],
            'label': 'Sex',
        },
        'x': {
            'facets': [
                'race',
            ],
            'group_by': 'race',
            'label': 'Race',
        },
        'grouping': ['sex', 'status'],
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

    @calculated_property(condition='dose', schema={
        "title": "Dosage range per fraction",
        "type": "string",

    })
    def dose_range(self, request, dose, fractions):
        dose_per_fraction = dose/fractions
        if dose_per_fraction < 2000:
            return "200 - 2000"
        elif dose_per_fraction < 4000:
            return "2000 - 4000"
        else:
            return "4000 - 6000"

    @calculated_property(condition='fractions', schema={
        "title": "Fractions range",
        "type": "string",
        
    })
    def fractions_range(self, request, fractions):
        
        if fractions < 5:
            return "1 - 5"
        elif fractions < 10:
            return "5 - 10"
        elif fractions < 15:
            return "10 - 15"
        else:
            return "15 and up"
        



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
    for key in ['@id', '@type', 'accession', 'uuid', 'sex', 'ethnicity', 'race', 'diagnosis', 'last_follow_up_date', 'status',  'ihc','labs', 'vitals', 'germline', 'germline_summary','radiation', 'radiation_summary', 'vital_status', 'medical_imaging',
                'medications','medication_range', 'supportive_medications', 'biospecimen', 'surgery_summary','sur_nephr_robotic_assist']:
        try:
            filtered[key] = properties[key]
        except KeyError:
            pass
    return filtered





