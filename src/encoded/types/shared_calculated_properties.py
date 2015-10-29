from contentbase import (
    calculated_property
)

from .base import (
    paths_filtered_by_status,
)

from itertools import chain


def file_is_revoked(request, path):
    return request.embed(path, '@@object').get('status') == 'revoked'


class CalculatedSlims:

    @calculated_property(condition='biosample_term_id', schema={
        "title": "Organ slims",
        "type": "array",
        "items": {
            "type": "string",
        },
    })
    def organ_slims(self, registry, biosample_term_id):
        if biosample_term_id in registry['ontology']:
            return registry['ontology'][biosample_term_id]['organs']
        return []

    @calculated_property(condition='biosample_term_id', schema={
        "title": "System slims",
        "type": "array",
        "items": {
            "type": "string",
        },
    })
    def system_slims(self, registry, biosample_term_id):
        if biosample_term_id in registry['ontology']:
            return registry['ontology'][biosample_term_id]['systems']
        return []

    @calculated_property(condition='biosample_term_id', schema={
        "title": "Developmental slims",
        "type": "array",
        "items": {
            "type": "string",
        },
    })
    def developmental_slims(self, registry, biosample_term_id):
        if biosample_term_id in registry['ontology']:
            return registry['ontology'][biosample_term_id]['developmental']
        return []


class CalculatedSynonyms:

    @calculated_property(condition='biosample_term_id', schema={
        "title": "Biosample synonyms",
        "type": "array",
        "items": {
            "type": "string",
        },
    })
    def biosample_synonyms(self, registry, biosample_term_id):
        if biosample_term_id in registry['ontology']:
            return registry['ontology'][biosample_term_id]['synonyms']
        return []

    @calculated_property(condition='assay_term_id', schema={
        "title": "Assay synonyms",
        "type": "array",
        "items": {
            "type": "string",
        },
    })
    def assay_synonyms(self, registry, assay_term_id):
        if assay_term_id in registry['ontology']:
            return registry['ontology'][assay_term_id]['synonyms'] + [
                registry['ontology'][assay_term_id]['name'],
            ]
        return []


class RelatedFiles:

    @calculated_property(schema={
        "title": "Contributing files",
        "type": "array",
        "items": {
            "type": 'string',
            "linkTo": "file",
        },
    })
    def contributing_files(self, request, original_files, related_files, status):
        files = set(original_files + related_files)
        derived_from = set()
        for path in files:
            properties = request.embed(path, '@@object')
            derived_from.update(
                paths_filtered_by_status(request, properties.get('derived_from', []))
            )
        outside_files = list(derived_from.difference(files))
        if status in ('release ready', 'released'):
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
            "linkTo": "file",
        },
    })
    def files(self, request, original_files, related_files, status):
        if status in ('release ready', 'released'):
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
            "linkTo": "file",
        },
    })
    def revoked_files(self, request, original_files, related_files):
        return [
            path for path in chain(original_files, related_files)
            if file_is_revoked(request, path)
        ]

    @calculated_property(define=True, schema={
        "title": "Assembly",
        "type": "array",
        "items": {
            "type": "string",
        },
    })
    def assembly(self, request, original_files, related_files):
        assembly = []
        for path in chain(original_files, related_files):
            properties = request.embed(path, '@@object')
            if properties['file_format'] in ['bigWig', 'bigBed', 'narrowPeak', 'broadPeak', 'bedRnaElements', 'bedMethyl', 'bedLogR'] and \
                    properties['status'] in ['released']:
                if 'assembly' in properties:
                    assembly.append(properties['assembly'])
        return list(set(assembly))
