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
    acl=ALLOW_SUBMITTER_ADD,
    properties={
        'title': 'Bioreplicates',
        'description': 'Listing of BioReplicates',
    })
class Bioreplicate(Item):
    item_type = 'bioreplicate'
    schema = load_schema('encoded:schemas/bioreplicate.json')
    rev = {
        'biofile': ('Biofile', 'bioreplicate'),
    }

    embedded = [
        'bioexperiment',
        'biolibrary',
        'biolibrary.biospecimen',
        'biolibrary.biospecimen.patient.accession',
        'biofile'
    ]
    audit_inherit = [
    ]
    set_status_up = [
    ]
    set_status_down = []

    @calculated_property(
        schema={
            "title": "Biofile",
            "type": "array",
            "items": {
                "type": 'string',
                "linkTo": "Biofile"
            },
        }
    )
    def biofile(self, request, biofile):
        return paths_filtered_by_status(request, biofile)
