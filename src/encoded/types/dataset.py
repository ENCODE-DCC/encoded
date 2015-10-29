from contentbase import (
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
from .shared_calculated_properties import (
    CalculatedSlims,
    CalculatedSynonyms
)


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
    schema = load_schema('encoded:schemas/dataset.json')
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
    properties={
        'title': "Annotation dataset",
        'description': 'A set of annotation files produced by ENCODE.',
    })
class Annotation(Dataset, CalculatedSlims, CalculatedSynonyms):
    item_type = 'annotation'
    schema = load_schema('encoded:schemas/annotation.json')
    base_types = [Dataset.__name__] + Dataset.base_types
    embedded = Dataset.embedded + ['software_used', 'software_used.software', 'organism', 'target']


@collection(
    name='publication_data',
    properties={
        'title': "Publication dataset",
        'description': 'A set of files that are described/analyzed in a publication.',
    })
class PublicationData(Dataset):
    item_type = 'publication_data'
    base_types = [Dataset.__name__] + Dataset.base_types
    schema = load_schema('encoded:schemas/publication_data.json')


@collection(
    name='references',
    properties={
        'title': "Reference dataset",
        'description': 'A set of reference files used by ENCODE.',
    })
class Reference(Dataset):
    item_type = 'reference'
    schema = load_schema('encoded:schemas/reference.json')
    base_types = [Dataset.__name__] + Dataset.base_types
    embedded = Dataset.embedded + ['software_used', 'software_used.software', 'organism']


@collection(
    name='ucsc_browser_composites',
    properties={
        'title': "UCSC browser composite dataset",
        'description': 'A set of files that comprise a composite at the UCSC genome browser.',
    })
class UcscBrowserComposite(Dataset, CalculatedSynonyms):
    item_type = 'ucsc_browser_composite'
    base_types = [Dataset.__name__] + Dataset.base_types
    schema = load_schema('encoded:schemas/ucsc_browser_composite.json')
    embedded = Dataset.embedded + ['organism']


@collection(
    name='projects',
    properties={
        'title': "Project dataset",
        'description': 'A set of files that comprise a project.',
    })
class Project(Dataset):
    item_type = 'project'
    base_types = [Dataset.__name__] + Dataset.base_types
    schema = load_schema('encoded:schemas/project.json')
