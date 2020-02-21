from snovault import (
    calculated_property,
    collection,
    load_schema,
)
from .base import (
    Item,
    # SharedItem,
    paths_filtered_by_status,
)
from pyramid.traversal import find_root, resource_path
import re


@collection(
    name="surgeries",
    unique_key="accession",
    properties={
        "title": "Surgery Report",
        "description": "Surgery and pathology report",
    },
)
class Surgery(Item):
    item_type = "surgery"
    schema = load_schema("encoded:schemas/surgery.json")
    name_key = "accession"

    embedded = [
        "pathology_report",
        "surgery_procedure",
        "ihc"
    ]
    rev = {
        "pathology_report": ("PathologyReport", "surgery"),
        "surgery_procedure": ("SurgeryProcedure", "surgery"),
        "ihc": ("Ihc", "surgery"),
    }
    audit_inherit = []
    set_status_up = []
    set_status_down = []

    @calculated_property(
        schema={
            "title": "Surgery Procedures",
            "type": "array",
            "items": {
                "type": "string",
                "linkTo": "SurgeryProcedure",
            },
        }
    )
    def surgery_procedure(self, request, surgery_procedure):
        return paths_filtered_by_status(request, surgery_procedure)

    @calculated_property(
        condition="surgery_procedure",
        schema={
            "title": "Nephrectomy Robotic Assist",
            "type": "array",
            "items": {
                "type": "string",
            },
        },
    )
    def nephr_robotic_assist(self, request, surgery_procedure):

        for sp in surgery_procedure:

            sp_object = request.embed(sp, "@@object")
            nephr_details=sp_object.get('nephrectomy_details')
            robotic_assist_type = []

            if nephr_details is not None:
                nephr_robotic_assist = sp_object.get('nephrectomy_details').get('robotic_assist')
                if nephr_robotic_assist is True:
                    robotic_assist_type.append("True")
                else:
                    robotic_assist_type.append("False")

        return robotic_assist_type

    @calculated_property(
        schema={
            "title": "Pathology Report",
            "type": "array",
            "items": {
                "type": "string",
                "linkTo": "PathologyReport",
            },
        }
    )
    def pathology_report(self, request, pathology_report):
        return paths_filtered_by_status(request, pathology_report)


    @calculated_property(
        schema={
            "title": "ihc link PR",
            "type": "array",
            "items": {
                "type": "string",
                "linkTo": "Ihc",
            },
        }
    )
    def ihc(self, request, ihc):
        return paths_filtered_by_status(request, ihc)


@collection(
    name="surgery-procedures",
    properties={
        "title": "Surgery procedures",
        "description": "Surgery procedures results pages",
    },
)
class SurgeryProcedure(Item):
    item_type = "surgery_procedure"
    schema = load_schema("encoded:schemas/surgery_procedure.json")
    embeded = []


@collection(
    name="PR_ihc",
    properties={
        "title": "Pathology tumor reports IHC",
        "description": "Pathology tumor IHC reports results pages",
    },
)
class Ihc(Item):
    item_type = "ihc"
    schema = load_schema("encoded:schemas/ihc.json")
    embeded = []


