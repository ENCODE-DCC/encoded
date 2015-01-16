from ..schema_utils import (
    load_schema,
)
from ..contentbase import (
    calculated_property,
    collection,
)
from .base import (
    Item,
    paths_filtered_by_status,
)
from itertools import chain
from urllib.parse import quote_plus
from urllib.parse import urljoin


def file_is_revoked(request, path):
    return request.embed(path, '@@object').get('status') == 'revoked'


@collection(
    name='datasets',
    unique_key='accession',
    properties={
        'title': 'Datasets',
        'description': 'Listing of datasets',
    })
class Dataset(Item):
    item_type = 'dataset'
    schema = load_schema('dataset.json')
    embedded = [
        'files',
        'files.replicate',
        'files.replicate.experiment',
        'files.replicate.experiment.lab',
        'files.replicate.experiment.target',
        'files.submitted_by',
        'revoked_files',
        'revoked_files.replicate',
        'revoked_files.replicate.experiment',
        'revoked_files.replicate.experiment.lab',
        'revoked_files.replicate.experiment.target',
        'revoked_files.submitted_by',
        'submitted_by',
        'lab',
        'award',
        'documents.lab',
        'documents.award',
        'documents.submitted_by',
    ]
    audit_inherit = [
        'original_files',
        'revoked_files',
        'submitted_by',
        'lab',
        'award',
        'documents.lab',
    ]
    name_key = 'accession'
    rev = {
        'original_files': ('file', 'dataset'),
    }

    @calculated_property(schema={
        "title": "Original files",
        "type": "array",
        "items": {
            "type": ['string', 'object'],
            "linkFrom": "file.dataset",
        },
    })
    def original_files(self, request, original_files):
        return paths_filtered_by_status(request, original_files)

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
        "title": "Related files",
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
        "type": "string",
    })
    def assembly(self, request, original_files, related_files):
        for path in chain(original_files, related_files):
            properties = request.embed(path, '@@object')
            if properties['file_format'] in ['bigWig', 'bigBed', 'narrowPeak', 'broadPeak'] and \
                    properties['status'] in ['released']:
                if 'assembly' in properties:
                    return properties['assembly']

    @calculated_property(condition='assembly', schema={
        "title": "Hub",
        "type": "string",
    })
    def hub(self, request):
        return request.resource_path(self, '@@hub', 'hub.txt')

    @classmethod
    def expand_page(cls, request, properties):
        properties = super(Dataset, cls).expand_page(request, properties)
        if 'hub' in properties:
            hub_url = urljoin(request.resource_url(request.root), properties['hub'])
            properties = properties.copy()
            hgTracks = 'http://genome.ucsc.edu/cgi-bin/hgTracks?'
            properties['visualize_ucsc'] = hgTracks + '&'.join([
                'db=' + quote_plus(properties['assembly']),
                'hubUrl=' + quote_plus(hub_url, ':/@'),
            ])
        return properties
