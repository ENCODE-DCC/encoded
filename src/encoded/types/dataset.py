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
)
from pyramid.traversal import (
    find_resource,
)
from urllib import quote_plus
from urlparse import urljoin


def file_is_revoked(file, root):
    item = find_resource(root, file)
    return item.upgrade_properties()['status'] == 'revoked'


def file_not_revoked(file, root):
    item = find_resource(root, file)
    return item.upgrade_properties()['status'] != 'revoked'


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
            'files': [
                {
                    '$value': '{file}',
                    '$repeat': ('file', 'original_files', file_not_revoked),
                    '$templated': True,
                },
                {
                    '$value': '{file}',
                    '$repeat': ('file', 'related_files', file_not_revoked),
                    '$templated': True,
                },
            ],
            'revoked_files': [
                {
                    '$value': '{file}',
                    '$repeat': ('file', 'original_files', file_is_revoked),
                    '$templated': True,
                },
                {
                    '$value': '{file}',
                    '$repeat': ('file', 'related_files', file_is_revoked),
                    '$templated': True,
                },
            ],
            'hub': {'$value': '{item_uri}@@hub/hub.txt', '$templated': True, '$condition': 'assembly'},
            'assembly': {'$value': '{assembly}', '$templated': True, '$condition': 'assembly'},
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
        name_key = 'accession'
        keys = ACCESSION_KEYS + ALIAS_KEYS
        rev = {
            'original_files': ('file', 'dataset'),
        }

        def template_namespace(self, properties, request=None):
            ns = super(Dataset.Item, self).template_namespace(properties, request)
            if request is None:
                return ns
            for link in ns['original_files'] + ns['related_files']:
                f = find_resource(request.root, link)
                if f.properties['file_format'] in ['bigWig', 'bigBed', 'narrowPeak', 'broadPeak'] and \
                        f.properties['status'] in ['released']:
                    if 'assembly' in f.properties:
                        ns['assembly'] = f.properties['assembly']
                        break
            return ns

        @classmethod
        def expand_page(cls, request, properties):
            properties = super(Dataset.Item, cls).expand_page(request, properties)
            if 'hub' in properties:
                hub_url = urljoin(request.resource_url(request.root), properties['hub'])
                properties = properties.copy()
                properties['visualize_ucsc'] = 'http://genome.ucsc.edu/cgi-bin/hgTracks?' + '&'.join([
                    'db=' + quote_plus(properties['assembly']),
                    'hubUrl=' + quote_plus(hub_url, ':/@'),
                ])
            return properties
