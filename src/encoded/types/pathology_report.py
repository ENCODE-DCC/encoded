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
import re
# from snovault.resource_views import item_view_object
# from snovault.util import expand_path
# from collections import defaultdict

@collection(
    name='pathology_report',
    unique_key='accession',
    properties={
        'title': 'Pathology Report',
        'description': 'Available Pathology reports',
    })
class Pathology_report(Item):
    item_type = 'pathology_report'
    schema = load_schema('encoded:schemas/pathology_report.json')
    name_key = 'accession'
    
    embedded = [
        # 'patient',
        'surgery',
        # 'ihc',
    ]
    # rev = {
    #     'patient': ('Patient', 'pathology_report'),
    #     # 'surgery': ('Surgery', 'pathology_report'),
    #     # 'ihc': ('Ihc', 'pathology_report'),
    # }
    audit_inherit = []
    set_status_up = []
    set_status_down = []

    # @calculated_property( schema={
    #     "title": "Patient",
    #     "type": "string",

    # })
    # def patient(self, request, patient):
    #     return paths_filtered_by_status(request, patient)

    # @calculated_property( schema={
    #     "title": "Surgeries",
    #     "type": "array",
    #     "items": {
    #         "type": "string",
    #         "linkTo": "Surgery",
    #     },
    # })
    # def surgery(self, request, surgery):
    #     return paths_filtered_by_status(request, surgery)

# @collection(
#     name='patient',
#     properties={
#         'title': 'Patients',
#         'description': 'Patients results pages',
#     })
# class Patient(Item):
#     item_type = 'patient'
#     schema = load_schema('encoded:schemas/patient.json')
#     embeded = [] 
    
# @collection(
#     name='surgery',
#     properties={
#         'title': 'Surgeries',
#         'description': 'Surgeries results pages',
#     })
# class Surgery(Item):
#     item_type = 'surgery'
#     schema = load_schema('encoded:schemas/surgery.json')
#     embeded = [] 
    


# @view_config(context=Pathology_report, permission='view', request_method='GET', name='page')
# def pathology_report_page_view(context, request):
#     if request.has_permission('view_details'):
#         properties = item_view_object(context, request)
#     else:
#         item_path = request.resource_path(context)
#         properties = request.embed(item_path, '@@object')
#     for path in context.embedded:
#         expand_path(request, properties, path)
#     return properties


# @view_config(context=Pathology_report, permission='view', request_method='GET',
#              name='object')
# def pathology_report_basic_view(context, request):
#     properties = item_view_object(context, request)
#     filtered = {}
#     for key in ['@id', '@type', 'accession', 'uuid', 'patient','surgery']:
#         try:
#             filtered[key] = properties[key]
#         except KeyError:
#             pass
#     return filtered    