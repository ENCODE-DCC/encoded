from pyramid.traversal import find_root
from snovault import (
    calculated_property,
    collection,
    load_schema,
)
from .base import (
    ALLOW_SUBMITTER_ADD,
    Item,
    paths_filtered_by_status,
    SharedItem
)
from .biodataset import Biodataset
from .shared_calculated_properties import (
    CalculatedAssaySynonyms,
    CalculatedAssayTermID,
    CalculatedVisualize
)

from .biosample import (
    construct_biosample_summary,
    generate_summary_dictionary
)

from .assay_data import assay_terms


@collection(
    name='bioexperiments',
    unique_key='accession',
    properties={
        'title': 'Bioexperiments',
        'description': 'Bioexperiment information page',
    },
)
class Bioexperiment(Biodataset,
                    CalculatedAssaySynonyms,
                    CalculatedAssayTermID,
                    CalculatedVisualize):
    item_type = 'bioexperiment'
    schema = load_schema('encoded:schemas/bioexperiment.json')
    embedded = Biodataset.embedded + [
        'award',
        'lab',
        "submitted_by",
        'documents',
        'bioreplicate',
        'bioreplicate.biolibrary',
        'bioreplicate.biolibrary.documents',
        'bioreplicate.biolibrary.biospecimen',
        'bioreplicate.biolibrary.biospecimen.part_of',
        'bioreplicate.biolibrary.biospecimen.part_of',
        'possible_controls',
        'bioreplicate.biolibrary.biospecimen.documents',
        "references",
        "files",
        "files.platform",
        'related_series',


    ]
    rev = Biodataset.rev.copy()
    rev.update({
        'related_series': ('Bioseries', 'related_datasets'),
        'bioreplicate': ('Bioreplicate', 'bioexperiment'),
        'superseded_by': ('Bioexperiment', 'supersedes')

    })


    audit_inherit = [
        'original_files',
        'original_files.bioreplicate',
        'original_files.platform',
        'revoked_files',
        'revoked_files.bioreplicate',
        'submitted_by',
        'lab',
        'award',
        'documents',

    ]
    set_status_up = [
        'original_files',
        'bioreplicate',
        'documents',
    ]
    set_status_down = [
        'original_files',
        'bioreplicate',
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
        }
    })
    def biospecimen_summary(self, request, bioreplicate=None):
        biospecimen_summary_list = []

        biospecimen_summary_dict = {
            "accession": "",
            "openspecimen_id": "",
            "patient": "",
            "sample_type": "",
            "tissue_derivatives": "",
            "tissue_type": "",
            "anatomic_site": "",
            "species": "",
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
                        print(biospecimenObject)
                        if 'accession' in biospecimenObject:
                            biospecimen_summary_dict['accession'] = biospecimenObject['accession']
                        if 'patient' in biospecimenObject:
                            biospecimen_summary_dict['patient'] = biospecimenObject['patient']
                        if 'openspecimen_id' in biospecimenObject:
                            biospecimen_summary_dict['openspecimen_id'] = biospecimenObject['openspecimen_id']
                        if 'sample_type' in biospecimenObject:
                            biospecimen_summary_dict['sample_type'] = biospecimenObject['sample_type']
                        if "anatomic_site" in biospecimenObject:
                            biospecimen_summary_dict['anatomic_site'] = biospecimenObject['anatomic_site']
                        if 'tissue_derivatives' in biospecimenObject:
                            biospecimen_summary_dict['tissue_derivatives'] = biospecimenObject["tissue_derivatives"]
                        if 'tissue_type' in biospecimenObject:
                            biospecimen_summary_dict['tissue_type'] = biospecimenObject["tissue_type"]
                        if 'species' in biospecimenObject:
                            biospecimen_summary_dict['species'] = biospecimenObject["species"]
                        if 'primary_site' in biospecimenObject:
                            biospecimen_summary_dict['primary_site'] = biospecimenObject["primary_site"]

                        biospecimen_summary_list.append(biospecimen_summary_dict)

        return biospecimen_summary_list

    @calculated_property(schema={
        "title": "Replication type",
        "description": "Calculated field that indicates the replication model",
        "type": "string"
    })
    def replication_type(self, request, bioreplicate=None, assay_term_name=None):
        # ENCD-4251 loop through replicates and select one replicate, which has
        # the smallest technical_replicate_number, per biological replicate.
        # That replicate should have a libraries property which, as calculated
        # in replicate.libraries (ENCD-4251), should have collected all
        # possible technical replicates belong to the biological replicate.

        bio_rep_dict = {}

        for rep in bioreplicate:
            replicate_object = request.embed(rep, '@@object')
            if replicate_object['status'] == 'deleted':
                continue
            bio_rep_num = replicate_object['biological_replicate_number']
            if bio_rep_num not in bio_rep_dict:
                bio_rep_dict[bio_rep_num] = replicate_object
                continue
            tech_rep_num = replicate_object['technical_replicate_number']
            if tech_rep_num < bio_rep_dict[bio_rep_num]['technical_replicate_number']:
                bio_rep_dict[bio_rep_num] = replicate_object

        biospecimen_number_list = []

        for replicate_object in bio_rep_dict.values():
            if 'biolibrary' in replicate_object and replicate_object['biolibrary']:
                biolibraryObject = request.embed(replicate_object['biolibrary'], '@@object')


                if 'biospecimen' in biolibraryObject:
                    biospecimen_object = request.embed(biolibraryObject['biospecimen'], '@@object')
                    biospecimen_number_list.append(
                        replicate_object.get('biological_replicate_number')
                    )
                    biospecimen_species = biospecimen_object.get('species')
                    biospecimen_type = biospecimen_object.get('sample_type'),

            else:
                # REPLICATES WITH NO LIBRARIES WILL BE CAUGHT BY AUDIT (TICKET 3268)
                # If I have a replicate without a library,
                # I cannot make a call about the replicate structure
                return None

        #  exclude ENCODE2
        if (len(set(biospecimen_number_list)) < 2):
            return 'unreplicated'

        if biospecimen_type == 'cell line':
            return 'isogenic'



        return 'anisogenic'

    @calculated_property(schema={
        "title": "Superseded by",
        "type": "array",
        "items": {
            "type": ['string', 'object'],
            "linkFrom": "Bioexperiment.supersedes",
        },
        "notSubmittable": True,
    })
    def superseded_by(self, request, superseded_by):
        return paths_filtered_by_status(request, superseded_by)

    @calculated_property(schema={
        "title": "Biorelated series",
        "type": "array",
        "items": {
            "type": ['string', 'object'],
            "linkFrom": "Bioseries.related_datasets",
        },
        "notSubmittable": True,
    })
    def related_series(self, request, related_series):
        return paths_filtered_by_status(request, related_series)
