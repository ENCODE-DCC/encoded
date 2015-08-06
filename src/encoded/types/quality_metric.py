from contentbase import (
    collection,
    calculated_property,
    load_schema,
)
from contentbase.attachment import ItemWithAttachment
from .base import (
    Item,
)


class QualityMetric(Item):
    item_type = 'quality_metric'
    base_types = ['quality_metric'] + Item.base_types


@collection(
    name='mad-qc-metrics',
    properties={
        'title': "Replicate Concordance Metrics using Mean Absolute Deviation (MAD)",
        'description': 'A set of QC metrics comparing two quantificiations '
                       'from replicates',
    })
class MadQcMetric(QualityMetric):
    item_type = 'mad_qc_metric'
    schema = load_schema('encoded:schemas/mad_qc_metric.json')


@collection(
    name='star-qc-metrics',
    properties={
        'title': "STAR mapping Quality Metrics",
        'description': 'A set of QC metrics from STAR RNA-seq mapping',
    })
class StarQcMetric(QualityMetric):
    item_type = 'star_qc_metric'
    schema = load_schema('encoded:schemas/star_qc_metric.json')


@collection(
    name='fastqc-qc-metrics',
    properties={
        'title': "FastQC mapping quality metrics",
        'description': 'A set of QC metrics from FastQC',
    })
class FastqcQcMetric(QualityMetric, ItemWithAttachment):
    item_type = 'fastqc_qc_metric'
    schema = load_schema('encoded:schemas/fastqc_qc_metric.json')

    @calculated_property(schema={
        "title": "Applies to",
        "type": "array",
        "items": {
            "type": 'string',
            "linkTo": "file",
        },
    })
    def applies_to(self, request, step_run):
        input_files = request.embed(step_run, '@@object')['input_files']
        return input_files


@collection(
    name='bismark-qc-metrics',
    properties={
        'title': "Bismark (WGBS) mapping quality metrics",
        'description': 'A set of QC metrics from Bismark mapping for WGBS',
    })
class BismarkQcMetric(QualityMetric):
    item_type = 'bismark_qc_metric'
    schema = load_schema('encoded:schemas/bismark_qc_metric.json')

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
    schema = load_schema('encoded:schemas/encode2_chipseq_qc_metric.json')

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
    schema = load_schema('encoded:schemas/chipseq_filter_qc_metric.json')

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
    name='samtools-flagstats-qc-metrics',
    properties={
        'title': "Mapping Quality Metrics from 'samtools --flagstats'",
        'description': "A set of mapping QC metrics from 'samtools --flagstats'",
    })
class SamtoolsFlagstatsQcMetric(QualityMetric):
    item_type = 'samtools_flagstats_qc_metric'
    schema = load_schema('encoded:schemas/samtools_flagstats_qc_metric.json')


@collection(
    name='samtools-stats-qc-metrics',
    properties={
        'title': "Mapping Quality Metrics from the Summary of 'samtools --stats'",
        'description': "A set of mapping QC metrics from 'samtools --stats'",
    })
class SamtoolsStatsQcMetric(QualityMetric):
    item_type = 'samtools_stats_qc_metric'
    schema = load_schema('encoded:schemas/samtools_stats_qc_metric.json')


@collection(
    name='bigwigcorrelate-qc-metrics',
    properties={
        'title': "Pearson's Correlation of two bigWig Signal Files.",
        'description': "A set of signal replicate QC metrics from 'bigWigCorrelate'",
    })
class BigwigcorrelateQcMetric(QualityMetric):
    item_type = 'bigwigcorrelate_qc_metric'
    schema = load_schema('encoded:schemas/bigwigcorrelate_qc_metric.json')


@collection(
    name='dnase-peak-qc-metrics',
    properties={
        'title': "Counts of DNase Regions and Hotspots",
        'description': 'A set of peak QC metrics for regions and hotspots',
    })
class DnasePeakQcMetric(QualityMetric):
    item_type = 'dnase_peak_qc_metric'
    schema = load_schema('encoded:schemas/dnase_peak_qc_metric.json')


@collection(
    name='edwbamstats-qc-metrics',
    properties={
        'title': "Mapping Quality Metrics from 'edwBamStats'",
        'description': "A set of mapping QC metrics from 'edwBamStats'",
    })
class EdwbamstatsQcMetric(QualityMetric):
    item_type = 'edwbamstats_qc_metric'
    schema = load_schema('encoded:schemas/edwbamstats_qc_metric.json')


@collection(
    name='edwcomparepeaks-qc-metrics',
    properties={
        'title': "Comparison of two sets of Called Peaks from 'edwComparePeaks'",
        'description': "A set of peak replicate QC metrics from 'edwComparePeaks'",
    })
class EdwcomparepeaksQcMetric(QualityMetric):
    item_type = 'edwcomparepeaks_qc_metric'
    schema = load_schema('encoded:schemas/edwcomparepeaks_qc_metric.json')


@collection(
    name='hotspot-qc-metrics',
    properties={
        'title': "Peak Quality Metrics from the 'HotSpot' package",
        'description': "A set of peak QC metrics from the 'HotSpot' package",
    })
class HotspotQcMetric(QualityMetric):
    item_type = 'hotspot_qc_metric'
    schema = load_schema('encoded:schemas/hotspot_qc_metric.json')


@collection(
    name='idr-summary-qc-metrics',
    properties={
        'title': "Irreproducible Discovery Rate (IDR) Summary Quality Metrics",
        'description': "A set of Peak Replicate QC metrics from 'idr'",
    })
class SamtoolsFlagstatsQcMetric(QualityMetric):
    item_type = 'idr_summary_qc_metric'
    schema = load_schema('encoded:schemas/idr_summary_qc_metric.json')


@collection(
    name='pbc-qc-metrics',
    properties={
        'title': "Quality Metrics 'PCR Bottleneck Coefficient' (PBC) of Mapping Sample",
        'description': 'A set of sampled mapping QC metrics',
    })
class PbcQcMetric(QualityMetric):
    item_type = 'pbc_qc_metric'
    schema = load_schema('encoded:schemas/pbc_qc_metric.json')


@collection(
    name='phantompeaktooks-spp-qc-metrics',
    properties={
        'title': "Mapping quality metrics from 'phantompeakqualtools run_spp.R'",
        'description': "A set of sampled mapping QC metrics from 'phantompeakqualtools run_spp.R'",
    })
class PhantompeaktooksSppQcMetric(QualityMetric):
    item_type = 'phantompeaktooks_spp_qc_metric'
    schema = load_schema('encoded:schemas/phantompeaktooks_spp_qc_metric.json')

