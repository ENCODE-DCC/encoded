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

    embedded = ["pathology_report", "surgery_procedure", "ihc"]
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
            "items": {"type": "string", "linkTo": "SurgeryProcedure"},
        }
    )
    def surgery_procedure(self, request, surgery_procedure):
        return paths_filtered_by_status(request, surgery_procedure)

    @calculated_property(
        condition="surgery_procedure",
        schema={
            "title": "surgery procedure nephrectomy robotic assist",
            "type": "array",
            "items": {"type": "string"},
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
            "items": {"type": "string", "linkTo": "PathologyReport"},
        }
    )
    def pathology_report(self, request, pathology_report):
        return paths_filtered_by_status(request, pathology_report)

    @calculated_property(
        condition="pathology_report",
        schema={
            "title": "pathonlogy_report tumor size range",
            "type": "array",
            "items": {"type": "string",},
        },
    )
    def tumor_size_range(self, request, pathology_report):

        for object in pathology_report:

            tumor_object = request.embed(object, "@@object")
            tumor_size = tumor_object["tumor_size"]

            tumor_size_range = []

            if 0 <= tumor_size < 3:
                tumor_size_range.append("0-3 cm")
            elif 3 <= tumor_size < 7:
                tumor_size_range.append("3-7 cm")
            elif 7 <= tumor_size < 10:
                tumor_size_range.append("7-10 cm")
            else:
                tumor_size_range.append("10+ cm")
        return tumor_size_range

    @calculated_property(
        condition="pathology_report",
        schema={
            "title": "pathonlogy_report pT stage in version 6",
            "type": "array",
            "items": {"type": "string",},
        },
    )
    def pT_stage_version6(self, request, pathology_report):

        for object in pathology_report:

            pr_object = request.embed(object, "@@object")

            t_stage = pr_object["t_stage"]
            version = pr_object["ajcc_version"]

            t_stage_version6 = []

            if t_stage == "pT1a" and version == "6th edition":
                t_stage_version6.append("1A")
            elif t_stage == "pT1b" and version == "6th edition":
                t_stage_version6.append("1B")
            elif t_stage == "pT2" and version == "6th edition":
                t_stage_version6.append("2")
            elif t_stage == "pT3" and version == "6th edition":
                t_stage_version6.append("3")
            elif t_stage == "pT3a" and version == "6th edition":
                t_stage_version6.append("3A")
            elif t_stage == "pT3b" and version == "6th edition":
                t_stage_version6.append("3B")
            elif t_stage == "pT3c" and version == "6th edition":
                t_stage_version6.append("3C")
            elif t_stage == "pT4" and version == "6th edition":
                t_stage_version6.append("4")

        return t_stage_version6

    @calculated_property(
        condition="pathology_report",
        schema={
            "title": "pathonlogy_report pT stage in version 7",
            "type": "array",
            "items": {"type": "string",},
        },
    )
    def pT_stage_version7(self, request, pathology_report):

        for object in pathology_report:

            pr_object = request.embed(object, "@@object")

            t_stage = pr_object["t_stage"]
            version = pr_object["ajcc_version"]

            t_stage_version7 = []

            if t_stage == "pT1a" and version == "7th edition":
                t_stage_version7.append("1A")
            elif t_stage == "pT1b" and version == "7th edition":
                t_stage_version7.append("1B")
            elif t_stage == "pT2a" and version == "7th edition":
                t_stage_version7.append("2A")
            elif t_stage == "pT2b" and version == "7th edition":
                t_stage_version7.append("2B")
            elif t_stage == "pT3a" and version == "7th edition":
                t_stage_version7.append("3A")
            elif t_stage == "pT3b" and version == "7th edition":
                t_stage_version7.append("3B")
            elif t_stage == "pT3c" and version == "7th edition":
                t_stage_version7.append("3C")
            elif t_stage == "pT4" and version == "7th edition":
                t_stage_version7.append("4")

        return t_stage_version7

    @calculated_property(
        condition="pathology_report",
        schema={
            "title": "pathonlogy_report pTNM stage in version 6",
            "type": "array",
            "items": {"type": "string",},
        },
    )
    def pTNM_stage_version6(self, request, pathology_report):

        for object in pathology_report:

            pr_object = request.embed(object, "@@object")

            tnm_stage = pr_object["ajcc_tnm_stage"]
            version = pr_object["ajcc_version"]

            tnm_stage_version6 = []

            if tnm_stage == "1" and version == "6th edition":
                tnm_stage_version6.append("1")
            elif tnm_stage == "2" and version == "6th edition":
                tnm_stage_version6.append("2")
            elif tnm_stage == "3" and version == "6th edition":
                tnm_stage_version6.append("3")
            elif tnm_stage == "4" and version == "6th edition":
                tnm_stage_version6.append("4")

        return tnm_stage_version6

    @calculated_property(
        condition="pathology_report",
        schema={
            "title": "pathonlogy_report pTNM stage in version 7",
            "type": "array",
            "items": {"type": "string",},
        },
    )
    def pTNM_stage_version7(self, request, pathology_report):

        for object in pathology_report:

            pr_object = request.embed(object, "@@object")

            tnm_stage = pr_object["ajcc_tnm_stage"]
            version = pr_object["ajcc_version"]

            tnm_stage_version7 = []

            if tnm_stage == "1" and version == "7th edition":
                tnm_stage_version7.append("1")
            elif tnm_stage == "2" and version == "7th edition":
                tnm_stage_version7.append("2")
            elif tnm_stage == "3" and version == "7th edition":
                tnm_stage_version7.append("3")
            elif tnm_stage == "4" and version == "7th edition":
                tnm_stage_version7.append("4")

        return tnm_stage_version7

    @calculated_property(
        schema={
            "title": "ihc link PR",
            "type": "array",
            "items": {"type": "string", "linkTo": "Ihc"},
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
    properties={"title": "PR-ihc linked", "description": "PR-ihc results pages",},
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

