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
from .shared_calculated_properties import (
    CalculatedBiosampleSlims,
    CalculatedBiosampleSynonyms,
    CalculatedAssaySynonyms,
    CalculatedFileSetAssay,
    CalculatedFileSetBiosample,
    CalculatedSeriesAssay,
    CalculatedSeriesBiosample,
    CalculatedSeriesTreatment,
    CalculatedSeriesTarget
)

from itertools import chain
import datetime
from ..visualization import vis_format_external_url


def item_is_revoked(request, path):
    return request.embed(path, '@@object').get('status') == 'revoked'


def calculate_assembly(request, files_list, status):
    assembly = set()
    viewable_file_formats = ['bigWig',
                             'bigBed',
                             'narrowPeak',
                             'broadPeak',
                             'bedRnaElements',
                             'bedMethyl',
                             'bedLogR']
    viewable_file_status = ['released']
    if status not in ['released']:
        viewable_file_status.extend(['in progress'])

    for path in files_list:
        properties = request.embed(path, '@@object')
        if properties['file_format'] in viewable_file_formats and \
                properties['status'] in viewable_file_status:
            if 'assembly' in properties:
                assembly.add(properties['assembly'])
    return list(assembly)


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
        'submitted_by',
        'lab',
        'award.pi.lab',
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
            "type": "string",
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
        if status in ('release ready', 'released', 'archived'):
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
    def assembly(self, request, original_files, status):
        return calculate_assembly(request, original_files, status)

    @calculated_property(condition='assembly', schema={
        "title": "Hub",
        "type": "string",
    })
    def hub(self, request):
        return request.resource_path(self, '@@hub', 'hub.txt')

    @calculated_property(condition='hub', category='page', schema={
        "title": "Visualize Data",
        "type": "string",
    })
    def visualize(self, request, hub, assembly, status):
        hub_url = urljoin(request.resource_url(request.root), hub)
        viz = {}
        for assembly_name in assembly:
            if assembly_name in viz:  # mm10 and mm10-minimal resolve to the same thing
                continue
            browser_urls = {}
            if status == 'released':  # Non-biodalliance is for released experiments/files only
                ucsc_url = vis_format_external_url("ucsc", hub_url, assembly_name)
                if ucsc_url is not None:
                    browser_urls['UCSC'] = ucsc_url
                ensembl_url = vis_format_external_url("ensembl", hub_url, assembly_name)
                if ensembl_url is not None:
                    browser_urls['Ensembl'] = ensembl_url
            # Now for biodalliance.  bb and bw already known?  How about non-deleted?
            # TODO: define (in visualization.py?) supported assemblies list
            if assembly_name in ['hg19', 'GRCh38', 'mm10', 'mm10-minimal' ,'mm9','dm6','dm3','ce10','ce11']:
                if status not in ["proposed", "started", "deleted", "revoked", "replaced"]:
                    file_formats = '&file_format=bigBed&file_format=bigWig'
                    file_inclusions = '&status=released&status=in+progress'
                    bd_path = ('/search/?type=File&assembly=%s&dataset=%s%s%s#browser' %
                               (assembly_name,request.path,file_formats,file_inclusions))
                    browser_urls['Quick View'] = bd_path  # no host to avoid 'test' problems
            if browser_urls:
                viz[assembly_name] = browser_urls
        if viz:
            return viz
        else:
            return None

    @calculated_property(condition='date_released', schema={
        "title": "Month released",
        "type": "string",
    })
    def month_released(self, date_released):
        return datetime.datetime.strptime(date_released, '%Y-%m-%d').strftime('%B, %Y')


