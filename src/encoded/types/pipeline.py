from snovault import (
    collection,
    calculated_property,
    load_schema,
)
from .base import (
    Item,
    paths_filtered_by_status,
)
from .shared_calculated_properties import (
    CalculatedAssayTermID
)

import re

@collection(
    name='pipelines',
    unique_key='accession',
    properties={
        'title': 'Pipelines',
        'description': 'Listing of Pipelines',
    })
class Pipeline(Item, CalculatedAssayTermID):
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
        'analysis_steps.pipelines',
        'analysis_steps.current_version.software_versions',
        'analysis_steps.current_version.software_versions.software',
        'analysis_steps.current_version.software_versions.software.references',
        'analysis_steps.versions',
        'analysis_steps.versions.software_versions',
        'analysis_steps.versions.software_versions.software',
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
        'pipelines': ('Pipeline', 'analysis_steps'),
        'versions': ('AnalysisStepVersion', 'analysis_step')
    }
    embedded = [
        'current_version',
        'current_version.software_versions',
        'current_version.software_versions.software',
        'parents'
    ]

    ''' Add this back to use as @id if that change can be made. Current names will also need to be updated.
    @calculated_property(schema={
        "title": "Full name",
        "type": "string",
        "description": "Full name of the analysis step with major version number.",
        "comment": "Do not submit. Value is automatically assigned by the server."
    })
    def fullname(self, name, major_version):
        return u'{}-{}'.format(name, major_version)
    '''

    @calculated_property(schema={
        "title": "Pipelines",
        "type": "array",
        "items": {
            "type": 'string',
            "linkTo": "Pipeline",
        },
    })
    def pipelines(self, request, pipelines):
        return paths_filtered_by_status(request, pipelines)

    @calculated_property(schema={
        "title": "Current version",
        "type": "string",
        "linkTo": "AnalysisStepVersion",
    })
    def current_version(self, request, versions):
        version_objects = [
            request.embed(path, '@@object')
            for path in paths_filtered_by_status(request, versions)
        ]
        if version_objects:
            current = max(version_objects, key=lambda obj: obj['minor_version'])
            return current['@id']

    @calculated_property(schema={
        "title": "Versions",
        "type": "array",
        "items": {
            "type": 'string',
            "linkTo": "AnalysisStepVersion",
        },
    })
    def versions(self, request, versions):
        return paths_filtered_by_status(request, versions)


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
        value = u'{analysis_step}/{minor_version}'.format(**properties)
        keys.setdefault('analysis_step_version:analysis_step_minor_version', []).append(value)
        return keys

    @calculated_property(schema={
        "title": "Name",
        "type": "string",
    })
    def name(self, analysis_step, minor_version):
        analysis_step = re.sub('^\/analysis-steps\/', '', analysis_step)
        analysis_step = re.sub('/', '', analysis_step)
        return u'{}-{}'.format(analysis_step, minor_version)


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
        'analysis_step_version.analysis_step',
    ]
    # Avoid using reverse links on this object as invalidating a virtual
    # step_run can cause thousands of objects to be reindexed.
