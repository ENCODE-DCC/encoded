from contentbase import (
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
    CalculatedSlims,
    CalculatedSynonyms,
    RelatedFiles
)


def file_is_revoked(request, path):
    return request.embed(path, '@@object').get('status') == 'revoked'


@collection(
    name='datasets',
    unique_key='accession',
    properties={
        'title': "Datasets",
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
        'contributing_files'
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
            "linkTo": "File",
        },
    })
    def contributing_files(self, request, original_files, status):
        derived_from = set()
        for path in original_files:
            properties = request.embed(path, '@@object')
            derived_from.update(
                paths_filtered_by_status(request, properties.get('derived_from', []))
            )
        outside_files = list(derived_from.difference(original_files))
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
            "linkTo": "File",
        },
    })
    def files(self, request, original_files, status):
        if status in ('release ready', 'released'):
            return paths_filtered_by_status(
                request, original_files,
                include=('released',),
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
            "linkTo": "File",
        },
    })
    def revoked_files(self, request, original_files):
        return [
            path for path in original_files
            if file_is_revoked(request, path)
        ]

    @calculated_property(define=True, schema={
        "title": "Assembly",
        "type": "array",
        "items": {
            "type": "string",
        },
    })
    def assembly(self, request, original_files):
        assembly = []
        for path in original_files:
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
        'title': "Annotation analysis set",
        'description': 'A set of annotation files produced by ENCODE.',
    })
class Annotation(Dataset, CalculatedSlims, CalculatedSynonyms, RelatedFiles):
    item_type = 'annotation'
    base_types = [Dataset.__name__] + Dataset.base_types
    schema = load_schema('encoded:schemas/annotation.json')
    embedded = Dataset.embedded + ['software_used', 'software_used.software', 'organism']


@collection(
    name='publication-data',
    properties={
        'title': "Publication analysis set",
        'description': 'A set of files that are described/analyzed in a publication.',
    })
class PublicationData(Dataset, RelatedFiles):
    item_type = 'publication_data'
    base_types = [Dataset.__name__] + Dataset.base_types
    schema = load_schema('encoded:schemas/publication_data.json')


@collection(
    name='references',
    properties={
        'title': "Reference analysis set",
        'description': 'A set of reference files used by ENCODE.',
    })
class Reference(Dataset, RelatedFiles):
    item_type = 'reference'
    base_types = [Dataset.__name__] + Dataset.base_types
    schema = load_schema('encoded:schemas/reference.json')
    embedded = Dataset.embedded + ['software_used', 'software_used.software', 'organism']


@collection(
    name='ucsc-browser-composites',
    properties={
        'title': "UCSC browser composite analysis set",
        'description': 'A set of files that comprise a composite at the UCSC genome browser.',
    })
class UcscBrowserComposite(Dataset, CalculatedSynonyms, RelatedFiles):
    item_type = 'ucsc_browser_composite'
    base_types = [Dataset.__name__] + Dataset.base_types
    schema = load_schema('encoded:schemas/ucsc_browser_composite.json')
    embedded = Dataset.embedded + ['organism']


@collection(
    name='projects',
    properties={
        'title': "Project analysis set",
        'description': 'A set of files that comprise a project.',
    })
class Project(Dataset, RelatedFiles):
    item_type = 'project'
    base_types = [Dataset.__name__] + Dataset.base_types
    schema = load_schema('encoded:schemas/project.json')
