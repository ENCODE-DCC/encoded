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
  
  

    @calculated_property(
        schema={
            "title": "ihc link PR",
            "type": "array",
            "items": {"type": "string", "linkTo": "Ihc"},
        }
    )
    def ihc(self, request, ihc):
        return paths_filtered_by_status(request, ihc)
    

    
   
