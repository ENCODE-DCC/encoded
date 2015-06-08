from contentbase.schema_utils import (
    load_schema,
)
from contentbase import (
    collection,
    calculated_property,
)
from .base import (
    Item,
    paths_filtered_by_status,
)


@collection(
    name='pipelines',
    properties={
        'title': 'Pipelines',
        'description': 'Listing of Pipelines',
    })
class Pipeline(Item):
    item_type = 'pipeline'
    schema = load_schema('encoded:schemas/pipeline.json')
    name_key = 'accession'
    embedded = [
        'documents',
        'documents.award',
        'documents.lab',
        'documents.submitted_by',
        'analysis_steps',
        'analysis_steps.parents',
        'analysis_steps.parents.software_versions',
        'analysis_steps.parents.software_versions.software',
        'analysis_steps.parents.software_versions.software.references',
        'analysis_steps.documents',
        'analysis_steps.software_versions',
        'analysis_steps.software_versions.software',
        'analysis_steps.software_versions.software.references',
    ]


@collection(
    name='analysis-steps',
    unique_key='analysis_step:name',
    properties={
        'title': 'Analysis steps',
        'description': 'Listing of Analysis Steps',
    })
class AnalysisStep(Item):
    item_type = 'analysis_step'
    schema = load_schema('encoded:schemas/analysis_step.json')
    name_key = 'name'
    embedded = [
        'software_versions',
        'software_versions.software',
        'parents'
    ]


@collection(
    name='analysis-step-runs',
    properties={
        'title': 'Analysis step runs',
        'description': 'Listing of Analysis Step Runs',
    })
class AnalysisStepRun(Item):
    item_type = 'analysis_step_run'
    schema = load_schema('encoded:schemas/analysis_step_run.json')
    embedded = [
        'analysis_step',
        'workflow_run',
        'qc_metrics',
        'output_files'
    ]
    rev = {
        'qc_metrics': ('quality_metric', 'step_run'),
        'output_files': ('file', 'step_run')
    }

    @calculated_property(schema={
        "title": "QC Metric",
        "type": "array",
        "items": {
            "type": ['string', 'object'],
            "linkFrom": "quality_metric.step_run",
        },
    })
    def qc_metrics(self, request, qc_metrics):
        return paths_filtered_by_status(request, qc_metrics)

    @calculated_property(schema={
        "title": "Output Files",
        "type": "array",
        "items": {
            "type": "string",
            "linkFrom": "file.step_run",
        },
    })
    def output_files(self, request, output_files):
        return paths_filtered_by_status(request, output_files)


@collection(
    name='workflow-runs',
    properties={
        'title': 'Workflow runs',
        'description': 'Listing of (DNANexus) Workflow Runs'
    })
class WorkflowRun(Item):
    item_type = 'workflow_run'
    schema = load_schema('encoded:schemas/workflow_run.json')
    embedded = [
        'pipeline'
    ]


@collection(
    name='quality-metrics',
    properties={
        'title': "QC metrics",
        'description': 'Listing of the QC metrics'
    })
class QualityMetric(Item):
    item_type = 'quality_metric'
    schema = load_schema('encoded:schemas/quality_metric.json')
