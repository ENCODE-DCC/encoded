from ..schema_utils import (
    load_schema,
)
from ..contentbase import (
    location,
)
from .base import (
    ACCESSION_KEYS,
    ALIAS_KEYS,
    Collection,
    paths_filtered_by_status,
)
from itertools import chain
from pyramid.traversal import (
    find_resource,
)
from urllib import quote_plus
from urlparse import urljoin


def file_is_revoked(root, path):
    item = find_resource(root, path)
    return item.upgrade_properties()['status'] == 'revoked'


def assembly(root, original_files, related_files):
    for path in chain(original_files, related_files):
        f = find_resource(root, path)
        properties = f.upgrade_properties(finalize=False)
        if properties['file_format'] in ['bigWig', 'bigBed', 'narrowPeak', 'broadPeak'] and \
                properties['status'] in ['released']:
            if 'assembly' in properties:
                return properties['assembly']
    return None


@location('datasets')
class Dataset(Collection):
    item_type = 'dataset'
    schema = load_schema('dataset.json')
    properties = {
        'title': 'Datasets',
        'description': 'Listing of datasets',
    }

    class Item(Collection.Item):
        template = {
            # XXX Still needed?
            'original_files': (
                lambda root, original_files: paths_filtered_by_status(root, original_files)
            ),
            'files': (
                lambda root, original_files, related_files: paths_filtered_by_status(
                    root, chain(original_files, related_files),
                    exclude=('revoked', 'deleted', 'replaced'),
                )
            ),
            'revoked_files': (
                lambda root, original_files, related_files: [
                    path for path in chain(original_files, related_files)
                    if file_is_revoked(root, path)
                ]
            ),
            'hub': {
                '$value': '{item_uri}@@hub/hub.txt',
                '$condition': assembly,
            },
            'assembly': {
                '$value': assembly,
                '$condition': assembly,
            },
        }
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
        keys = ACCESSION_KEYS + ALIAS_KEYS
        rev = {
            'original_files': ('file', 'dataset'),
        }

        @classmethod
        def expand_page(cls, request, properties):
            properties = super(Dataset.Item, cls).expand_page(request, properties)
            if 'hub' in properties:
                hub_url = urljoin(request.resource_url(request.root), properties['hub'])
                properties = properties.copy()
                hgTracks = 'http://genome.ucsc.edu/cgi-bin/hgTracks?'
                properties['visualize_ucsc'] = hgTracks + '&'.join([
                    'db=' + quote_plus(properties['assembly']),
                    'hubUrl=' + quote_plus(hub_url, ':/@'),
                ])
            return properties
