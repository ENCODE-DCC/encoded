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
from .dataset import Dataset
from .shared_calculated_properties import (
    CalculatedAssaySynonyms,
    CalculatedVisualize,
    CalculatedBiosampleSummary
)

@collection(
    name='experiments',
    unique_key='accession',
    properties={
        'title': 'Experiments',
        'description': 'Listing of Experiments',
    })
class Experiment(Dataset,
                 CalculatedAssaySynonyms,
                 CalculatedVisualize,
                 CalculatedBiosampleSummary):
    item_type = 'experiment'
    schema = load_schema('encoded:schemas/experiment.json')
    embedded = Dataset.embedded + []
    audit_inherit = []
    set_status_up = [
        'original_files',
        'documents',
        'target',
    ]
    set_status_down = [
        'original_files',
    ]
    rev = Dataset.rev.copy()
    rev.update({
        'superseded_by': ('Experiment', 'supersedes'),
        'libraries': ('Library','experiment')
    })

    @calculated_property(schema={
            "title": "Superseded by",
            "type": "array",
            "items": {
                "type": ['string', 'object'],
                "linkFrom": "Experiment.supersedes",
            },
            "notSubmittable": True,
    })
    def superseded_by(self, request, superseded_by):
        return paths_filtered_by_status(request, superseded_by)

    @calculated_property(schema={
        "title": "Libraries",
        "type": "array",
        "items": {
            "type": ['string', 'object'],
            "linkFrom": "Library.experiment",
        },
        "notSubmittable": True,
    })
    def libraries(self, request, libraries):
        return paths_filtered_by_status(request, libraries)

    @calculated_property(schema={
        "title": "Protein tags",
        "description": "The protein tags introduced through the genetic modifications of biosamples investigated in the experiment.",
        "comment": "Do not submit. This field is calculated through applied_modifications.",
        "type": "array",
        "notSubmittable": True,
        "minItems": 1,
        "items": {
            "title": "Protein tag",
            "description": "The protein tag introduced in the modification.",
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "name": {
                    "title": "Tag name",
                    "type": "string",
                    "enum": [
                        "3xFLAG",
                        "6XHis",
                        "DsRed",
                        "eGFP",
                        "ER",
                        "FLAG",
                        "GFP",
                        "HA",
                        "mCherry",
                        "T2A",
                        "TagRFP",
                        "TRE",
                        "V5",
                        "YFP",
                        "mAID-mClover",
                        "mAID-mClover-NeoR",
                        "mAID-mClover-Hygro"
                    ]
                },
                "location": {
                    "title": "Tag location",
                    "type": "string",
                    "enum": [
                        "C-terminal",
                        "internal",
                        "N-terminal",
                        "other",
                        "unknown"
                    ]
                },
                "target": {
                    "title": "Tagged protein",
                    "type": "string",
                    "linkTo": "Target",
                }
            }
        }
    })
    def protein_tags(self, request, replicates=None):
        protein_tags = []
        if replicates is not None:
            for rep in replicates:
                replicateObject = request.embed(rep, '@@object?skip_calculated=true')
                if replicateObject['status'] in ('deleted', 'revoked'):
                    continue
                if 'library' in replicateObject:
                    libraryObject = request.embed(replicateObject['library'], '@@object?skip_calculated=true')
                    if libraryObject['status'] in ('deleted', 'revoked'):
                        continue
                    if 'biosample' in libraryObject:
                        biosampleObject = request.embed(libraryObject['biosample'], '@@object')
                        if biosampleObject['status'] in ('deleted', 'revoked'):
                            continue
                        genetic_modifications = biosampleObject.get('applied_modifications')
                        if genetic_modifications:
                            for gm in genetic_modifications:
                                gm_object = request.embed(gm, '@@object?skip_calculated=true')
                                if gm_object.get('introduced_tags') is None:
                                    continue
                                if gm_object.get('introduced_tags'):
                                    for tag in gm_object.get('introduced_tags'):
                                        tag_dict = {'location': tag['location'], 'name': tag['name']}
                                        if gm_object.get('modified_site_by_target_id'):
                                            tag_dict.update({'target': gm_object.get('modified_site_by_target_id')})
                                            protein_tags.append(tag_dict)
        if len(protein_tags) > 0:
            return protein_tags

    # Don't specify schema as this just overwrites the existing value
    @calculated_property(condition='analyses')
    def analyses(self, request, analyses):
        updated_analyses = []
        for analysis in analyses:
            assemblies = set()
            genome_annotations = set()
            for f in analysis.get('files', []):
                file_object = request.embed(
                    f,
                    '@@object_with_select_calculated_properties?field=analysis_step'
                )
                if 'assembly' in file_object:
                    assemblies.add(file_object['assembly'])
                if 'genome_annotation' in file_object:
                    genome_annotations.add(file_object['genome_annotation'])
            analysis['assemblies'] = sorted(assemblies)
            analysis['genome_annotations'] = sorted(genome_annotations)
            updated_analyses.append(analysis)
        return analyses

    matrix = {
        'y': {
            'group_by': 'biosample_ontology.term_name',
            'label': 'Biosample',
        },
        'x': {
            'group_by': 'assay_title',
            'label': 'Assay',
        },
    }

    summary = {
        'x': {
            'group_by': 'status'
        },
        'y': {
            'group_by': ['replication_type']
        }
    }

    reference_epigenome = {
        'y': {
            'group_by': 'biosample_ontology.term_name',
            'label': 'Biosample',
        },
        'x': {
            'group_by': ['assay_title', 'target.label'],
            'label': 'Assay',
        },
    }
