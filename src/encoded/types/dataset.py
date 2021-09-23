from snovault import (
    abstract_collection,
    calculated_property,
    collection,
    load_schema,
)
from snovault.util import Path
from .base import (
    Item,
    paths_filtered_by_status,
)

from urllib.parse import quote_plus
from urllib.parse import urljoin
from .shared_calculated_properties import (
    CalculatedAssaySynonyms,
    CalculatedAssayTermID,
    CalculatedAssayTitle,
    CalculatedAssaySlims,
    CalculatedBiosampleSummary,
    CalculatedSimpleSummary,
    CalculatedReplicates,
    CalculatedReplicationType,
    CalculatedCategorySlims,
    CalculatedFileSetAssay,
    CalculatedFileSetBiosample,
    CalculatedSeriesAssay,
    CalculatedSeriesAssayType,
    CalculatedSeriesBiosample,
    CalculatedSeriesTreatment,
    CalculatedSeriesTarget,
    CalculatedObjectiveSlims,
    CalculatedTypeSlims,
    CalculatedVisualize
)

from .biosample import construct_biosample_summary

from .shared_biosample import biosample_summary_information

from .assay_data import assay_terms

from itertools import chain
from pkg_resources import parse_version
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
    schema = load_schema('encoded:schemas/dataset.json')
    embedded = [
        'analyses',
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
    ]
    embedded_with_frame = [
        Path('references', exclude=['datasets', 'publication_data']),
        Path(
            'files.analyses',
            include=[
                '@id',
                '@type',
                'uuid',
                'status',
                'pipeline_award_rfas',
                'pipeline_version',
                'title',
            ],
        ),
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
        if status in ('released',):
            return paths_filtered_by_status(
                request, outside_files,
                include=('released', 'archived', 'in progress'),
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

    @calculated_property(condition='analyses', schema={
        "title": "Default analysis",
        "description": "One default analysis that should be checked first.",
        "comment": "Do not submit. This field is calculated from files in this analysis.",
        "type": "string",
        "linkTo": "Analysis",
        "notSubmittable": True
    })
    def default_analysis(self, request, status, analyses):
        types = request.registry['types']
        unreleased_status = ['in progress', 'submitted', 'deleted', 'replaced']
        # Easier to sort everything by max, so reverse order of all
        status_order = list(reversed(types['analysis'].schema['properties']['status']['enum']))
        award_rfa_order = list(reversed(types['award'].schema['properties']['rfa']['enum']))
        assembly_order = list(reversed(types['file'].schema['properties']['assembly']['enum'] + ['mixed']))
        genome_annotation_order = list(reversed(types['file'].schema['properties']['genome_annotation']['enum'] + ['mixed']))

        analyses = (
            request.embed(
                analysis_id,
                '@@object_with_select_calculated_properties'
                '?field=@id'
                '&field=pipeline_labs'
                '&field=pipeline_award_rfas'
                '&field=assembly'
                '&field=genome_annotation',
            )
            for analysis_id in analyses
        )
        if status not in unreleased_status:
            status_order = [
                s
                for s in status_order
                if s not in unreleased_status
            ]
            analyses = (
                analysis
                for analysis in analyses
                if  analysis['status'] in status_order
            )
        analysis_ranking = {}

        for analysis in analyses:
            status_rank = status_order.index(analysis['status'])
            # True ranked higher than False.
            lab_rank = '/labs/encode-processing-pipeline/' in analysis.get('pipeline_labs', [])
            # Get max index or zero if field doesn't exist.
            pipeline_award_rfa_rank = max(chain(
                (award_rfa_order.index(rfa)
                for rfa in analysis.get('pipeline_award_rfa', [])), [0])
            )
            # Get max index or zero if field doesn't exist. 
            assembly_rank = 0
            if analysis.get('assembly', '') in assembly_order:
                assembly_rank = assembly_order.index(analysis.get('assembly', ''))
            genome_annotation_rank = 0
            if analysis.get('genome_annotation', '') in genome_annotation_order:
                genome_annotation_rank = genome_annotation_order.index(analysis.get('genome_annotation', ''))
            # We reverse sort order at the end so later version numbers will rank higher.
            pipeline_version_rank = parse_version(analysis.get('pipeline_version', ''))
            # We reverse sort order at the end so later dates rank higher.
            date_rank = datetime.datetime.strptime(
                convert_date_string(
                    analysis['date_created']
                ),
                "%Y-%m-%dT%H:%M:%S.%f%z"
            )
            # Store all the ranking numbers for an analysis in a tuple that can be sorted.
            analysis_ranking[
                (
                    status_rank,
                    lab_rank,
                    pipeline_award_rfa_rank,
                    assembly_rank,
                    genome_annotation_rank,
                    pipeline_version_rank,
                    date_rank,
                )
            ] = analysis['@id']
        
        if analysis_ranking:
            # We want highest version, date, etc. so reverse sort order. Access value from top item.
            return sorted(analysis_ranking.items(), reverse=True)[0][1]


def convert_date_string(date_string):
    if ":" == date_string[-3]:
        date_string = date_string[:-3]+date_string[-2:]
    return date_string


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
    CalculatedAssayTitle,
    CalculatedAssaySlims,
    CalculatedCategorySlims,
    CalculatedTypeSlims,
    CalculatedObjectiveSlims):
    item_type = 'transgenic_enhancer_experiment'
    schema = load_schema('encoded:schemas/transgenic_enhancer_experiment.json')
    embedded = Dataset.embedded + [
        'biosample_ontology',
        'biosamples',
        'biosamples.donor.organism',
        'biosamples.biosample_ontology',
        'biosamples.organism',
        'biosamples.characterizations',
    ]
    audit_inherit = [
        'submitted_by',
        'lab',
        'award',
        'documents.lab',
    ]
    set_status_up = [
        'documents',
        'biosamples',
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
            "linkFrom": "TransgenicEnhancerExperiment.supersedes",
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
        add_classification_flag = False
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
                    biosample_add_classification_flag = biosample_info[2]
                    biosample_drop_originated_from_flag = biosample_info[3]
                    dictionaries_of_phrases.append(biosample_summary_dictionary)
                    if biosample_drop_age_sex_flag is True:
                        drop_age_sex_flag = True
                    if biosample_add_classification_flag is True:
                        add_classification_flag = True

        sentence_parts = [
            'genotype_strain',
            'experiment_term_phrase',
            'phase',
            'fractionated',
            'sex_stage_age',
            'post_nucleic_acid_delivery_time',
            'post_differentiation_time',
            'synchronization',
            'modifications_list',
            'originated_from',
            'treatments_phrase',
            'depleted_in',
            'disease_term_name',
            'pulse_chase_time'
        ]
        if drop_age_sex_flag:
            sentence_parts.remove('sex_stage_age')
        if add_classification_flag:
            sentence_parts.insert(2, 'sample_type')
        if biosample_drop_originated_from_flag:
            sentence_parts.remove('originated_from')

        if len(dictionaries_of_phrases) > 0:
            return construct_biosample_summary(dictionaries_of_phrases, sentence_parts)


@collection(
    name='single-cell-units',
    unique_key='accession',
    properties={
        'title': 'Single cell units',
        'description': 'Listing of single cell units',
    })
class SingleCellUnit(
    Dataset,
    CalculatedBiosampleSummary,
    CalculatedSimpleSummary,
    CalculatedReplicates,
    CalculatedAssaySynonyms,
    CalculatedAssayTermID,
    CalculatedVisualize,
    CalculatedAssaySlims,
    CalculatedAssayTitle,
    CalculatedCategorySlims,
    CalculatedTypeSlims,
    CalculatedObjectiveSlims,
    CalculatedReplicationType):
    item_type = 'single_cell_unit'
    schema = load_schema('encoded:schemas/single_cell_unit.json')
    embedded = Dataset.embedded + [
        'biosample_ontology',
        'files.platform',
        'files.analysis_step_version.analysis_step',
        'files.analysis_step_version.analysis_step.pipelines',
        'related_series',
        'replicates.antibody',
        'replicates.library',
        'replicates.library.biosample.biosample_ontology',
        'replicates.library.biosample.submitted_by',
        'replicates.library.biosample.source',
        'replicates.library.biosample.applied_modifications',
        'replicates.library.biosample.applied_modifications.documents',
        'replicates.library.biosample.organism',
        'replicates.library.biosample.donor',
        'replicates.library.biosample.donor.organism',
        'replicates.library.biosample.part_of',
        'replicates.library.biosample.part_of.donor',
        'replicates.library.biosample.part_of.treatments',
        'replicates.library.biosample.treatments',
        'replicates.library.construction_platform',
        'replicates.library.treatments',
        'possible_controls',
    ]
    audit_inherit = [
        'original_files',
        'original_files.replicate',
        'original_files.platform',
        'files.analysis_step_version.analysis_step.pipelines',
        'revoked_files',
        'revoked_files.replicate',
        'submitted_by',
        'lab',
        'award',
        'analyses',
        'documents',
        'replicates.antibody.characterizations.biosample_ontology',
        'replicates.antibody.characterizations',
        'replicates.antibody.targets',
        'replicates.library',
        'replicates.library.documents',
        'replicates.library.biosample',
        'replicates.library.biosample.biosample_ontology',
        'replicates.library.biosample.organism',
        'replicates.library.biosample.treatments',
        'replicates.library.biosample.applied_modifications',
        'replicates.library.biosample.donor.organism',
        'replicates.library.biosample.donor',
        'replicates.library.biosample.treatments',
        'replicates.library.biosample.originated_from',
        'replicates.library.biosample.originated_from.biosample_ontology',
        'replicates.library.biosample.part_of',
        'replicates.library.biosample.part_of.biosample_ontology',
        'replicates.library.biosample.pooled_from',
        'replicates.library.biosample.pooled_from.biosample_ontology',
        'replicates.library.spikeins_used',
        'replicates.library.treatments',
    ]
    set_status_up = [
        'original_files',
        'replicates',
        'documents',
        'analyses',
    ]
    set_status_down = [
        'original_files',
        'replicates',
        'analyses',
    ]
    rev = Dataset.rev.copy()
    rev.update({
        'related_series': ('Series', 'related_datasets'),
        'replicates': ('Replicate', 'experiment'),
        'superseded_by': ('SingleCellUnit', 'supersedes')
    })

    @calculated_property(schema={
        "title": "Related series",
        "type": "array",
        "items": {
            "type": ['string', 'object'],
            "linkFrom": "Series.related_datasets",
        },
        "notSubmittable": True,
    })
    def related_series(self, request, related_series):
        return paths_filtered_by_status(request, related_series)

    @calculated_property(schema={
            "title": "Superseded by",
            "type": "array",
            "items": {
                "type": ['string', 'object'],
                "linkFrom": "SingleCellUnit.supersedes",
            },
            "notSubmittable": True,
    })
    def superseded_by(self, request, superseded_by):
        return paths_filtered_by_status(request, superseded_by)


@abstract_collection(
    name='file-set',
    unique_key='accession',
    properties={
        'title': "File set",
        'description': 'A set of files.',
    }
)
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
                include=('released', 'archived'),
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
                include=('released', 'archived'),
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
        'documents',
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
    ]
    set_status_up = [
        'analyses'
    ]
    set_status_down = [
        'analyses'
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
        "type": "array",
        "items": {
            "type": "string"
        },
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
        inputs_set = set()
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
                                for derived_from_file in file['derived_from']:
                                    derived_from_file_embedded = request.embed(derived_from_file,
                                                                               '@@object?skip_calculated=true')
                                    if derived_from_file_embedded['output_type'] == \
                                            'representative DNase hypersensitivity sites':
                                        inputs_set.add('rDHS')
                                    if derived_from_file_embedded['output_type'] == \
                                            'consensus DNase hypersensitivity sites':
                                        inputs_set.add('cDHS')
                        else:
                            if file['dataset']:
                                properties = request.embed(file['dataset'], '@@object')
                                if 'assay_term_name' in properties:
                                    if properties['assay_term_name'] == 'ChIP-seq':
                                        target = request.embed(properties['target'],
                                                               '@@object?skip_calculated=true')
                                        inputs_set.add(target['label'])
                                    elif properties['assay_term_name'] == 'DNase-seq':
                                        inputs_set.add('DNase-seq')
        inputs_list = sorted(inputs_set)
        if inputs_list:
            return list(inputs_list)


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
        'award.pi.lab'
    ]
    embedded_with_frame = [
        Path('references', exclude=['datasets', 'publication_data']),
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
    embedded = FileSet.embedded + [
        'software_used',
        'software_used.software',
        'organism',
        'files.dataset',
        'donor',
        'examined_loci',
        'related_pipelines'
    ]

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
                    f = request.embed(path, '@@object?skip_calculated=true')
                    if 'replicate' in f:
                        rep = request.embed(f['replicate'], '@@object?skip_calculated=true')
                        if 'library' in rep:
                            lib = request.embed(rep['library'], '@@object?skip_calculated=true')
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
class Series(Dataset, CalculatedSeriesAssay, CalculatedSeriesAssayType, CalculatedSeriesBiosample, CalculatedSeriesTarget, CalculatedSeriesTreatment, CalculatedAssaySynonyms):
    item_type = 'series'
    base_types = ['Series'] + Dataset.base_types
    schema = load_schema('encoded:schemas/series.json')
    embedded = Dataset.embedded + [
        'biosample_ontology',
        'organism',
        'target',
        'target.genes',
        'target.organism',
        'related_datasets.biosample_ontology',
        'related_datasets.files',
        'related_datasets.files.analysis_step_version',
        'related_datasets.files.analysis_step_version.analysis_step',
        'related_datasets.files.analysis_step_version.analysis_step.pipelines',
        'related_datasets.files.target',
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
        'related_datasets.replicates.library.biosample.applied_modifications',
        'related_datasets.replicates.library.spikeins_used',
        'related_datasets.replicates.library.treatments',
        'related_datasets.possible_controls',
        'related_datasets.possible_controls.lab',
        'related_datasets.target',
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
    embedded_with_frame = [
        Path('references', exclude=['datasets', 'publication_data']),
        Path('related_datasets.references', exclude=['datasets', 'publication_data']),
        Path(
            'related_datasets.files.analyses',
            include=[
                '@id',
                '@type',
                'uuid',
                'status',
                'pipeline_award_rfas',
                'pipeline_version',
                'title',
            ],
        ),
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

    @calculated_property(schema={
        "title": "Biosample summary",
        "type": "string",
    })
    def biosample_summary(self, request, related_datasets):
        all_summaries = set()
        all_ontologies = set()
        biosample_accessions = set()
        all_strains = set()
        all_treatments = set()
        all_biosample_terms = []
        strain_name = ''
        treatment_names = ''
        for dataset in related_datasets:
            datasetObject = request.embed(dataset, '@@object')
            if datasetObject['status'] not in ('deleted', 'replaced'):
                if 'biosample_summary' in datasetObject:
                    all_summaries.add(datasetObject['biosample_summary'])
                all_ontologies.add(datasetObject['biosample_ontology'])
                replicates = datasetObject.get('replicates')
                if replicates:
                    for rep in replicates:
                        replicateObject = request.embed(rep, '@@object')
                        if replicateObject['status'] == 'deleted':
                            continue
                        if 'library' in replicateObject:
                            libraryObject = request.embed(replicateObject['library'], '@@object')
                            if libraryObject['status'] == 'deleted':
                                continue
                            if 'biosample' in libraryObject:
                                biosampleObject = request.embed(libraryObject['biosample'], '@@object')
                                if biosampleObject['status'] == 'deleted':
                                    continue
                                if biosampleObject['accession'] not in biosample_accessions:
                                    biosample_accessions.add(biosampleObject['accession'])
                                    if biosampleObject['organism'] in ['/organisms/mouse/', '/organisms/dmelanogaster/', '/organisms/celegans/' ]:
                                        if 'donor' in biosampleObject:
                                            donorObject = request.embed(biosampleObject['donor'], '@@object')
                                            if donorObject['status'] != 'deleted':
                                                strain_name = donorObject.get('strain_name')
                                                strain_background = donorObject.get('strain_background')
                                                if strain_name and strain_name.lower() != 'unknown':
                                                    all_strains.add(strain_name)
                                                elif strain_background and strain_background.lower() != 'unknown':
                                                    all_strains.add(strain_background)
                                    treatments = biosampleObject.get('treatments')
                                    if treatments:
                                        for treatment in treatments:
                                            treatmentObject = request.embed(treatment, '@@object')
                                            all_treatments.add(treatmentObject['treatment_term_name'])
        if all_ontologies:
            for ontology in all_ontologies:
                biosample_ontology = str(ontology)
                biosample_type_object = request.embed(biosample_ontology, '@@object')
                biosample_name = biosample_type_object['term_name']
                biosample_classification = biosample_type_object['classification']
                if biosample_classification == 'whole organisms':
                    term = biosample_classification
                else:
                    term = f"{biosample_name} {biosample_classification}"
                all_biosample_terms.append(term)
            all_terms = ', '.join(all_biosample_terms)
        if len(all_strains) == 1:
            strain_name = ', '.join(str(s) for s in all_strains)
        if all_treatments:
            treatment_names = ', '.join(str(s) for s in all_treatments)
        if all_summaries and all_ontologies:
            if len(all_summaries) == 1 and len(all_ontologies) == 1:
                return ', '.join(list(map(str, all_summaries)))
            elif len(all_summaries) > 1 and len(all_ontologies) == 1:
                biosample_ontology = ', '.join(str(s) for s in all_ontologies)
                biosample_type_object = request.embed(biosample_ontology, '@@object')
                biosample_name = biosample_type_object['term_name']
                biosample_classification = biosample_type_object['classification']
                if biosample_classification == 'whole organisms':
                    biosample_display = 'whole organisms'
                else:
                    biosample_display = f"{biosample_name} {biosample_classification}"
                if strain_name:
                    if treatment_names:
                        return f"{strain_name} {biosample_display} treated with {treatment_names}"
                    else:
                        return f"{strain_name} {biosample_display}"
                else:
                    if treatment_names:
                        return f"{biosample_display} treated with {treatment_names}"
                    else:
                        return f"{biosample_display}"
            elif len(all_summaries) > 1 and len(all_ontologies) > 1:
                if strain_name:
                    if treatment_names:
                        return f"{strain_name} {all_terms} treated with {treatment_names}"
                    else:
                        return f"{strain_name} {all_terms}"
                else:
                    if treatment_names:
                        return f"{all_terms} treated with {treatment_names}"
                    else:
                        return all_terms
            elif len(all_ontologies) > 1:
                if strain_name:
                    return f"{strain_name} {all_terms}"
                else:
                    return all_terms
        if all_ontologies and not all_summaries:
            return all_terms


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
    embedded = Series.embedded + [
        'related_datasets.analyses',
    ]


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
    embedded = Series.embedded + [
        'related_datasets.analyses',
    ]


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
    embedded = Series.embedded + [
        'related_datasets.analyses',
    ]


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
    embedded = Series.embedded + [
        'related_datasets.analyses',
    ]


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
    embedded = Series.embedded + [
        'related_datasets.analyses',
    ]


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
    embedded = Series.embedded + [
        'related_datasets.analyses',
    ]


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
    embedded = Series.embedded + [
        'related_datasets.analyses',
    ]

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
        'related_datasets.analyses',
        'related_datasets.award',
        'related_datasets.lab',
        'related_datasets.replicates.library.biosample',
        'related_datasets.target',
        'target',
        'target.genes',
        'target.organism',
    ]
    embedded_with_frame = []

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
    embedded = [
        'biosample_ontology',
        'organism',
        'lab',
        'award',
        'submitted_by',
        'related_datasets.lab',
        'related_datasets.biosample_ontology',
        'related_datasets.replicates.library',
        'related_datasets.replicates.library.biosample',
        'related_datasets.replicates.library.construction_platform'
    ]


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
    embedded = Series.embedded + [
        'related_datasets.analyses',
        'related_datasets.examined_loci',
        'related_datasets.examined_loci.gene',
        'related_datasets.elements_references',
        'related_datasets.elements_references.examined_loci',
        'elements_references',
        'elements_references.examined_loci',
    ]

    @calculated_property(condition='related_datasets', schema={
        "title": "Elements references",
        "type": "array",
        "items": {
            "type": "string",
            "linkTo": ["Annotation", "Reference"]
        }
    })
    def elements_references(self, request, related_datasets):
        return request.select_distinct_values('elements_references', *related_datasets)

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

@collection(
    name='gene-silencing-series',
    unique_key='accession',
    properties={
        'title': "Gene silencing series",
        'description': 'A series that group gene silencing experiments with the relevant controls.',
    })
class GeneSilencingSeries(Series):
    item_type = 'gene_silencing_series'
    schema = load_schema('encoded:schemas/gene_silencing_series.json')
    embedded = Series.embedded + [
        'related_datasets.analyses',
    ]


@collection(
    name='differentiation-series',
    unique_key='accession',
    properties={
        'title': "Differentiation series",
        'description': 'A series that groups experiments investigating biosamples along a differentiation trajectory.',
    })
class DifferentiationSeries(Series):
    item_type = 'differentiation_series'
    schema = load_schema('encoded:schemas/differentiation_series.json')
    embedded = Series.embedded + [
        'related_datasets.analyses',
    ]


@collection(
    name='pulse-chase-time-series',
    unique_key='accession',
    properties={
        'title': "Pulse chase time series",
        'description': 'A series that groups experiments investigating biosamples using pulse-chase analysis.',
    })
class PulseChaseTimeSeries(Series):
    item_type = 'pulse_chase_time_series'
    schema = load_schema('encoded:schemas/pulse_chase_time_series.json')
    embedded = Series.embedded + [
        'related_datasets.analyses',
    ]


@collection(
    name='disease-series',
    unique_key='accession',
    properties={
        'title': "Disease series",
        'description': 'A series that groups experiments investigating samples with an identified disease.',
    })
class DiseaseSeries(Series):
    item_type = 'disease_series'
    schema = load_schema('encoded:schemas/disease_series.json')
    embedded = Series.embedded + [
        'related_datasets.analyses',
    ]
    
    rev = Dataset.rev.copy()
    rev.update({
        'superseded_by': ('DiseaseSeries', 'supersedes')
    })

    @calculated_property(schema={
        "title": "Superseded by",
        "type": "array",
        "items": {
            "type": ['string', 'object'],
            "linkFrom": "DiseaseSeries.supersedes",
        },
        "notSubmittable": True,
    })
    def superseded_by(self, request, superseded_by):
        return paths_filtered_by_status(request, superseded_by)


@collection(
    name='multiomics-series',
    unique_key='accession',
    properties={
        'title': "Multiomics series",
        'description': 'Experimental data investigating biosamples via multiple genomic analyses.',
    })
class MultiomicsSeries(Series):
    item_type = 'multiomics_series'
    schema = load_schema('encoded:schemas/multiomics_series.json')
    embedded = Series.embedded + [
        'related_datasets.analyses',
    ]

    rev = Dataset.rev.copy()
    rev.update({
        'superseded_by': ('MultiomicsSeries', 'supersedes')
    })

    @calculated_property(schema={
        "title": "Superseded by",
        "type": "array",
        "items": {
            "type": ['string', 'object'],
            "linkFrom": "MultiomicsSeries.supersedes",
        },
        "notSubmittable": True,
    })
    def superseded_by(self, request, superseded_by):
        return paths_filtered_by_status(request, superseded_by)
