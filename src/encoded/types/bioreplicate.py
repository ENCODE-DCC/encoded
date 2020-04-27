from snovault import (
    calculated_property,
    collection,
    load_schema,
)
from .base import (
    ALLOW_SUBMITTER_ADD,
    Item,
    paths_filtered_by_status,
)
import re


@collection(
    name='bioreplicates',
    # acl=ALLOW_SUBMITTER_ADD,
    unique_key='accession',
    properties={
        'title': 'bioreplicates',
        'description': 'listing of bioreplicates',
    })
class bioreplicate(Item):
    item_type = 'bioreplicate'
    schema = load_schema('encoded:schemas/bioreplicate.json')

    rev = {

    }
    embedded = [
        'biolibrary',
        'biolibrary.biospecimen'
    ]
    audit_inherit = [
    ]
    set_status_up = [

    ]
    set_status_down = []
