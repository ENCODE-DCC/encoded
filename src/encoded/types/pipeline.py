from ..schema_utils import (
    load_schema,
)
from ..contentbase import (
    location,
)
from .base import (
    ACCESSION_KEYS,
    ALIAS_KEYS,
    Collection,
)


@location('pipelines')
class Pipeline(Collection):
    item_type = 'pipeline'
    schema = load_schema('pipeline.json')
    properties = {
        'title': 'Pipelines',
        'description': 'Listing of Pipelines'
    }

    class Item(Collection.Item):
        name_key = 'accesion'
        keys = ACCESSION_KEYS + ALIAS_KEYS

        embedded = [
            'documents',
            'analysis_steps',
            'analysis_steps.software_versions',
            'analysis_steps.software_versions.software',
            'analysis_steps.software_versions.software.references'
        ]


@location('analysis-steps')
class AnalysisStep(Collection):
    item_type = 'analysis_step'
    schema = load_schema('analysis_step.json')
    properties = {
        'title': 'Analysis steps',
        'description': 'Listing of Analysis Steps'
    }

    class Item(Collection.Item):
        keys = ALIAS_KEYS

        embedded = [
            'software_versions',
            'software_versions.software',
            'parents'
        ]


@location('analysis-step-runs')
class AnalysisStepRun(Collection):
    item_type = 'analysis_step_run'
    schema = load_schema('analysis_step_run.json')
    properties = {
        'title': 'Analysis step runs',
        'description': 'Listing of Analysis Step Runs'
    }

    class Item(Collection.Item):
        keys = ALIAS_KEYS

        embedded = [
            'analysis_step',
            'workflow_run'
        ]


@location('qc-metrics')
class QcMetric(Collection):
    item_type = 'qc_metric',
    schema = load_schema('qc_metric')
    properties = {
        'title': "QC metrics",
        'description': 'Listing of the QC metrics'
    }

    class Item(Collection.Item):

        embedded = [
            'file'
        ]


@location('workflow-runs')
class WorkflowRun(Collection):
    item_type = 'workflow_run'
    schema = load_schema('workflow_run.json')
    properties = {
        'title': 'Workflow runs',
        'description': 'Listing of (DNANexus) Workflow Runs'
    }

    class Item(Collection.Item):
        keys = ALIAS_KEYS

        embedded = [
            'pipeline',
        ]
