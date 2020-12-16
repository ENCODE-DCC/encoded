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
        "pathology_report.ihc"
    ]
    rev = {
        "pathology_report": ("PathologyReport", "surgery"),
        "surgery_procedure": ("SurgeryProcedure", "surgery"),
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
                    robotic_assist_type.append("Yes")
                else:
                    robotic_assist_type.append("No")

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


    def name(self):
        return self.__name__
