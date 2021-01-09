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
        'award',
        'references'
    ]
    rev = {
        'superseded_by': ('Dataset', 'supersedes'),
        'libraries': ('Library','dataset'),
        'original_files': ('DataFile','dataset')
    }
    audit_inherit = [
        'original_files',
        'original_files.derived_from',
        'libraries',
        'libraries.derived_from'
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
    def superseded_by(self, request, superseded_by):
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
    def libraries(self, request, libraries):
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
    def original_files(self, request, original_files):
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
    def contributing_files(self, request, original_files, status):
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
        "description": "The DataFiles that belong to this Dataset, filtered by status relative to the status of the Dataset.",
        "comment": "Do not submit. This is a calculated property",
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
        "description": "The DataFiles that are revoked and belong to this Dataset.",
        "comment": "Do not submit. This is a calculated property",
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
        "description": "The Genome assemblies used for references in the data analysis in this Dataset.",
        "comment": "Do not submit. This is a calculated property",
        "type": "array",
        "items": {
            "type": "string",
        },
    })
    def assembly(self, request, original_files, status):
        return calculate_assembly(request, original_files, status)
