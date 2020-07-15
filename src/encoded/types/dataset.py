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
    CalculatedAssaySynonyms,
    CalculatedAssayTermID,
    CalculatedAssaySlims,
    CalculatedCategorySlims,
    CalculatedFileSetAssay,
    CalculatedFileSetBiosample,
    CalculatedSeriesAssay,
    CalculatedSeriesBiosample,
    CalculatedSeriesTreatment,
    CalculatedSeriesTarget,
    CalculatedObjectiveSlims,
    CalculatedTypeSlims,
    CalculatedVisualize
)

from .biosample import construct_biosample_summary

from .shared_biosample import biosample_summary_information

from itertools import chain
import datetime


def item_is_revoked(request, path):
    return request.embed(path, '@@object?skip_calculated=true').get('status') == 'revoked'


def calculate_assembly(request, files_list, status):
    assembly = set()
    viewable_file_status = ['released','in progress']

    for path in files_list:
        properties = request.embed(path, '@@object?skip_calculated=true')
        if properties['status'] in viewable_file_status:
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
        'files.replicate.experiment.target.genes',
        'files.submitted_by',
        'files.lab',
        'revoked_files',
        'revoked_files.replicate',
        'revoked_files.replicate.experiment',
        'revoked_files.replicate.experiment.lab',
        'revoked_files.replicate.experiment.target',
        'revoked_files.replicate.experiment.target.genes',
        'revoked_files.submitted_by',
        'submitted_by',
        'lab',
        'award.pi.lab',
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
    set_status_up = [
        'original_files',
        'replicates',
        'documents',
        'target',
    ]
    set_status_down = []
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
        "notSubmittable": True,
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
            properties = request.embed(path, '@@object?skip_calculated=true')
            derived_from.update(
                paths_filtered_by_status(request, properties.get('derived_from', []))
            )
        outside_files = list(derived_from.difference(original_files))
        if status in ('released'):
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
        if status in ('released', 'archived'):
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
        "title": "Genome assembly",
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


@collection(
    name='transgenic-enhancer-experiments',
    unique_key='accession',
    properties={
        'title': 'Transgenic enhancer experiments',
        'description': 'Listing of Transgenic Enhancer Experiments',
    })
class TransgenicEnhancerExperiment(
    Dataset,
    CalculatedAssaySynonyms,
    CalculatedAssayTermID,
    CalculatedAssaySlims,
    CalculatedCategorySlims,
    CalculatedTypeSlims,
    CalculatedObjectiveSlims):
    item_type = 'transgenic_enhancer_experiment'
    schema = load_schema('encoded:schemas/transgenic_enhancer_experiment.json')
    embedded = Dataset.embedded + [
        'biosample_ontology',
        'biosamples',
    ]
    audit_inherit = [
        'submitted_by',
        'lab',
        'award',
        'documents.lab',
    ]
    set_status_up = [
        'documents'
    ]
    set_status_down = []
    rev = Dataset.rev.copy()
    rev.update({
        'superseded_by': ('TransgenicEnhancerExperiment', 'supersedes')
    })

    @calculated_property(schema={
        "title": "Superseded by",
        "type": "array",
        "items": {
            "type": ['string', 'object'],
            "linkFrom": "InVivoExperiment.supersedes",
        },
        "notSubmittable": True,
    })
    def superseded_by(self, request, superseded_by):
        return paths_filtered_by_status(request, superseded_by)

    @calculated_property(schema={
        "title": "Biosample summary",
        "type": "string",
    })
    def biosample_summary(self, request, biosamples=None):
        drop_age_sex_flag = False
        dictionaries_of_phrases = []
        biosample_accessions = set()
        if biosamples is not None:
            for bs in biosamples:
                biosampleObject = request.embed(bs, '@@object')
                if biosampleObject['status'] == 'deleted':
                    continue
                if biosampleObject['accession'] not in biosample_accessions:
                    biosample_accessions.add(biosampleObject['accession'])
                    biosample_info = biosample_summary_information(request, biosampleObject)
                    biosample_summary_dictionary = biosample_info[0]
                    biosample_drop_age_sex_flag = biosample_info[1]
                    dictionaries_of_phrases.append(biosample_summary_dictionary)
                    if biosample_drop_age_sex_flag is True:
                        drop_age_sex_flag = True

        if drop_age_sex_flag is True:
            sentence_parts = [
                'strain_background',
                'experiment_term_phrase',
                'phase',
                'fractionated',
                'synchronization',
                'modifications_list',
                'originated_from',
                'treatments_phrase',
                'depleted_in'
            ]
        else:
            sentence_parts = [
                'strain_background',
                'experiment_term_phrase',
                'phase',
                'fractionated',
                'sex_stage_age',
                'synchronization',
                'modifications_list',
                'originated_from',
                'treatments_phrase',
                'depleted_in'
            ]
        if len(dictionaries_of_phrases) > 0:
            return construct_biosample_summary(dictionaries_of_phrases, sentence_parts)


