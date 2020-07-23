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

def item_is_revoked(request, path):
    return request.embed(path, '@@object?skip_calculated=true').get('status') == 'revoked'


def calculate_assembly(request, files_list, status):
    assembly = set()
    viewable_file_status = ['released','in progress']

    for path in files_list:
        properties = request.embed(path, '@@object?skip_calculated=true')
        if properties['status'] in viewable_file_status:
            if 'assembly' in properties:
                assembly.add(properties['assembly'])
    return list(assembly)


@collection(
    name='datasets',
    unique_key='accession',
    properties={
        'title': 'Datasets',
        'description': 'Listing of Datasets',
    })
class Dataset(Item):
    item_type = 'dataset'
    schema = load_schema('encoded:schemas/dataset.json')
    name_key = 'accession'
    embedded = [
        'libraries',
        'libraries.protocol',
        'award',
        'files'
    ]
    rev = {
        'superseded_by': ('Dataset', 'supersedes'),
        'libraries': ('Library','dataset'),
        'original_files': ('DataFile','dataset')
    }

    @calculated_property(schema={
            "title": "Superseded by",
            "type": "array",
            "items": {
                "type": ['string', 'object'],
                "linkFrom": "Dataset.supersedes",
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
            "linkFrom": "Library.dataset",
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


    @calculated_property(condition='assay_term_id', schema={
        "title": "Assay synonyms",
        "type": "array",
        "items": {
            "type": "string",
        },
    })
    def assay_synonyms(self, registry, assay_term_id):
        assay_term_id = ensurelist(assay_term_id)
        syns = set()
        for term_id in assay_term_id:
            if term_id in registry['ontology']:
                syns.update(registry['ontology'][term_id]['synonyms'] + [
                    registry['ontology'][term_id]['name'],
                ])
        return list(syns)


    @calculated_property(schema={
        "title": "Original files",
        "type": "array",
        "items": {
            "type": ['string', 'object'],
            "linkFrom": "DataFile.dataset",
        },
        "notSubmittable": True,
    })
    def original_files(self, request, original_files):
        return paths_filtered_by_status(request, original_files)

    @calculated_property(schema={
        "title": "Contributing files",
        "type": "array",
        "items": {
            "type": "string",
            "linkTo": "DataFile",
        },
    })
    def contributing_files(self, request, original_files, status):
        derived_from = set()
        for path in original_files:
            properties = request.embed(path, '@@object?skip_calculated=true')
            derived_from.update(
                paths_filtered_by_status(request, properties.get('derived_from', []))
            )
        outside_files = list(derived_from.difference(original_files))
        if status in ('released'):
            return paths_filtered_by_status(
                request, outside_files,
                include=('released',),
            )
        else:
            return paths_filtered_by_status(
                request, outside_files,
                exclude=('revoked', 'deleted', 'replaced'),
            )

    @calculated_property(schema={
        "title": "Files",
        "type": "array",
        "items": {
            "type": "string",
            "linkTo": "DataFile",
        },
    })
    def files(self, request, original_files, status):
        if status in ('released', 'archived'):
            return paths_filtered_by_status(
                request, original_files,
                include=('released', 'archived'),
            )
        else:
            return paths_filtered_by_status(
                request, original_files,
                exclude=('revoked', 'deleted', 'replaced'),
            )

    @calculated_property(schema={
        "title": "Revoked files",
        "type": "array",
        "items": {
            "type": "string",
            "linkTo": "DataFile",
        },
    })
    def revoked_files(self, request, original_files):
        return [
            path for path in original_files
            if item_is_revoked(request, path)
        ]

    @calculated_property(define=True, schema={
        "title": "Genome assembly",
        "type": "array",
        "items": {
            "type": "string",
        },
    })
    def assembly(self, request, original_files, status):
        return calculate_assembly(request, original_files, status)

    @calculated_property(condition='assembly', schema={
        "title": "Hub",
        "type": "string",
    })
    def hub(self, request):
        return request.resource_path(self, '@@hub', 'hub.txt')

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
