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
import re
from snovault.resource_views import item_view_object
from snovault.util import expand_path
from collections import defaultdict

def group_values_by_path(request, pathology_report):
    values_by_key = defaultdict(list)
    for path in pathology_report:
        properties = request.embed(path, '@@object?skip_calculated=true')
        values_by_key[properties.get('path_id')].append(properties)
    return dict(values_by_key)


@collection(
    name='surgery',
    unique_key='uuid',
    properties={
        'title': 'Surgery view',
        'description': 'Single Surgery related Pathology report',
    })
class Surgery_view(Item):
    item_type = 'surgery'
    schema = load_schema('encoded:schemas/surgery.json')
    name_key = 'uuid'
    
    embedded = [
        'pathology_report'
    ]
    rev = {
        # 'patient': ('Patient', 'pathology_report'),
        'pathology_report': ('PathologyReport', 'surgery'),
        # 'ihc': ('Ihc', 'pathology_report'),
    }
    audit_inherit = []
    set_status_up = []
    set_status_down = []

    @calculated_property( schema={
        "title": "PathologyReport",
        "type": "array",
        "items": {
            "type": "string",
            "linkTo": "PathologyReport",
        },
    })
    def pathology_report(self, request, pathology_report):
        return group_values_by_path(request, pathology_report)

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
    


# @view_config(context=Surgery_view, permission='view', request_method='GET', name='page')
# def surgery_report_page_view(context, request):
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