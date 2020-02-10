# from pyramid.view import (
#     view_config,
# )
# from pyramid.security import (
#     Allow,
#     Deny,
#     Everyone,
# )
# from pyramid.traversal import find_root
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
from pyramid.traversal import (
    find_root,
    resource_path
)
import re
# from snovault.resource_views import item_view_object
# from snovault.util import expand_path
# from collections import defaultdict

@collection(
    name='surgery',
    unique_key='accession',
    properties={
        'title': 'Surgery Report',
        'description': 'Surgery and pathology report',
    })
class Surgery(Item):
    item_type = 'surgery'
    schema = load_schema('encoded:schemas/surgery.json')
    name_key = 'accession'

    embedded = [
        'pathology_report',
        'surgery_procedure'
    ]
    rev = {
        'pathology_report': ('PathologyReport', 'surgery'),
        'surgery_procedure': ('SurgeryProcedure', 'surgery'),
    }
    audit_inherit = []
    set_status_up = []
    set_status_down = []

    @calculated_property(schema={
        "title": "Surgery Procedures",
        "type": "array",
        "items": {
            "type": 'string',
            "linkTo": "SurgeryProcedure"
        },
    })
    def surgery_procedure(self, request, surgery_procedure):
        return paths_filtered_by_status(request, surgery_procedure)

    @calculated_property(schema={
        "title": "Pathology Report",
        "type": "array",
        "items": {
            "type": 'string',
            "linkTo": "PathologyReport"
        },
    })
    def pathology_report(self, request, pathology_report):
        return paths_filtered_by_status(request, pathology_report)


@collection(
    name='surgery-procedures',
    properties={
        'title': 'Surgery procedures',
        'description': 'Surgery procedures results pages',
    })
class SurgeryProcedure(Item):
    item_type = 'surgery_procedure'
    schema = load_schema('encoded:schemas/surgery_procedure.json')
    embeded = []


@collection(
    name='pathology-reports',
    unique_key='pathology_report:name',
    properties={
        'title': 'Pathology tumor reports',
        'description': 'Pathology tumor reports results pages',
    })
class PathologyReport(Item):
    item_type = 'pathology_report'
    schema = load_schema('encoded:schemas/pathology_report.json')
    embeded = []

    def unique_keys(self, properties):
        keys = super(PathologyReport, self).unique_keys(properties)
        keys.setdefault('pathology_report:name', []).append(self._name(properties))
        return keys

    @calculated_property(schema={
        "title": "Name",
        "type": "string",
        "description": "Name of the tumor specific pathology report.",
        "comment": "Do not submit. Value is automatically assigned by the server.",
        "uniqueKey": "name"
    })
    def name(self):
        return self.__name__

    @property
    def __name__(self):
        properties = self.upgrade_properties()
        return self._name(properties)

    def _name(self, properties):
        root = find_root(self)
        surgery_uuid = properties['surgery']
        surgery_id = root.get_by_uuid(surgery_uuid).upgrade_properties()['accession']
        return u'{}-{}'.format(surgery_id, properties['tumor_sequence_number'])
