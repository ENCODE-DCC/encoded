
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
    name='bioexperiment',
    unique_key='accession',
    properties={
        'title': 'Bioxperiments',
        'description': 'Bioexperiment information page',
    },
)
class Bioexperiment(Item):
    item_type = 'bioexperiment'
    schema = load_schema('encoded:schemas/bioexperiment.json')
    name_key = 'accession'
    rev = {
        'bioreplicate': ('Bioreplicate', 'bioexperiment'),

    }
    embedded = [
        'award',
        'lab',
        'user',
        'biospecimen',
        'bioreplicate',
        'bioreplicate.biolibrary'
        'bioreplicate.biolibrary.biospecimen'
        
        # 'publication',
        # "biolibrary",# have biosample, need to add extraction method, lysis method,treatment, method...
        # "biolibrary.biospecimen",
        # "biolibrary.bioreplicate",
        # "biolibrary.bioreplicate.biofile",
        # "biolibrary.platform", #link to Platform

        #in mixin.json,linkto 'Publication'
        # 'document' #in mixin.json,linkto 'Publication'
    ]
  
    audit_inherit = [
    ]
    set_status_up = [
        # 'documents',
    ]
    set_status_down = [
    ]
    
    @calculated_property(
        schema={
            "title": "Bioreplicate",
            "type": "array",
            "items": {
                "type": 'string',
                "linkTo": "Bioreplicate"
            },
        }
    )
    def bioreplicate(self, request, bioreplicate):
        return paths_filtered_by_status(request, bioreplicate)
    

  


    

    
   
