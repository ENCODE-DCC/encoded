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
        condition="pathology_report",
        schema={
            "title": "Tumor size range",
            "type": "array",
            "items": {"type": "string",},
        },
    )
    def tumor_size_range(self, request, pathology_report):

        for object in pathology_report:

            tumor_object = request.embed(object, "@@object")
            path_source_procedure = tumor_object['path_source_procedure']
            tumor_size_range = []
            if  path_source_procedure == 'path_nephrectomy':
                tumor_size = 'unknown'
                if 'tumor_size' in properties:
                    tumor_size = tumor_object["tumor_size"]
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
