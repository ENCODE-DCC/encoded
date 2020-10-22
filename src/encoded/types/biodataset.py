from snovault import (
    abstract_collection,
    calculated_property,
    collection,
    load_schema,
)
from .base import (
    Item,
    paths_filtered_by_status,
)

from urllib.parse import quote_plus
from urllib.parse import urljoin
from .shared_calculated_properties import (
    CalculatedAssaySynonyms,
    CalculatedFileSetAssay,
    CalculatedFileSetBiosample,
    CalculatedSeriesAssay,
    CalculatedSeriesBiosample,
    CalculatedSeriesTreatment,
    CalculatedSeriesTarget,
    CalculatedVisualize
)

from itertools import chain
import datetime


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


@abstract_collection(
    name='biodatasets',
    unique_key='accession',
    properties={
        'title': "Biodatasets",
        'description': 'Listing of all types of dataset.',
    })
class Biodataset(Item):
    base_types = ['Biodataset'] + Item.base_types
    embedded = [
        'files',
        # 'files.replicate',
        # 'files.replicate.experiment',
        # 'files.replicate.experiment.lab',
        # 'files.replicate.experiment.target',
        # 'files.replicate.experiment.target.genes',
        # 'files.submitted_by',
        # 'files.lab',
        'revoked_files',
        # 'revoked_files.replicate',
        # 'revoked_files.replicate.experiment',
        # 'revoked_files.replicate.experiment.lab',
        # 'revoked_files.replicate.experiment.target',
        # 'revoked_files.replicate.experiment.target.genes',
        # 'revoked_files.submitted_by',
        'submitted_by',
        'lab',
        # 'award.pi.lab',
        'references'
    ]
    audit_inherit = [
        'original_files',
        'revoked_files',
        'contributing_files'
        'submitted_by',
        'lab',
        'award',
        'documents.lab',
    ]
    set_status_up = [
        'documents'
    ]
    set_status_down = []
    name_key = 'accession'
    rev = {
        'original_files': ('Biofile', 'biodataset'),
    }

    @calculated_property(schema={
        "title": "Original files",
        "type": "array",
        "items": {
            "type": ['string', 'object'],
            "linkFrom": "Biofile.biodataset",
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
            "linkTo": "Biofile",
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
            "linkTo": "Biofile",
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
            "linkTo": "Biofile",
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

    # @calculated_property(condition='assembly', schema={
    #     "title": "Hub",
    #     "type": "string",
    # })
    # def hub(self, request):
    #     return request.resource_path(self, '@@hub', 'hub.txt')

    @calculated_property(condition='date_released', schema={
        "title": "Month released",
        "type": "string",
    })
    def month_released(self, date_released):
        return datetime.datetime.strptime(date_released, '%Y-%m-%d').strftime('%B, %Y')

class FileSet(Biodataset):
    item_type = 'file_set'
    base_types = ['FileSet'] + Biodataset.base_types
    schema = load_schema('encoded:schemas/file_set.json')
    embedded = Biodataset.embedded

    @calculated_property(schema={
        "title": "Contributing files",
        "type": "array",
        "items": {
            "type": "string",
            "linkTo": "Biofile",
        },
    })
    def contributing_files(self, request, original_files, related_files, status):
        files = set(original_files + related_files)
        derived_from = set()
        for path in files:
            properties = request.embed(path, '@@object?skip_calculated=true')
            derived_from.update(
                paths_filtered_by_status(request, properties.get('derived_from', []))
            )
        outside_files = list(derived_from.difference(files))
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

    @calculated_property(define=True, schema={
        "title": "Files",
        "type": "array",
        "items": {
            "type": "string",
            "linkTo": "Biofile",
        },
    })
    def files(self, request, original_files, related_files, status):
        if status in ('released'):
            return paths_filtered_by_status(
                request, chain(original_files, related_files),
                include=('released',),
            )
        else:
            return paths_filtered_by_status(
                request, chain(original_files, related_files),
                exclude=('revoked', 'deleted', 'replaced'),
            )

    @calculated_property(schema={
        "title": "Revoked files",
        "type": "array",
        "items": {
            "type": "string",
            "linkTo": "Biofile",
        },
    })
    def revoked_files(self, request, original_files, related_files):
        return [
            path for path in chain(original_files, related_files)
            if item_is_revoked(request, path)
        ]

    @calculated_property(define=True, schema={
        "title": "Genome assembly",
        "type": "array",
        "items": {
            "type": "string",
        },
    })
    def assembly(self, request, original_files, related_files, status):
        return calculate_assembly(request, list(chain(original_files, related_files))[:101], status)