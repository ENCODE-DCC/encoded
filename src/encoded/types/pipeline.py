from ..schema_utils import (
    load_schema,
)
from ..contentbase import (
    location,
)
from .base import (
    Item,
)


@location(
    name='pipelines',
    properties={
        'title': 'Pipelines',
        'description': 'Listing of Pipelines',
    })
class Pipeline(Item):
    item_type = 'pipeline'
    schema = load_schema('pipeline.json')
    name_key = 'accession'

    embedded = [
        'documents',
        'analysis_steps',
        'analysis_steps.software_versions',
        'analysis_steps.software_versions.software',
        'analysis_steps.software_versions.software.references',
        'end_points',
    ]


@location(
    name='analysis-steps',
    properties={
        'title': 'Analysis steps',
        'description': 'Listing of Analysis Steps',
    })
class AnalysisStep(Item):
    item_type = 'analysis_step'
    schema = load_schema('analysis_step.json')

    embedded = [
        'software_versions',
        'software_versions.software',
        'parents'
    ]


@location(
    name='analysis-step-runs',
    properties={
        'title': 'Analysis step runs',
        'description': 'Listing of Analysis Step Runs',
    })
class AnalysisStepRun(Item):
    item_type = 'analysis_step_run'
    schema = load_schema('analysis_step_run.json')

    embedded = [
        'analysis_step',
    ]
