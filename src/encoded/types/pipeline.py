from contentbase import (
    collection,
    calculated_property,
    load_schema,
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
        'analysis_steps.documents',
        'analysis_steps.current_version.software_versions',
        'analysis_steps.current_version.software_versions.software',
        'analysis_steps.current_version.software_versions.software.references',
        'lab',
        'award.pi.lab',
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
    rev = {
        'pipelines': ('pipeline', 'analysis_steps'),
        'versions': ('analysis_step_version', 'analysis_step')
    }
    embedded = [
        'current_version',
        'current_version.software_versions',
        'current_version.software_versions.software',
        'parents'
    ]

    @calculated_property(schema={
        "title": "Pipelines",
        "type": "array",
        "items": {
            "type": 'string',
            "linkTo": "pipeline",
        },
    })
    def pipelines(self, request, pipelines):
        return paths_filtered_by_status(request, pipelines)

    @calculated_property(schema={
        "title": "Current version",
        "type": "string",
        "linkTo": "analysis_step_version",
    })
    def current_version(self, request, versions):
        version_objects = [
            request.embed(path, '@@object')
            for path in paths_filtered_by_status(request, versions)
        ]
        if version_objects:
            current = max(version_objects, key=lambda obj: obj['version'])
            return current['@id']


@collection(
    name='analysis-step-versions',
    properties={
        'title': 'Analysis step versions',
        'description': 'Listing of Analysis Step Versions',
    })
class AnalysisStepVersion(Item):
    item_type = 'analysis_step_version'
    schema = load_schema('encoded:schemas/analysis_step_version.json')

    def unique_keys(self, properties):
        keys = super(AnalysisStepVersion, self).unique_keys(properties)
        value = u'{analysis_step}/{version}'.format(**properties)
        keys.setdefault('analysis_step_version:analysis_step_version', []).append(value)
        return keys


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
