from snovault import (
    calculated_property,
    collection,
    load_schema,
)
from snovault.util import try_to_get_field_from_item_with_skip_calculated_first
from .base import (
    Item,
    paths_filtered_by_status
)


@collection(
    name='analyses',
    unique_key='accession',
    properties={
        'title': 'Analyses',
        'description': 'Listing of analysis',
    })
class Analysis(Item):
    item_type = 'analysis'
    schema = load_schema('encoded:schemas/analysis.json')
    name_key = 'accession'
    embedded = [
        'files',
        'files.quality_metrics',
        'pipeline_labs',
    ]

    rev = {
        'superseded_by': ('Analysis', 'supersedes'),
    }

    @calculated_property(schema={
        "title": "Datasets",
        "description": "Datasets the analysis belongs to.",
        "comment": "Do not submit. This field is calculated from files in this analysis.",
        "type": "array",
        "notSubmittable": True,
        "uniqueItems": True,
        "items": {
            "title": "Dataset",
            "description": "The dataset the analysis belongs to.",
            "type": "string",
            "linkTo": "Dataset"
        }
    })
    def datasets(self, request, files):
        return sorted({
            dataset
            for dataset in [
                try_to_get_field_from_item_with_skip_calculated_first(
                    request, 'dataset', f
                )
                for f in files
            ]
            if dataset is not None
        })

    file_schema = load_schema(
        'encoded:schemas/file.json'
    )

    @calculated_property(schema={
        "title": "Assembly",
        "description": "A genome assembly on which this analysis is performed.",
        "comment": "Do not submit. This field is calculated from files in this analysis.",
        "type": "string",
        "notSubmittable": True,
        "enum": ["mixed", *file_schema["properties"]["assembly"]["enum"]],
    })
    def assembly(self, request, files):
        assemblies = {
            assembly
            for assembly in [
                try_to_get_field_from_item_with_skip_calculated_first(
                    request, 'assembly', f
                )
                for f in files
            ]
            if assembly is not None
        }
        if len(assemblies) > 1:
            return 'mixed'
        if len(assemblies) == 1:
            return assemblies.pop()
        if len(assemblies) < 1:
            return

    @calculated_property(schema={
        "title": "Genome Annotation",
        "description": "A genome annotation on which this analysis is performed.",
        "comment": "Do not submit. This field is calculated from files in this analysis.",
        "type": "string",
        "notSubmittable": True,
        "enum": ["mixed", *file_schema["properties"]["genome_annotation"]["enum"]],
    })
    def genome_annotation(self, request, files):
        genome_annotations = {
            genome_annotation
            for genome_annotation in [
                try_to_get_field_from_item_with_skip_calculated_first(
                    request, 'genome_annotation', f
                )
                for f in files
            ]
            if genome_annotation is not None
        }
        if len(genome_annotations) > 1:
            return 'mixed'
        if len(genome_annotations) == 1:
            return genome_annotations.pop()
        if len(genome_annotations) < 1:
            return

    @calculated_property(
        define=True,
        schema={
            "title": "Pipelines",
            "description": "A list of pipelines used to generate this analysis.",
            "comment": "Do not submit. This field is calculated from files in this analysis.",
            "type": "array",
            "notSubmittable": True,
            "items": {
                "type": "string",
                "linkTo": "Pipeline"
            }
        }
    )
    def pipelines(self, request, files):
        pipelines = set()
        for f in files:
            file_object = request.embed(
                f,
                '@@object_with_select_calculated_properties?field=analysis_step_version'
            )
            if 'analysis_step_version' in file_object:
                analysis_step = request.embed(
                    file_object['analysis_step_version'],
                    '@@object?skip_calculated=true'
                )['analysis_step']
                pipelines |= set(
                    request.embed(
                        analysis_step,
                        '@@object_with_select_calculated_properties?field=pipelines'
                    ).get('pipelines', [])
                )
        return sorted(pipelines)

    @calculated_property(schema={
        "title": "Pipeline awards",
        "description": "A list of award bioproject phases to which pipelines "
                       "that used to generate this analysis belong to.",
        "comment": "Do not submit. This field is calculated from files in this analysis.",
        "type": "array",
        "notSubmittable": True,
        "items": {
            "type": "string"
        }
    })
    def pipeline_award_rfas(self, request, pipelines=[]):
        pipeline_award_rfas = set()
        for pipeline in pipelines:
            pipeline_object = request.embed(
                pipeline,
                '@@object?skip_calculated=true'
            )
            pipeline_award_rfas.add(
                request.embed(
                    pipeline_object['award'],
                    '@@object?skip_calculated=true'
                )['rfa']
            )
        return sorted(pipeline_award_rfas)

    @calculated_property(schema={
        "title": "Pipeline labs",
        "description": "A list of labs whose pipelines are used to generate this analysis.",
        "comment": "Do not submit. This field is calculated from files in this analysis.",
        "type": "array",
        "notSubmittable": True,
        "items": {
            "type": "string",
            "linkTo": "Lab"
        }
    })
    def pipeline_labs(self, request, pipelines=[]):
        return sorted({
            lab
            for lab in [
                try_to_get_field_from_item_with_skip_calculated_first(
                    request, 'lab', pipeline
                )
                for pipeline in pipelines
            ]
            if lab is not None
        })

    @calculated_property(schema={
        "title": "Superseded by",
        "description": "The analyses that supersede this analysis (i.e. is more preferable to use).",
        "comment": "Do not submit. Values in the list are reverse links of an analysis that supersedes.",
        "type": "array",
        "items": {
            "type": ['string', 'object'],
            "linkFrom": "Analysis.supersedes",
        },
        "notSubmittable": True,
    })
    def superseded_by(self, request, superseded_by):
        return paths_filtered_by_status(request, superseded_by)
