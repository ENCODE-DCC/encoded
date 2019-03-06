from snovault import (
    collection,
    calculated_property,
    load_schema,
)
from .base import paths_filtered_by_status
from .dataset import Dataset


@collection(
    name='analyses',
    unique_key='accession',
    properties={
        'title': 'Analyses',
        'description': 'Collection of analyses',
    })
class Analysis(Dataset):
    item_type = 'analysis'
    schema = load_schema('encoded:schemas/analysis.json')
    rev = {
        'analysis_step_runs': ('AnalysisStepRun', 'analysis'),
        'superseded_by': ('Analysis', 'supersedes'),
    }
    embedded = [
        'analysis_step_runs',
        'files',
        'submitted_by',
    ]
    name_key = 'accession'
    set_status_up = [
        'analysis_step_runs',
        'original_files',
    ]
    set_status_down = [
        'analysis_step_runs',
        'original_files',
    ]

    @calculated_property(schema={
        "title": "Individual step run(s)",
        "description": "Individual steps in this analysis.",
        "type": "array",
        "items": {
            "title": "Analysis step run",
            "description": "One analysis step in an analysis.",
            "comment": "See analysis_step_run.json for available identifiers.",
            "type": "string",
            "linkTo": "AnalysisStepRun"
        },
        "notSubmittable": True,
    })
    def analysis_step_runs(self, request, analysis_step_runs):
        return paths_filtered_by_status(request, analysis_step_runs)

    @calculated_property(define=True, schema={
        "title": "Original files",
        "type": "array",
        "items": {
            "type": ['string', 'object'],
            "linkFrom": "File.dataset",
        },
        "notSubmittable": True,
    })
    def original_files(self, request, analysis_step_runs):
        output_files = set()
        for step_run in analysis_step_runs:
            step_run_obj = request.embed(step_run, '@@object?skip_calculated=true')
            if 'output_files' in step_run_obj:
                output_files |= set(step_run_obj['output_files'])
        return paths_filtered_by_status(request, output_files)

    # Override the analyses property of dataset
    @calculated_property()
    def analyses(self):
        return None

    @calculated_property(schema={
        "description": "Platforms used in this analysis.",
        "title": "Platforms",
        "type": "array",
        "items": {
            "type": 'string',
        },
        "notSubmittable": True,
    })
    def platforms(self, request, analysis_step_runs):
        platforms = set()
        for step_run in analysis_step_runs:
            step_run_obj = request.embed(step_run, '@@object?skip_calculated=true')
            if 'platform' in step_run_obj:
                platforms.add(step_run_obj['platform'])
        return sorted(platforms)

    @calculated_property(schema={
        "title": "Superseded by",
        "type": "array",
        "items": {
            "type": ['string', 'object'],
            "linkFrom": "Analysis.supersedes",
        },
        "notSubmittable": True,
    })
    def superseded_by(self, request, superseded_by):
        return paths_filtered_by_status(request, superseded_by)
