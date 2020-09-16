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

from itertools import chain
import datetime


def item_is_revoked(request, path):
    return request.embed(path, '@@object?skip_calculated=true').get('status') == 'revoked'


def calculate_refver(request, files_list, status):
    refver = set()
    viewable_file_status = ['released','in progress']

    for path in files_list:
        properties = request.embed(path, '@@object?skip_calculated=true')
        if properties['status'] in viewable_file_status:
            if 'reference_version' in properties:
                refver.add(properties['reference_version'])
    return list(refver)


@collection(
    name='reference-file-sets',
    unique_key='accession',
    properties={
        'title': "Reference file sets",
        'description': 'A set of reference files used by ENCODE.',
    })
class ReferenceFileSet(Item):
    item_type = 'reference_file_set'
    schema = load_schema('encoded:schemas/reference_file_set.json')
    embedded = [
        'files'
    ]
    name_key = 'accession'
    rev = {
        'original_files': ('DataFile', 'dataset'),
    }

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
        "title": "Reference version",
        "type": "array",
        "items": {
            "type": "string",
        },
    })
    def reference_version(self, request, original_files, status):
        return calculate_refver(request, original_files, status)
