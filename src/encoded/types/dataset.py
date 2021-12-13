from snovault import (
    calculated_property,
    collection,
    load_schema,
)
from .base import (
    Item,
    paths_filtered_by_status,
)


def item_is_revoked(request, path):
    return request.embed(path, '@@object?skip_calculated=true').get('status') == 'revoked'


def calculate_reference(request, files_list, ref_field):
    results = set()
    viewable_file_status = ['released','in progress']

    for path in files_list:
        properties = request.embed(path, '@@object?skip_calculated=true')
        if properties['status'] in viewable_file_status:
            if ref_field in properties:
                results.add(properties[ref_field])
    return list(results)


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
        'libraries.lab',
        'libraries.biosample_ontologies',
        'award',
        'award.coordinating_pi',
        'references',
        'corresponding_contributors',
        'contributors'
    ]
    rev = {
        'superseded_by': ('Dataset', 'supersedes'),
        'libraries': ('Library','dataset'),
        'original_files': ('DataFile','dataset')
    }
    audit_inherit = [
        'files',
        'files.derived_from',
        'files.cell_annotations',
        'libraries',
        'libraries.donors',
        'libraries.derived_from',
        'libraries.protocol'
    ]


    @calculated_property(schema={
        "title": "Superseded by",
        "description": "The Dataset that supersedes this one.",
        "comment": "Do not submit. This is a calculated property",
        "type": "array",
        "items": {
            "type": ['string', 'object'],
            "linkFrom": "Dataset.supersedes",
        },
        "notSubmittable": True,
    })
    def superseded_by(self, request, superseded_by=None):
        if superseded_by:
            return paths_filtered_by_status(request, superseded_by)


    @calculated_property(schema={
        "title": "Libraries",
        "description": "The Libraries that belong to this Dataset.",
        "comment": "Do not submit. This is a calculated property",
        "type": "array",
        "items": {
            "type": ['string', 'object'],
            "linkFrom": "Library.dataset",
        },
        "notSubmittable": True,
    })
    def libraries(self, request, libraries=None):
        if libraries:
            return paths_filtered_by_status(request, libraries)


    @calculated_property(schema={
        "title": "Original files",
        "description": "The DataFiles that belong to this Dataset, regardless of status.",
        "comment": "Do not submit. This is a calculated property",
        "type": "array",
        "items": {
            "type": ['string', 'object'],
            "linkFrom": "DataFile.dataset",
        },
        "notSubmittable": True,
    })
    def original_files(self, request, original_files=None):
        if original_files:
            return paths_filtered_by_status(request, original_files)


    @calculated_property(schema={
        "title": "Contributing files",
        "description": "The DataFiles that contribute to this Dataset's data products but do not belong to this Dataset, typically reference files.",
        "comment": "Do not submit. This is a calculated property",
        "type": "array",
        "items": {
            "type": "string",
            "linkTo": "DataFile",
        },
    })
    def contributing_files(self, request, status, original_files=None):
        if original_files:
            derived_from = set()
            for f in original_files:
                f_obj = request.embed(f, '@@object?skip_calculated=true')
                f_df = f_obj.get('derived_from')
                if isinstance(f_df, str):
                    derived_from.add(f_df)
                else:
                    derived_from.update(f_df)

            outside_ids = list(derived_from.difference(original_files))
            outside_files = []
            for i in outside_ids:
                outsideObject = request.embed(i, '@@object')
                if 'File' in outsideObject.get('@type'):
                    outside_files.append(i)

            if status in ('released'):
                contributing = paths_filtered_by_status(
                    request, outside_files,
                    include=('released',),
                )
            else:
                contributing = paths_filtered_by_status(
                    request, outside_files,
                    exclude=('revoked', 'deleted', 'replaced'),
                )
            if contributing:
                return contributing


    @calculated_property(schema={
        "title": "Files",
        "description": "The DataFiles that belong to this Dataset, filtered by status relative to the status of the Dataset.",
        "comment": "Do not submit. This is a calculated property",
        "type": "array",
        "items": {
            "type": "string",
            "linkTo": "DataFile",
        },
    })
    def files(self, request, status, original_files=None):
        if original_files:
            if status in ('in progress'):
                return paths_filtered_by_status(
                    request, original_files,
                    include=('released', 'in progress'),
                )
            elif status in ('released'):
                return paths_filtered_by_status(
                    request, original_files,
                    include=('released'),
                )
            elif status in ('archived'):
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
        "description": "The DataFiles that are revoked and belong to this Dataset.",
        "comment": "Do not submit. This is a calculated property",
        "type": "array",
        "items": {
            "type": "string",
            "linkTo": "DataFile",
        },
    })
    def revoked_files(self, request, original_files=None):
        if original_files:
            revoked = [
                path for path in original_files
                if item_is_revoked(request, path)
            ]
            if revoked:
                return revoked


    @calculated_property(define=True, schema={
        "title": "Reference assembly",
        "description": "The Genome assemblies used for references in the data analysis in this Dataset.",
        "comment": "Do not submit. This is a calculated property",
        "type": "array",
        "items": {
            "type": "string",
        },
    })
    def reference_assembly(self, request, original_files=None):
        if original_files:
            return calculate_reference(request, original_files, "assembly")


    @calculated_property(define=True, schema={
        "title": "Reference annotation",
        "description": "The genome annotations used for references in the data analysis in this Dataset.",
        "comment": "Do not submit. This is a calculated property",
        "type": "array",
        "items": {
            "type": "string",
        },
    })
    def reference_annotation(self, request, original_files=None):
        if original_files:
            return calculate_reference(request, original_files, "genome_annotation")
