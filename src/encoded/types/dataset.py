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
    CalculatedSynonyms
)

from itertools import chain


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
    name='analysis-file-sets',
    properties={
        'title': "Analysis file set",
        'description': 'Listing of analysis file sets',
    })
class AnalysisFileSet(Dataset):
    item_type = 'analysis_file_set'
    base_types = [Dataset.__name__] + Dataset.base_types
    schema = load_schema('encoded:schemas/analysis_file_set.json')
    embedded = Dataset.embedded

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


@collection(
    name='annotations',
    properties={
        'title': "Annotation analysis set",
        'description': 'A set of annotation files produced by ENCODE.',
    })
class Annotation(AnalysisFileSet, CalculatedSlims, CalculatedSynonyms):
    item_type = 'annotation'
    base_types = [AnalysisFileSet.__name__] + AnalysisFileSet.base_types
    schema = load_schema('encoded:schemas/annotation.json')
    embedded = AnalysisFileSet.embedded + ['software_used', 'software_used.software', 'organism']


@collection(
    name='publication-data',
    properties={
        'title': "Publication analysis set",
        'description': 'A set of files that are described/analyzed in a publication.',
    })
class PublicationData(AnalysisFileSet):
    item_type = 'publication_data'
    base_types = [AnalysisFileSet.__name__] + AnalysisFileSet.base_types
    schema = load_schema('encoded:schemas/publication_data.json')


@collection(
    name='references',
    properties={
        'title': "Reference analysis set",
        'description': 'A set of reference files used by ENCODE.',
    })
class Reference(AnalysisFileSet):
    item_type = 'reference'
    base_types = [AnalysisFileSet.__name__] + AnalysisFileSet.base_types
    schema = load_schema('encoded:schemas/reference.json')
    embedded = AnalysisFileSet.embedded + ['software_used', 'software_used.software', 'organism']


@collection(
    name='ucsc-browser-composites',
    properties={
        'title': "UCSC browser composite analysis set",
        'description': 'A set of files that comprise a composite at the UCSC genome browser.',
    })
class UcscBrowserComposite(AnalysisFileSet, CalculatedSlims, CalculatedSynonyms):
    item_type = 'ucsc_browser_composite'
    base_types = [AnalysisFileSet.__name__] + AnalysisFileSet.base_types
    schema = load_schema('encoded:schemas/ucsc_browser_composite.json')
    embedded = AnalysisFileSet.embedded + ['organism']


@collection(
    name='projects',
    properties={
        'title': "Project analysis set",
        'description': 'A set of files that comprise a project.',
    })
class Project(AnalysisFileSet):
    item_type = 'project'
    base_types = [AnalysisFileSet.__name__] + AnalysisFileSet.base_types
    schema = load_schema('encoded:schemas/project.json')


@collection(
    name='series',
    properties={
        'title': "Series-type dataset",
        'description': 'A dataset that references other datasets.',
    })
class Series(Dataset):
    item_type = 'series'
    base_types = [Dataset.__name__] + Dataset.base_types
    schema = load_schema('encoded:schemas/series.json')
    embedded = Dataset.embedded


@collection(
    name='paired-sets',
    properties={
        'title': "Paired Set Series",
        'description': 'A series that pairs two datasets (experiments) together',
    })
class PairedSet(Series, CalculatedSlims, CalculatedSynonyms):
    item_type = 'paired_set'
    base_types = [Series.__name__] + Series.base_types
    schema = load_schema('encoded:schemas/paired_set.json')
    embedded = Series.embedded + ['organism']


@collection(
    name='treatment-time-series',
    properties={
        'title': "Treatment time series",
        'description': 'A series that varies on treatment duration across an applied treatment.',
    })
class TreatmentTimeSeries(Series, CalculatedSlims, CalculatedSynonyms):
    item_type = 'treatment_time_series'
    base_types = [Series.__name__] + Series.base_types
    schema = load_schema('encoded:schemas/treatment_time_series.json')
    embedded = Series.embedded + ['organism']
