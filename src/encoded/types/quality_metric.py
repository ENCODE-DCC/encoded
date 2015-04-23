from ..schema_utils import (
    load_schema,
)
from ..contentbase import (
    collection,
    calculated_property,
)
from .base import (
    Item,
    paths_filtered_by_status,
)


class QualityMetric(Item):
    item_type = 'quality_metric'
    base_types = ['quality_metric'] + Item.base_types


@collection(
    name='mad-cc-lrna-metrics',
    properties={
        'title': "lRNA Replicate Concordance Metrics",
        'description': 'A set of QC metrics comparing two quantificiations from (long) RNA-seq replicates',
    })
class MadCCLrnaMetric(QualityMetric):
    item_type = 'mad_cc_lrna_qc_metric'
    schema = load_schema('mad_cc_lrna_qc_metric.json')

    @calculated_property(schema={
        "title": "Applies to",
        "type": "array",
        "items": {
            "type": 'string',
            "linkTo": "file",
        },
    })
    def applies_to(self, request, step_run):
        workflow_run = request.embed(step_run, '@@object').get('workflow_run', {})
        if workflow_run:
            input_files = request.embed(workflow_run, '@@object')['input_files']
        else:
            input_files = []
        return input_files


@collection(
    name='star-qc-metrics',
    properties={
        'title': "STAR mapping quality metrics",
        'description': 'A set of QC metrics from STAR RNA-seq mapping',
    })
class StarQcMetric(QualityMetric):
    item_type = 'star_qc_metric'
    schema = load_schema('star_qc_metric.json')

    @calculated_property(schema={
        "title": "Applies to",
        "type": "array",
        "items": {
            "type": 'string',
            "linkTo": "file",
        },
    })
    def applies_to(self, request, step_run):
        output_files = request.embed(step_run, '@@object')['output_files']
        return output_files


@collection(
    name='fastqc-qc-metrics',
    properties={
        'title': "FastQC mapping quality metrics",
        'description': 'A set of QC metrics from FastQC',
    })
class FastqcQcMetric(QualityMetric):
    item_type = 'fastqc_qc_metric'
    schema = load_schema('fastqc_qc_metric.json')

    @calculated_property(schema={
        "title": "Applies to",
        "type": "array",
        "items": {
            "type": 'string',
            "linkTo": "file",
        },
    })
    def applies_to(self, request, step_run):
        output_files = request.embed(step_run, '@@object')['output_files']
        return output_files


@collection(
    name='bismark-qc-metrics',
    properties={
        'title': "Bismark (WGBS) mapping quality metrics",
        'description': 'A set of QC metrics from Bismark mapping for WGBS',
    })
class BismarkQcMetric(QualityMetric):
    item_type = 'bismark_qc_metric'
    schema = load_schema('bismark_qc_metric.json')

    @calculated_property(schema={
        "title": "Applies to",
        "type": "array",
        "items": {
            "type": 'string',
            "linkTo": "file",
        },
    })
    def applies_to(self, request, step_run):
        output_files = request.embed(step_run, '@@object')['output_files']
        return output_files


@collection(
    name='encode2-chipseq-qc-metrics',
    properties={
        'title': "Quality metrics for ChIP-seq (ENCODE2)",
        'description': 'A set of QC metrics used for ENCODE2 ChIP-seq experiments',
    })
class Encode2ChipSeqQcMetric(QualityMetric):
    item_type = 'encode2_chipseq_qc_metric'
    schema = load_schema('encode2_chipseq_qc_metric.json')

    @calculated_property(schema={
        "title": "Applies to",
        "type": "array",
        "items": {
            "type": 'string',
            "linkTo": "file",
        },
    })
    def applies_to(self, request, step_run):
        output_files = request.embed(step_run, '@@object')['output_files']
        return output_files


@collection(
    name='chipseq-filter-qc-metrics',
    properties={
        'title': "Quality metrics for ChIP-seq (filtering step)",
        'description': 'A set of QC metrics used ChIP-seq experiments (filtering step)',
    })
class ChipSeqFilterQcMetric(QualityMetric):
    item_type = 'chipseq_filter_qc_metric'
    schema = load_schema('chipseq_filter_qc_metric.json')

    @calculated_property(schema={
        "title": "Applies to",
        "type": "array",
        "items": {
            "type": 'string',
            "linkTo": "file",
        },
    })
    def applies_to(self, request, step_run):
        output_files = request.embed(step_run, '@@object')['output_files']
        return output_files


@collection(
    name='flagstats-qc-metrics',
    properties={
        'title': "Mapping quality metrics from samtools --flagstats",
        'description': 'A set of mapping QC metrics from samtools --flagstats',
    })
class FlagstatsQcMetric(QualityMetric):
    item_type = 'flagstats_qc_metric'
    schema = load_schema('flagstats_qc_metric.json')

    @calculated_property(schema={
        "title": "Applies to",
        "type": "array",
        "items": {
            "type": 'string',
            "linkTo": "file",
        },
    })
    def applies_to(self, request, step_run):
        output_files = request.embed(step_run, '@@object')['output_files']
        return output_files
