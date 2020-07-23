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
    name="pathology-reports",
    unique_key="accession",
    properties={
        "title": "Pathology tumor reports",
        "description": "Pathology tumor reports results pages",
    },
)
class PathologyReport(Item):
    item_type = "pathology_report"
    schema = load_schema("encoded:schemas/pathology_report.json")
    name_key = "accession"
    embedded = [
        "ihc",
    ]
    rev = {
        "ihc": ("Ihc", "pathology_report"),
    }
    audit_inherit = []
    set_status_up = []
    set_status_down = []

    @calculated_property(  schema={
        "title": "Pathology Report Tumor Range",
        "description": "Customized tumor range for pathology report",
        "type": "string",

    })

    def pathology_report_tumor_range(self):
        return self.__pathology_report_tumor_range__

    @property
    def __pathology_report_tumor_range__(self):
        properties = self.upgrade_properties()
        return self._pathology_report_tumor_range(properties)

    def _pathology_report_tumor_range(self, properties):
        tumor_size_range = []
        tumor_size=properties['tumor_size']
        if properties['path_source_procedure'] == 'path_nephrectomy':
            if tumor_size is None:
                tumor_size_range.append("unknown")
            elif 0 <= tumor_size < 3:
                tumor_size_range.append("0-3 cm")
            elif 3 <= tumor_size < 7:
                tumor_size_range.append("3-7 cm")
            elif 7 <= tumor_size < 10:
                tumor_size_range.append("7-10 cm")
            else:
                tumor_size_range.append("10+ cm")
        return tumor_size_range

    @calculated_property(
        schema={
            "title": "ihc link PR",
            "type": "array",
            "items": {"type": "string", "linkTo": "Ihc"},
        }
    )
    def ihc(self, request, ihc):
        return paths_filtered_by_status(request, ihc)