class FileSet(Dataset):
    item_type = 'file_set'
    base_types = ['FileSet'] + Dataset.base_types
    schema = load_schema('encoded:schemas/file_set.json')
    embedded = Dataset.embedded

    @calculated_property(define=True, schema={
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
            properties = request.embed(path, '@@object?skip_calculated=true')
            derived_from.update(
                paths_filtered_by_status(request, properties.get('derived_from', []))
            )
        outside_files = list(derived_from.difference(files))
        if status in ('released'):
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
        if status in ('released'):
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
        "title": "Genome assembly",
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
class Annotation(FileSet, CalculatedVisualize):
    item_type = 'annotation'
    schema = load_schema('encoded:schemas/annotation.json')
    embedded = FileSet.embedded + [
        'biosample_ontology',
        'software_used',
        'software_used.software',
        'organism',
        'targets',
        'targets.genes',
        'files.dataset',
        'files.analysis_step_version.analysis_step',
        'files.analysis_step_version.analysis_step.pipelines',
        'files.analysis_step_version.analysis_step.versions',
        'files.analysis_step_version.analysis_step.versions.software_versions',
        'files.analysis_step_version.analysis_step.versions.software_versions.software',
        'files.analysis_step_version.software_versions',
        'files.analysis_step_version.software_versions.software',
        'files.quality_metrics',
        'files.quality_metrics.step_run',
        'files.quality_metrics.step_run.analysis_step_version.analysis_step',
        'files.replicate.library',
        'files.library'
    ]
    rev = Dataset.rev.copy()
    rev.update({
        'superseded_by': ('Annotation', 'supersedes')
    })

    matrix = {
        'y': {
            'facets': [
                'organism.scientific_name',
                'biosample_ontology.classification',
                'biosample_ontology.organ_slims',
                'biosample_ontology.cell_slims',
                'award.project',
                'assembly',
                'encyclopedia_version'
            ],
            'group_by': ['biosample_ontology.classification', 'biosample_ontology.term_name'],
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
        "title": "Files",
        "type": "array",
        "items": {
            "type": "string",
            "linkTo": "File",
        },
    })
    def files(self, request, original_files, status):
        if status in ('released', 'archived'):
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
        "title": "Superseded by",
        "type": "array",
        "items": {
            "type": ['string', 'object'],
            "linkFrom": "Annotation.supersedes",
        },
        "notSubmittable": True,
    })
    def superseded_by(self, request, superseded_by):
        return paths_filtered_by_status(request, superseded_by)

    @calculated_property(condition='contributing_files', schema={
        "title": "Biochemical profile inputs",
        "description": "The input data used to generate a cCRE annotation.",
        "type": "string",
        "notSubmittable": True
    })
    def biochemical_inputs(
        self,
        request,
        annotation_type,
        encyclopedia_version=None,
        contributing_files=None
    ):
        # https://encodedcc.atlassian.net/browse/ENCD-5288
        inputs_list = []
        if encyclopedia_version is not None and \
            encyclopedia_version in [
                'ENCODE v4', 'ENCODE v5', 'ENCODE v6'
                ]:
            if annotation_type == 'candidate Cis-Regulatory Elements':
                if contributing_files is not None:
                    for input_file in contributing_files:
                        file = request.embed(input_file, '@@object?skip_calculated=true')
                        if file['output_type'] == 'candidate Cis-Regulatory Elements':
                            if 'derived_from' in file:
                                derived_from_file = request.embed(file['derived_from'][0], '@@object?skip_calculated=true')
                                if derived_from_file['output_type'] == 'representative DNase hypersensitivity sites (rDHSs)':
                                    inputs_list.append('rDHS')
                                if derived_from_file['output_type'] == 'consensus DNase hypersensitivity sites (cDHSs)':
                                    inputs_list.append('cDHS')
                        else:
                            if file['dataset']:
                                properties = request.embed(file['dataset'], '@@object')
                                if 'assay_term_name' in properties:
                                    if properties['assay_term_name'] == 'ChIP-seq':
                                        target = request.embed(properties['target'], '@@object?skip_calculated=true')
                                        inputs_list.append(target['label'])
                                    elif properties['assay_term_name'] == 'DNase-seq':
                                        inputs_list.append('DNase-seq')
        inputs_list = sorted(inputs_list)
        return ((', ').join([str(each) for each in inputs_list]))


