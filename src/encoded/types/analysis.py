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


def is_desired_object(obj, filters):
    if not isinstance(obj, dict) or not isinstance(filters, dict):
        return
    # Keys/Conditions in filters are combined with AND
    for key in filters:
        if key not in obj:
            return False
        if isinstance(filters[key], list):
            if isinstance(obj[key], list):
                if sorted(filters[key]) != sorted(obj[key]):
                    return False
            elif obj[key] not in filters[key]:
                return False
        else:
            if isinstance(obj[key], list):
                if filters[key] not in obj[key]:
                    return False
            elif obj[key] != filters[key]:
                return False
    return True


def make_quality_metric_report(request, file_objects, quality_metric_definition):
    quality_metrics_report = {quality_metric_definition['report_name']: []}
    for f_obj in file_objects:
        if not is_desired_object(
            f_obj, quality_metric_definition.get('file_filters', {})
        ):
            continue
        for qm in f_obj.get('quality_metrics', []):
            qm_obj = request.embed(qm, '@@object')
            if not is_desired_object(
                qm_obj,
                quality_metric_definition.get('quality_metric_filters', {})
            ):
                continue
            qm_report = {
                'metric': qm_obj.get(
                    quality_metric_definition['quality_metric_name']
                )
            }
            if qm_report['metric'] is None:
                continue
            qm_report['biological_replicates'] = f_obj.get(
                'biological_replicates', []
            )
            standard = quality_metric_definition.get('standard', {})
            # The following order matters and depends a lot on the schema
            # definition.
            for qm_level in [
                'pass',
                'warning',
                'not_compliant',
                'error',
                None
            ]:
                if qm_level not in standard:
                    continue
                threshold = standard[qm_level]
                if isinstance(threshold, str):
                    qualified = qm_report['metric'] == threshold
                else:
                    qualified = qm_report['metric'] >= threshold
                if qualified:
                    break
            if qm_level is not None:
                qm_report['quality'] = qm_level
            quality_metrics_report[
                quality_metric_definition['report_name']
            ].append(qm_report)
    return quality_metrics_report


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

    set_status_up = [
        'files',
        'documents',
    ]
    set_status_down = [
        'files',
        'documents',
    ]

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

    @calculated_property(define=True, schema={
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

    @calculated_property(define=True, schema={
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

    @calculated_property(define=True, schema={
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
    def pipeline_award_rfas(self, request, pipelines):
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

    @calculated_property(define=True, schema={
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
    def pipeline_labs(self, request, pipelines):
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

    # Don't specify schema as it is highly variable
    @calculated_property()
    def quality_metrics_report(self, request, files, quality_standard=None):
        if not quality_standard:
            return
        qm_defs = request.embed(
            quality_standard, '@@object?skip_calculated=true'
        ).get('definitions', [])
        file_objects = [
            request.embed(
                f,
                '@@object_with_select_calculated_properties?field=quality_metrics&field=biological_replicates'
            )
            for f in files
        ]
        quality_metrics_report = {}
        for qm_def in qm_defs:
            quality_metrics_report.update(
                make_quality_metric_report(
                    request=request,
                    file_objects=file_objects,
                    quality_metric_definition=qm_def,
                )
            )
        return quality_metrics_report

    @calculated_property(schema={
        "title": "Title",
        "type": "string",
    })
    def title(self,
        assembly,
        genome_annotation,
        pipeline_labs,
        pipeline_award_rfas,
        pipeline_version=None
    ):
        analysis_type = 'Lab custom'
        if len(set(pipeline_labs)) > 1:
            analysis_type = 'Mixed pipelines'
        elif pipeline_labs == ['/labs/encode-processing-pipeline/']:
            analysis_type = 'Uniform'
            if pipeline_award_rfas:
                analysis_type = ', '.join(pipeline_award_rfas)
                if len(pipeline_award_rfas) > 1:
                    analysis_type = f'Mixed uniform {analysis_type}'   
        analysis_version = ''
        if pipeline_version and not analysis_type.startswith('Mixed uniform'):
            analysis_version = f' v{pipeline_version}'
        analysis_assembly = ''
        if assembly:
            analysis_assembly = f' {assembly}'
        analysis_annotation = ''
        if genome_annotation:
            if not (genome_annotation == 'mixed' and assembly == 'mixed'):
                analysis_annotation = f' {genome_annotation}'
        return f'{analysis_type}{analysis_version}{analysis_assembly}{analysis_annotation}'


@collection(
    name='quality-standards',
    unique_key='quality_standard:name',
    properties={
        'title': 'Quality standards',
        'description': 'Listing of Quality Standards',
    })
class QualityStandard(Item):
    item_type = 'quality_standard'
    schema = load_schema('encoded:schemas/quality_standard.json')

    def unique_keys(self, properties):
        keys = super(QualityStandard, self).unique_keys(properties)
        keys.setdefault('quality_standard:name', []).append(self._name(properties))
        return keys

    @property
    def __name__(self):
        properties = self.upgrade_properties()
        return self._name(properties)

    def _name(self, properties):
        return properties['name']
