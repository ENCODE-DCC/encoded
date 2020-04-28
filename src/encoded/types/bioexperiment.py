
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
import re


@collection(
    name='bioexperiments',
    unique_key='accession',
    properties={
        'title': 'Bioxperiments',
        'description': 'Bioexperiment information page',
    })
class Bioexperiment(Item):
    item_type = 'bioexperiment'
    schema = load_schema('encoded:schemas/bioexperiment.json')
    # name_key = 'accession'
    rev = {
        'bioreplicate': ('Bioreplicate', 'bioexperiment'),

    }
    embedded = [
        'biospecimen',
        'bioreplicate',
        'award',
        'lab',
        'user'

        # "biolibrary",# have biosample, need to add extraction method, lysis method,treatment, method...
        # "biolibrary.biospecimen",
        # "biolibrary.bioreplicate",
        # "biolibrary.bioreplicate.biofile",
        # "biolibrary.platform", #link to Platform

        # "references", #in mixin.json,linkto 'Publication'
        # 'document' #in mixin.json,linkto 'Publication'
    ]
  
    audit_inherit = [
        'submitted_by',
        'lab',
        'award',
        'documents',
        # 'references'

        ]
    set_status_up = [
        # 'documents',
    ]
    set_status_down = [
    ]
    
    @calculated_property(schema={
        "title": "Bioreplicate",
        "type": "array",
        "items": {
            "type": 'string',
            "linkTo": "Bioreplicate"
        },
    })
    def bioreplicate(self, request, bioreplicate):
        return paths_filtered_by_status(request, bioreplicate)
    

  


    

    
   