class FileSet(Dataset):
    item_type = 'file_set'
    base_types = ['FileSet'] + Dataset.base_types
    schema = load_schema('encoded:schemas/file_set.json')
    embedded = Dataset.embedded

    @calculated_property(schema={
        "title": "Contributing files",
        "type": "array",
        "items": {
            "type": "string",
            "linkTo": "File",
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

    @calculated_property(define=True, schema={
        "title": "Files",
        "type": "array",
        "items": {
            "type": "string",
            "linkTo": "File",
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
            "linkTo": "File",
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
    def assembly(self, request, original_files, related_files, status):
        return calculate_assembly(request, list(chain(original_files, related_files))[:101], status)


@collection(
    name='annotations',
    unique_key='accession',
    properties={
        'title': "Annotation file set",
        'description': 'A set of annotation files produced by ENCODE.',
    })
class Annotation(FileSet, CalculatedBiosampleSlims, CalculatedBiosampleSynonyms):
    item_type = 'annotation'
    schema = load_schema('encoded:schemas/annotation.json')
    embedded = FileSet.embedded + [
        'software_used',
        'software_used.software',
        'organism',
        'targets',
        'files.dataset',
        'files.analysis_step_version.analysis_step',
        'files.analysis_step_version.analysis_step.documents',
        'files.analysis_step_version.analysis_step.documents.award',
        'files.analysis_step_version.analysis_step.documents.lab',
        'files.analysis_step_version.analysis_step.documents.submitted_by',
        'files.analysis_step_version.analysis_step.pipelines',
        'files.analysis_step_version.analysis_step.pipelines.documents',
        'files.analysis_step_version.analysis_step.pipelines.documents.award',
        'files.analysis_step_version.analysis_step.pipelines.documents.lab',
        'files.analysis_step_version.analysis_step.pipelines.documents.submitted_by',
        'files.analysis_step_version.analysis_step.versions',
        'files.analysis_step_version.analysis_step.versions.software_versions',
        'files.analysis_step_version.analysis_step.versions.software_versions.software',
        'files.analysis_step_version.software_versions',
        'files.analysis_step_version.software_versions.software',
        'files.quality_metrics',
        'files.quality_metrics.step_run',
        'files.quality_metrics.step_run.analysis_step_version.analysis_step',
        'files.replicate.library',
    ]
    rev = Dataset.rev.copy()
    rev.update({
        'superseded_by': ('Annotation', 'supersedes')
    })

    matrix = {
        'y': {
            'facets': [
                'organism.scientific_name',
                'biosample_type',
                'organ_slims',
                'award.project',
                'assembly',
                'encyclopedia_version'
            ],
            'group_by': ['biosample_type', 'biosample_term_name'],
            'label': 'Biosample',
        },
        'x': {
            'facets': [
                'annotation_type',
                'month_released',
                'targets.label',
                'files.file_type',
            ],
            'group_by': 'annotation_type',
            'label': 'Type',
        },
    }

    @calculated_property(schema={
        "title": "Superseded by",
        "type": "array",
        "items": {
            "type": ['string', 'object'],
            "linkFrom": "Annotation.supersedes",
        },
    })
    def superseded_by(self, request, superseded_by):
        return paths_filtered_by_status(request, superseded_by)


@collection(
    name='publication-data',
    unique_key='accession',
    properties={
        'title': "Publication file set",
        'description': 'A set of files that are described/analyzed in a publication.',
    })
class PublicationData(FileSet, CalculatedFileSetBiosample, CalculatedFileSetAssay, CalculatedBiosampleSlims, CalculatedBiosampleSynonyms, CalculatedAssaySynonyms):
    item_type = 'publication_data'
    schema = load_schema('encoded:schemas/publication_data.json')
    embedded = [
        'organism',
        'submitted_by',
        'lab',
        'award.pi.lab',
        'documents.lab',
        'documents.award',
        'documents.submitted_by',
        'references'
    ]


@collection(
    name='references',
    unique_key='accession',
    properties={
        'title': "Reference file set",
        'description': 'A set of reference files used by ENCODE.',
    })
class Reference(FileSet):
    item_type = 'reference'
    schema = load_schema('encoded:schemas/reference.json')
    embedded = FileSet.embedded + ['software_used', 'software_used.software', 'organism', 'files.dataset']


@collection(
    name='ucsc-browser-composites',
    unique_key='accession',
    properties={
        'title': "UCSC browser composite file set",
        'description': 'A set of files that comprise a composite at the UCSC genome browser.',
    })
class UcscBrowserComposite(FileSet, CalculatedFileSetAssay, CalculatedAssaySynonyms):
    item_type = 'ucsc_browser_composite'
    schema = load_schema('encoded:schemas/ucsc_browser_composite.json')
    embedded = FileSet.embedded + [
        'organism',
        'files.dataset',
        'files.replicate.library'
    ]

    @calculated_property(condition='files', schema={
        "title": "Organism",
        "type": "array",
        "items": {
            "type": 'string',
            "linkTo": "Organism"
        },
    })
    def organism(self, request, files):
        organisms = []
        if files:
            for idx, path in enumerate(files):
                # Need to cap this due to the large numbers of files in related_files
                if idx < 100:
                    f = request.embed(path, '@@object')
                    if 'replicate' in f:
                        rep = request.embed(f['replicate'], '@@object')
                        if 'library' in rep:
                            lib = request.embed(rep['library'], '@@object')
                            if 'biosample' in lib:
                                bio = request.embed(lib['biosample'], '@@object')
                                if 'organism' in bio:
                                    organisms.append(bio['organism'])
            if organisms:
                return paths_filtered_by_status(request, list(set(organisms)))
            else:
                return organisms


@collection(
    name='projects',
    unique_key='accession',
    properties={
        'title': "Project file set",
        'description': 'A set of files that comprise a project.',
    })
class Project(FileSet, CalculatedFileSetAssay, CalculatedFileSetBiosample, CalculatedBiosampleSlims, CalculatedBiosampleSynonyms, CalculatedAssaySynonyms):
    item_type = 'project'
    schema = load_schema('encoded:schemas/project.json')
    embedded = FileSet.embedded + [
        'files.dataset',
        'files.replicate.library',
        'files.replicate.experiment.target',
        'organism'
    ]


@abstract_collection(
    name='series',
    unique_key='accession',
    properties={
        'title': "Series",
        'description': 'Listing of all types of series datasets.',
    })
class Series(Dataset, CalculatedSeriesAssay, CalculatedSeriesBiosample, CalculatedBiosampleSlims, CalculatedBiosampleSynonyms, CalculatedSeriesTarget, CalculatedSeriesTreatment, CalculatedAssaySynonyms):
    item_type = 'series'
    base_types = ['Series'] + Dataset.base_types
    schema = load_schema('encoded:schemas/series.json')
    embedded = Dataset.embedded + [
        'organism',
        'target',
        'target.organism',
        'references',
        'related_datasets.files',
        'related_datasets.files.analysis_step_version',
        'related_datasets.files.analysis_step_version.analysis_step',
        'related_datasets.files.analysis_step_version.analysis_step.pipelines',
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
    ]

    @calculated_property(schema={
        "title": "Revoked datasets",
        "type": "array",
        "items": {
            "type": "string",
            "linkTo": "File",
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
    def assembly(self, request, original_files, related_datasets, status):
        combined_assembly = set()
        for assembly_from_original_files in calculate_assembly(request, original_files, status):
            combined_assembly.add(assembly_from_original_files)
        for dataset in related_datasets:
            properties = request.embed(dataset, '@@object')
            if properties['status'] not in ('deleted', 'replaced'):
                for assembly_from_related_dataset in properties['assembly']:
                    combined_assembly.add(assembly_from_related_dataset)
        return list(combined_assembly)


@collection(
    name='matched-sets',
    unique_key='accession',
    properties={
        'title': "Matched Set Series",
        'description': 'A series that groups two or more datasets (experiments) together with shared properties',
    })
class MatchedSet(Series):
    item_type = 'matched_set'
    schema = load_schema('encoded:schemas/matched_set.json')
    embedded = Series.embedded


@collection(
    name='treatment-time-series',
    unique_key='accession',
    properties={
        'title': "Treatment time series",
        'description': 'A series that varies on treatment duration across an applied treatment.',
    })
class TreatmentTimeSeries(Series):
    item_type = 'treatment_time_series'
    schema = load_schema('encoded:schemas/treatment_time_series.json')
    embedded = Series.embedded


@collection(
    name='treatment-concentration-series',
    unique_key='accession',
    properties={
        'title': "Treatment concentration series",
        'description': 'A series that varies on treatment concentration across an applied treatment.',
    })
class TreatmentConcentrationSeries(Series):
    item_type = 'treatment_concentration_series'
    schema = load_schema('encoded:schemas/treatment_concentration_series.json')
    embedded = Series.embedded


@collection(
    name='organism-development-series',
    unique_key='accession',
    properties={
        'title': "Organism development series",
        'description': 'A series that varies age/life stage of an organism.',
    })
class OrganismDevelopmentSeries(Series):
    item_type = 'organism_development_series'
    schema = load_schema('encoded:schemas/organism_development_series.json')
    embedded = Series.embedded


@collection(
    name='replication-timing-series',
    unique_key='accession',
    properties={
        'title': "Replication timing series",
        'description': 'A series tracking replication timing over the cell cycle.',
    })
class ReplicationTimingSeries(Series):
    item_type = 'replication_timing_series'
    schema = load_schema('encoded:schemas/replication_timing_series.json')
    embedded = Series.embedded


@collection(
    name='reference-epigenomes',
    unique_key='accession',
    properties={
        'title': "Reference epigenomes",
        'description': 'A series made up of complimentary assays that define a reference epigenome according to IHEC.',
    })
class ReferenceEpigenome(Series):
    item_type = 'reference_epigenome'
    schema = load_schema('encoded:schemas/reference_epigenome.json')
    embedded = Series.embedded
