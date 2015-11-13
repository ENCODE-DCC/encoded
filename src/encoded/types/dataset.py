from contentbase import (
    abstract_collection,
    calculated_property,
    collection,
    load_schema,
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


@abstract_collection(
    name='datasets',
    unique_key='accession',
    properties={
        'title': "Datasets",
        'description': 'Listing of all types of dataset.',
    })
class Dataset(Item):
    base_types = ['Dataset'] + Item.base_types
    embedded = [
        'files',
        'files.replicate',
        'files.replicate.experiment',
        'files.replicate.experiment.lab',
        'files.replicate.experiment.target',
        'files.submitted_by',
        'files.lab',
        'revoked_files',
        'revoked_files.replicate',
        'revoked_files.replicate.experiment',
        'revoked_files.replicate.experiment.lab',
        'revoked_files.replicate.experiment.target',
        'revoked_files.submitted_by',
        'contributing_files',
        'contributing_files.replicate.experiment',
        'contributing_files.replicate.experiment.lab',
        'contributing_files.replicate.experiment.target',
        'contributing_files.submitted_by',
        'submitted_by',
        'lab',
        'award',
        'documents.lab',
        'documents.award',
        'documents.submitted_by',
        'references'
    ]
    audit_inherit = [
        'original_files',
        'revoked_files',
        'contributing_files',
        'submitted_by',
        'lab',
        'award',
        'documents.lab',
    ]
    name_key = 'accession'
    rev = {
        'original_files': ('File', 'dataset'),
    }

    @calculated_property(schema={
        "title": "Original files",
        "type": "array",
        "items": {
            "type": ['string', 'object'],
            "linkFrom": "File.dataset",
        },
    })
    def original_files(self, request, original_files):
        return paths_filtered_by_status(request, original_files)

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

    @calculated_property(condition='assembly', schema={
        "title": "Hub",
        "type": "string",
    })
    def hub(self, request):
        return request.resource_path(self, '@@hub', 'hub.txt')

    @calculated_property(condition='hub', category='page', schema={
        "title": "Visualuze at UCSC",
        "type": "string",
    })
    def visualize_ucsc(self, request, hub):
        hub_url = urljoin(request.resource_url(request.root), hub)
        return (
            'http://genome.ucsc.edu/cgi-bin/hgHubConnect'
            '?hgHub_do_redirect=on'
            '&hgHubConnect.remakeTrackHub=on'
            '&hgHub_do_firstDb=1&hubUrl='
        ) + quote_plus(hub_url, ':/@')


@collection(
    name='annotations',
    unique_key='accession',
    properties={
        'title': "Annotation dataset",
        'description': 'A set of annotation files produced by ENCODE.',
    })
class Annotation(Dataset):
    item_type = 'annotation'
    schema = load_schema('encoded:schemas/dataset.json')
    schema['properties']['dataset_type']['enum'] = ['annotation']


@collection(
    name='publication-data',
    unique_key='accession',
    properties={
        'title': "Publication dataset",
        'description': 'A set of files that are described/analyzed in a publication.',
    })
class PublicationData(Dataset):
    item_type = 'publication_data'
    schema = load_schema('encoded:schemas/dataset.json')
    schema['properties']['dataset_type']['enum'] = ['publication']


@collection(
    name='references',
    unique_key='accession',
    properties={
        'title': "Reference dataset",
        'description': 'A set of reference files used by ENCODE.',
    })
class Reference(Dataset):
    item_type = 'reference'
    schema = load_schema('encoded:schemas/dataset.json')
    schema['properties']['dataset_type']['enum'] = ['reference']


@collection(
    name='ucsc-browser-composites',
    unique_key='accession',
    properties={
        'title': "UCSC browser composite dataset",
        'description': 'A set of files that comprise a composite at the UCSC genome browser.',
    })
class UcscBrowserComposite(Dataset):
    item_type = 'ucsc_browser_composite'
    schema = load_schema('encoded:schemas/dataset.json')
    schema['properties']['dataset_type']['enum'] = ['composite']


@collection(
    name='projects',
    unique_key='accession',
    properties={
        'title': "Project dataset",
        'description': 'A set of files that comprise a project.',
    })
class Project(Dataset):
    item_type = 'project'
    schema = load_schema('encoded:schemas/dataset.json')
    schema['properties']['dataset_type']['enum'] = ['project']


@collection(
    name='matched-sets',
    unique_key='accession',
    properties={
        'title': "Matched set series",
        'description': 'A series that pairs two datasets (experiments) together',
    })
class MatchedSet(Dataset):
    item_type = 'matched_set'
    schema = load_schema('encoded:schemas/dataset.json')
    schema['properties']['dataset_type']['enum'] = ['paired set']
