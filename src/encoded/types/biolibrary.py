from snovault import (
    calculated_property,
    collection,
    load_schema,
)
from .base import (
    Item,
    paths_filtered_by_status,
)
import re


@collection(
    name='biolibraries',
    unique_key='accession',
    properties={
        'title': 'Biolibraries',
        'description': 'Biolibraries used or available',
    })
class Biolibrary(Item):
    item_type = 'biolibrary'
    schema = load_schema('encoded:schemas/biolibrary.json')
    name_key = 'accession'
    rev = {
        'parent_of': ('Biospecimen', 'originated_from'),
    }
    embedded = [
      
    ]
   
