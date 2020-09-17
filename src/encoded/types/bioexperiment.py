
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
    name='bioexperiments',
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
    embedded = [
        'award',
        'lab',
        "submitted_by",  # link to User
        # 'biospecimen',
        'documents',  # link to Document
        'bioreplicate',
        'bioreplicate.biolibrary',
        'bioreplicate.biolibrary.documents',
        'bioreplicate.biolibrary.biospecimen',
        'bioreplicate.biolibrary.biospecimen.documents',
        "references"  # link to Publication


    ]
    rev = {
        'bioreplicate': ('Bioreplicate', 'bioexperiment'),

    }

    audit_inherit = [

    ]
    set_status_up = [
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

    @calculated_property(schema={
        "title": "Biospecimen summary",
        "type": "array",
        "items": {
            "comment": "See experiment.json for a list of available identifiers.",
            "type": "object",
                    # "linkTo": "Experiment"
        }
    })
    def biospecimen_summary(self,
                            request,
                            bioreplicate=None):
        biospecimen_summary_list = []

  # "species": "mouse_related_info", "patient","collection_date, "sample_type",detailed sample type, "anatomic_site", "initial_quantity", "initial_quantiy_units",
  # "preservation_method":,  "donor", "host_biosample",   "pooled_from", "part_of",

        biospecimen_summary_dict = {
            "accession": "",
            "openspecimen_ID": "",
            "patient": "",
            "collection_type": "",
            "processing_type": "",
            "tissue_type": "",
            "anatomic_site": "",
            "host": "",
            "primary_site": "",
        }
        if bioreplicate is not None:
            for biorep in bioreplicate:
                bioreplicateObject = request.embed(biorep, '@@object')
                if bioreplicateObject['status'] == 'deleted':
                    continue
                if 'biolibrary' in bioreplicateObject:
                    biolibraryObject = request.embed(bioreplicateObject['biolibrary'], '@@object')
                    if biolibraryObject['status'] == 'deleted':
                        continue
                    if 'biospecimen' in biolibraryObject:
                        biospecimenObject = request.embed(
                            biolibraryObject['biospecimen'], '@@object')
                        if biospecimenObject['status'] == 'deleted':
                            continue
                      
                        if 'accession' in biospecimenObject:
                            biospecimen_summary_dict['accession'] = biospecimenObject['accession']
                        if 'patient' in biospecimenObject:
                            biospecimen_summary_dict['patient'] = biospecimenObject['patient']
                        if 'openspecimen_ID' in biospecimenObject:
                            biospecimen_summary_dict['openspecimen_ID'] = biospecimenObject['openspecimen_ID']
                        if 'collection_type' in biospecimenObject:
                            biospecimen_summary_dict['collection_type'] = biospecimenObject['collection_type']
                        if "anatomic_site" in biospecimenObject:
                            biospecimen_summary_dict['anatomic_site'] = biospecimenObject['anatomic_site']
                        if 'processing_type' in biospecimenObject:
                            biospecimen_summary_dict['processing_type'] = biospecimenObject["processing_type"]
                        if 'tissue_type' in biospecimenObject:
                            biospecimen_summary_dict['tissue_type'] = biospecimenObject["tissue_type"]
                        if 'host' in biospecimenObject:
                            biospecimen_summary_dict['host'] = biospecimenObject["host"]
                        if 'primary_site' in biospecimenObject:
                            biospecimen_summary_dict['primary_site'] = biospecimenObject["primary_site"]

                            biospecimen_summary_list.append(biospecimen_summary_dict)

        return biospecimen_summary_list