@collection(
    name="pathology-reports",
    unique_key="pathology_report:name",
    properties={
        "title": "Pathology tumor reports",
        "description": "Pathology tumor reports results pages",
    },
)
class PathologyReport(Item):
    item_type = "pathology_report"
    schema = load_schema("encoded:schemas/pathology_report.json")
    embeded = []

    def unique_keys(self, properties):
        keys = super(PathologyReport, self).unique_keys(properties)
        keys.setdefault("pathology_report:name", []).append(self._name(properties))
        return keys

    @calculated_property(
        schema={
            "title": "Name",
            "type": "string",
            "description": "Name of the tumor specific pathology report.",
            "comment": "Do not submit. Value is automatically assigned by the server.",
            "uniqueKey": "name",
        }
    )
    def name(self):
        return self.__name__

    @property
    def __name__(self):
        properties = self.upgrade_properties()
        return self._name(properties)

    def _name(self, properties):
        root = find_root(self)
        surgery_uuid = properties["surgery"]
        surgery_id = root.get_by_uuid(surgery_uuid).upgrade_properties()["accession"]
        return u"{}-{}".format(surgery_id, properties["tumor_sequence_number"])

    @calculated_property(
        condition='tumor_size',
        schema={
            "title": "Tumor size range",
            "type": "string",
        },
    )
    def tumor_size_range(self, request, tumor_size):

        if 0 <= tumor_size < 3:
            tumor_size_range = "0-2.9 cm"
        elif 3 <= tumor_size < 7:
            tumor_size_range = "3-6.9 cm"
        elif 7 <= tumor_size < 10:
            tumor_size_range = "7-9.9 cm"
        else:
            tumor_size_range = "10+ cm"

        return tumor_size_range

    @calculated_property(
        condition='t_stage',
        schema={
            "title": "pT stage in version 6",
            "type": "array",
            "items": {
                "type": "string",
            },
        },
    )
    def pT_stage_version6(self, t_stage, ajcc_version):

        t_stage_version6 = None

        if ajcc_version == "6th edition":
            if t_stage == "pT1a":
                t_stage_version6 ="1A"
            elif t_stage == "pT1b":
                t_stage_version6 ="1B"
            elif t_stage == "pT2":
                t_stage_version6 ="2"
            elif t_stage == "pT3":
                t_stage_version6 ="3"
            elif t_stage == "pT3a":
                t_stage_version6 ="3A"
            elif t_stage == "pT3b":
                t_stage_version6 ="3B"
            elif t_stage == "pT3c":
                t_stage_version6 ="3C"
            elif t_stage == "pT4":
                t_stage_version6 ="4"

        return t_stage_version6


    @calculated_property(
        condition='t_stage',
        schema={
            "title": "pT stage in version 7",
            "type": "array",
            "items": {
                "type": "string",
            },
        },
    )
    def pT_stage_version7(self, t_stage, ajcc_version):

        t_stage_version7 = None

        if ajcc_version == "7th edition":
            if t_stage == "pT1a":
                t_stage_version7 ="1A"
            elif t_stage == "pT1b":
                t_stage_version7 ="1B"
            elif t_stage == "pT2":
                t_stage_version7 ="2"
            elif t_stage == "pT3":
                t_stage_version7 ="3"
            elif t_stage == "pT3a":
                t_stage_version7 ="3A"
            elif t_stage == "pT3b":
                t_stage_version7 ="3B"
            elif t_stage == "pT3c":
                t_stage_version7 ="3C"
            elif t_stage == "pT4":
                t_stage_version7 ="4"

        return t_stage_version7


    @calculated_property(
        condition="ajcc_tnm_stage",
        schema={
            "title": "pTNM stage in version 6",
            "type": "array",
            "items": {
                "type": "string",
            },
        },
    )
    def pTNM_stage_version6(self, ajcc_tnm_stage, ajcc_version):

        tnm_stage_version6 = None

        if ajcc_version == "6th edition":
            if ajcc_tnm_stage == "1":
                tnm_stage_version6 ="1"
            elif ajcc_tnm_stage == "2":
                tnm_stage_version6 ="2"
            elif ajcc_tnm_stage == "3":
                tnm_stage_version6 ="3"
            elif ajcc_tnm_stage == "4":
                tnm_stage_version6 ="4"

        return tnm_stage_version6

    @calculated_property(
        condition="ajcc_tnm_stage",
        schema={
            "title": "pTNM stage in version 7",
            "type": "array",
            "items": {
                "type": "string",
            },
        },
    )
    def pTNM_stage_version7(self, ajcc_tnm_stage, ajcc_version):

        tnm_stage_version7 = None

        if ajcc_version == "7th edition":
            if ajcc_tnm_stage == "1":
                tnm_stage_version7 ="1"
            elif ajcc_tnm_stage == "2":
                tnm_stage_version7 ="2"
            elif ajcc_tnm_stage == "3":
                tnm_stage_version7 ="3"
            elif ajcc_tnm_stage == "4":
                tnm_stage_version7 ="4"

        return tnm_stage_version7
