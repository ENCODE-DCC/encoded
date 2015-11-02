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
import datetime


def item_is_revoked(request, path):
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
            if item_is_revoked(request, path)
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

    @calculated_property(condition='date_released', schema={
        "title": "Month released",
        "type": "string",
    })
    def month_released(self, date_released):
        return datetime.datetime.strptime(date_released, '%Y-%m-%d').strftime('%B, %Y')


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
    embedded = Dataset.embedded + [
        'files.replicate.antibody',
        'files.replicate.experiment.target.organism',
        'files.replicate.library',
        'files.replicate.library.biosample',
        'files.replicate.library.biosample.donor',
        'files.replicate.library.biosample.donor.organism',
        'files.replicate.library.biosample.rnais',
        'files.replicate.experiment.possible_controls'
    ]

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
            if item_is_revoked(request, path)
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
    embedded = Dataset.embedded + [
        'award.pi.lab',
        'references',
        'related_datasets.lab',
        'related_datasets.submitted_by',
        'related_datasets.award.pi.lab',
        'related_datasets.replicates.antibody',
        'related_datasets.replicates.antibody.targets',
        'related_datasets.replicates.library',
        'related_datasets.replicates.library.documents.lab',
        'related_datasets.replicates.library.documents.submitted_by',
        'related_datasets.replicates.library.documents.award',
        'related_datasets.replicates.library.biosample.submitted_by',
        'related_datasets.replicates.library.biosample.source',
        'related_datasets.replicates.library.biosample.organism',
        'related_datasets.replicates.library.biosample.rnais',
        'related_datasets.replicates.library.biosample.donor.organism',
        'related_datasets.replicates.library.biosample.donor.mutated_gene',
        'related_datasets.replicates.library.biosample.treatments',
        'related_datasets.replicates.library.spikeins_used',
        'related_datasets.replicates.library.treatments',
        'related_datasets.possible_controls',
        'related_datasets.possible_controls.target',
        'related_datasets.possible_controls.lab',
        'related_datasets.target.organism',
        'related_datasets.references',
        'files.lab',
        'files.platform',
        'files.lab',
        'files.derived_from',
        'files.derived_from.replicate',
        'files.analysis_step_version.analysis_step',
        'files.analysis_step_version.analysis_step.pipelines',
        'files.analysis_step_version.analysis_step.versions',
        'files.analysis_step_version.analysis_step.versions.software_versions',
        'files.analysis_step_version.analysis_step.versions.software_versions.software',
        'files.analysis_step_version.software_versions',
        'files.analysis_step_version.software_versions.software',
        'files.replicate.library.biosample',
        'files.quality_metrics',
        'files.quality_metrics.step_run',
        'files.quality_metrics.step_run.analysis_step_version.analysis_step',
        'contributing_files.platform',
        'contributing_files.lab',
        'contributing_files.derived_from',
        'contributing_files.analysis_step_version.analysis_step',
        'contributing_files.analysis_step_version.analysis_step.pipelines',
        'contributing_files.analysis_step_version.software_versions',
        'contributing_files.analysis_step_version.software_versions.software'
    ]

    @calculated_property(schema={
        "title": "Revoked datasets",
        "type": "array",
        "items": {
            "type": "string",
            "linkTo": "file",
        },
    })
    def revoked_datasets(self, request, related_datasets):
        return [
            path for path in related_datasets
            if item_is_revoked(request, path)
        ]

    @calculated_property(define=True, schema={
        "title": "Assembly",
        "type": "array",
        "items": {
            "type": "string",
        },
    })
    def assembly(self, request, related_datasets):
        assembly = []
        for path in related_datasets:
            properties = request.embed(path, '@@object')
            if 'assembly' in properties:
                assembly.extend(properties['assembly'])
        return list(set(assembly))


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
    embedded = Series.embedded


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
    embedded = Series.embedded


@collection(
    name='treatment-concentration-series',
    properties={
        'title': "Treatment concentration series",
        'description': 'A series that varies on treatment concentration across an applied treatment.',
    })
class TreatmentConcentrationSeries(Series, CalculatedSlims, CalculatedSynonyms):
    item_type = 'treatment_concentration_series'
    base_types = [Series.__name__] + Series.base_types
    schema = load_schema('encoded:schemas/treatment_concentration_series.json')
    embedded = Series.embedded


@collection(
    name='organism-development-series',
    properties={
        'title': "Organism development series",
        'description': 'A series that varies age/life stage of an organism.',
    })
class OrganismDevelopmentSeries(Series, CalculatedSlims, CalculatedSynonyms):
    item_type = 'organism_development_series'
    base_types = [Series.__name__] + Series.base_types
    schema = load_schema('encoded:schemas/organism_development_series.json')
    embedded = Series.embedded


@collection(
    name='replication-timing-series',
    properties={
        'title': "Replication timing series",
        'description': 'A series tracking replication timing over the cell cycle.',
    })
class ReplicationTimingSeries(Series, CalculatedSlims, CalculatedSynonyms):
    item_type = 'replication_timing_series'
    base_types = [Series.__name__] + Series.base_types
    schema = load_schema('encoded:schemas/replication_timing_series.json')
    embedded = Series.embedded


@collection(
    name='complete-epigenome-series',
    properties={
        'title': "Complete epigenome series",
        'description': 'A series made up of complimentary assays that define a complete epigenome according to IHEC.',
    })
class CompleteEpigenomeSeries(Series, CalculatedSlims, CalculatedSynonyms):
    item_type = 'complete_epigenome_series'
    base_types = [Series.__name__] + Series.base_types
    schema = load_schema('encoded:schemas/complete_epigenome_series.json')
    embedded = Series.embedded
