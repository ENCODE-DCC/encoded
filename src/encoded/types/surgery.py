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
from pyramid.traversal import (
    find_root,
    resource_path
)
import re
from snovault.resource_views import item_view_object
from snovault.util import expand_path
from collections import defaultdict

@collection(
    name='surgeries',
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
        'surgery_procedure',
        'ihc'
    ]
    rev = {
        'pathology_report': ('PathologyReport', 'surgery'),
        'surgery_procedure': ('SurgeryProcedure', 'surgery'),
        'ihc':('Ihc','surgery')
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

    @calculated_property(schema={
        "title": "ihc link PR",
        "type": "array",
        "items": {
            "type": 'string',
            "linkTo": "Ihc"
        },
    })
    # @calculated_property(condition='pathology_report', schema={
    #     "title": "pathonlogy_report tumor size range",
    #     "type": "array",
    #     "items": {
    #         "type": "string",
    #     },
    # })
    # def tumor_size_range(self, request,pathology_report):
    #     tumor_size_range = []
    #     for tumorSize in pathology_report:
    #         tumorSize = request.embed(tumorSize, '@@object')
    #         if tumorSize['tumor_size'] < 3:
    #             tumor_size_range.append("<3cm")
    #         elif tumorSize['tumor_size'] < 7:
    #             tumor_size_range.append("3cm-7cm")
    #         elif tumorSize['tumor_size'] < 10:
    #             tumor_size_range.append("7cm-10cm")
    #         else:
    #             tumor_size_range.append("10cm and up")
    #     return tumor_size_range


    def ihc(self, request, ihc):
        return paths_filtered_by_status(request, ihc)

@collection(
    name='PR_ihc',
    properties={
        'title': 'PR-ihc linked',
        'description': 'PR-ihc results pages',
    })
class Ihc(Item):
    item_type = 'ihc'
    schema = load_schema('encoded:schemas/ihc.json')
    embeded = []

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

# @view_config(context=Surgery, permission='view', request_method='GET', name='page')
# def surgery_page_view(context, request):
#     if request.has_permission('view_details'):
#         properties = item_view_object(context, request)
#     else:
#         item_path = request.resource_path(context)
#         properties = request.embed(item_path, '@@object')
#     for path in context.embedded:
#         expand_path(request, properties, path)
#     return properties

# @view_config(context=Surgery, permission='view', request_method='GET',
#              name='object')
# def surgery_basic_view(context, request):
#     properties = item_view_object(context, request)
#     filtered = {}
#     for key in ['@id', '@type', 'accession', 'uuid', 'date','hospital_location','PathologyReport','SurgeryProcedure','Ihc','tumor_size_range']:
#         try:
#             filtered[key] = properties[key]
#         except KeyError:
#             pass
#     return filtered