@collection(
    name='publication-data',
    unique_key='accession',
    properties={
        'title': "Publication file set",
        'description': 'A set of files that are described/analyzed in a publication.',
    })
class PublicationData(FileSet):
    item_type = 'publication_data'
    schema = load_schema('encoded:schemas/publication_data.json')
    embedded = [
        'submitted_by',
        'lab',
        'award.pi.lab',
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
    embedded = FileSet.embedded + ['software_used', 'software_used.software', 'organism', 'files.dataset', 'donor', 'examined_loci']


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
        'files.replicate.library',
        'files.library'
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
                    if 'library' in f:
                        lib = request.embed(f['library'], '@@object?skip_calculated=true')
                        if 'biosample' in lib:
                            bio = request.embed(lib['biosample'], '@@object?skip_calculated=true')
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
class Project(FileSet, CalculatedFileSetAssay, CalculatedFileSetBiosample, CalculatedAssaySynonyms):
    item_type = 'project'
    schema = load_schema('encoded:schemas/project.json')
    embedded = FileSet.embedded + [
        'biosample_ontology',
        'files.dataset',
        'files.replicate.library',
        'files.library',
        'files.replicate.experiment.target',
        'organism'
    ]


@collection(
    name='computational-models',
    unique_key='accession',
    properties={
        'title': "Computational model file set",
        'description': 'A set of files that comprise a computational model.',
    })
class ComputationalModel(FileSet):
    item_type = 'computational_model'
    schema = load_schema('encoded:schemas/computational_model.json')
    embedded = FileSet.embedded + [
        'submitted_by',
        'lab',
        'award.pi.lab',
        'software_used',
        'software_used.software'
    ]


@abstract_collection(
    name='series',
    unique_key='accession',
    properties={
        'title': "Series",
        'description': 'Listing of all types of series datasets.',
    })
class Series(Dataset, CalculatedSeriesAssay, CalculatedSeriesBiosample, CalculatedSeriesTarget, CalculatedSeriesTreatment, CalculatedAssaySynonyms):
    item_type = 'series'
    base_types = ['Series'] + Dataset.base_types
    schema = load_schema('encoded:schemas/series.json')
    embedded = Dataset.embedded + [
        'biosample_ontology',
        'organism',
        'target',
        'target.genes',
        'target.organism',
        'references',
        'related_datasets.biosample_ontology',
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
        'related_datasets.replicates.library.biosample.submitted_by',
        'related_datasets.replicates.library.biosample.source',
        'related_datasets.replicates.library.biosample.organism',
        'related_datasets.replicates.library.biosample.donor.organism',
        'related_datasets.replicates.library.biosample.treatments',
        'related_datasets.replicates.library.spikeins_used',
        'related_datasets.replicates.library.treatments',
        'related_datasets.replicates.libraries',
        'related_datasets.replicates.libraries.biosample.submitted_by',
        'related_datasets.replicates.libraries.biosample.source',
        'related_datasets.replicates.libraries.biosample.organism',
        'related_datasets.replicates.libraries.biosample.donor.organism',
        'related_datasets.replicates.libraries.biosample.treatments',
        'related_datasets.replicates.libraries.spikeins_used',
        'related_datasets.replicates.libraries.treatments',
        'related_datasets.possible_controls',
        'related_datasets.possible_controls.lab',
        'related_datasets.target.organism',
        'related_datasets.references',
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
        'files.library.biosample',
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
        "title": "Genome assembly",
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

    @calculated_property(define=True, schema={
        "title": "Control types",
        "type": "array",
        "items": {
            "type": "string",
        },
    })
    def control_type(self, request, related_datasets):
        return request.select_distinct_values('control_type', *related_datasets)


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
    name='aggregate-series',
    unique_key='accession',
    properties={
        'title': "Aggregate series",
        'description': 'A series that groups two or more datastes to allow meta-analysis.',
    })
class AggregateSeries(Series):
    item_type = 'aggregate_series'
    schema = load_schema('encoded:schemas/aggregate_series.json')
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

    rev = Dataset.rev.copy()
    rev.update({
        'superseded_by': ('ReferenceEpigenome', 'supersedes')
    })

    @calculated_property(schema={
        "title": "Superseded by",
        "type": "array",
        "items": {
            "type": ['string', 'object'],
            "linkFrom": "ReferenceEpigenome.supersedes",
        },
        "notSubmittable": True,
    })
    def superseded_by(self, request, superseded_by):
        return paths_filtered_by_status(request, superseded_by)


@collection(
    name='experiment-series',
    unique_key='accession',
    properties={
        'title': "Experiment series",
        'description': 'A series that groups two or more experiments.',
    })
class ExperimentSeries(Series):
    item_type = 'experiment_series'
    schema = load_schema('encoded:schemas/experiment_series.json')
    name_key = 'accession'
    embedded = [
        'biosample_ontology',
        'contributing_awards',
        'contributors',
        'organism',
        'related_datasets.award',
        'related_datasets.lab',
        'related_datasets.replicates.library.biosample',
        'related_datasets.target',
        'target',
        'target.genes',
        'target.organism',
    ]

    @calculated_property(schema={
        "title": "Assay type",
        "type": "array",
        "items": {
            "type": "string",
        },
    })
    def assay_slims(self, request, related_datasets):
        return request.select_distinct_values('assay_slims', *related_datasets)

    @calculated_property(schema={
        "title": "Assay title",
        "type": "array",
        "items": {
            "type": "string",
        },
    })
    def assay_title(self, request, related_datasets):
        return request.select_distinct_values('assay_title', *related_datasets)

    @calculated_property(schema={
        "title": "Awards",
        "type": "array",
        "items": {
            "type": 'string',
            "linkTo": "Award",
        },
    })
    def contributing_awards(self, request, related_datasets):
        return request.select_distinct_values('award', *related_datasets)

    @calculated_property(schema={
        "title": "Labs",
        "type": "array",
        "items": {
            "type": 'string',
            "linkTo": "Lab",
        },
    })
    def contributors(self, request, related_datasets):
        return request.select_distinct_values('lab', *related_datasets)

    @calculated_property(schema={
        "title": "Biosample summary",
        "type": "array",
        "items": {
            "type": 'string',
        },
    })
    def biosample_summary(self, request, related_datasets):
        return request.select_distinct_values('biosample_summary', *related_datasets)


@collection(
    name='single-cell-rna-series',
    unique_key='accession',
    properties={
        'title': "Single cell RNA series",
        'description': 'A series that group single cell RNA experiments sharing a similar cell classification.',
    })
class SingleCellRnaSeries(Series):
    item_type = 'single_cell_rna_series'
    schema = load_schema('encoded:schemas/single_cell_rna_series.json')
    embedded = Series.embedded


@collection(
    name='functional-characterization-series',
    unique_key='accession',
    properties={
        'title': "Functional characterization series",
        'description': 'A series that group functional characterization experiments which should be analyzed and interpreted together.',
    })
class FunctionalCharacterizationSeries(Series):
    item_type = 'functional_characterization_series'
    schema = load_schema('encoded:schemas/functional_characterization_series.json')
    embedded = Series.embedded
