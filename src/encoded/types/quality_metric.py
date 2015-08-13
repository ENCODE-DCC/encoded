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
    name='star-qc-metrics',
    properties={
        'title': "STAR mapping Quality Metrics",
        'description': 'A set of QC metrics from STAR RNA-seq mapping',
    })
class StarQcMetric(ItemWithAttachment, QualityMetric):
    item_type = 'star_quality_metric'
    schema = load_schema('encoded:schemas/star_quality_metric.json')


@collection(
    name='fastqc-qc-metrics',
    properties={
        'title': "FastQC mapping quality metrics",
        'description': 'A set of QC metrics from FastQC',
    })
class FastqcQcMetric(QualityMetric, ItemWithAttachment):
    item_type = 'fastqc_quality_metric'
    schema = load_schema('encoded:schemas/fastqc_quality_metric.json')


@collection(
    name='bismark-qc-metrics',
    properties={
        'title': "Bismark (WGBS) mapping quality metrics",
        'description': 'A set of QC metrics from Bismark mapping for WGBS',
    })
class BismarkQcMetric(QualityMetric):
    item_type = 'bismark_quality_metric'
    schema = load_schema('encoded:schemas/bismark_quality_metric.json')


@collection(
    name='encode2-chipseq-qc-metrics',
    properties={
        'title': "Quality metrics for ChIP-seq (ENCODE2)",
        'description': 'A set of QC metrics used for ENCODE2 ChIP-seq experiments',
    })
class Encode2ChipSeqQcMetric(QualityMetric):
    item_type = 'encode2_chipseq_quality_metric'
    schema = load_schema('encoded:schemas/encode2_chipseq_quality_metric.json')


@collection(
    name='chipseq-filter-qc-metrics',
    properties={
        'title': "Quality metrics for ChIP-seq (filtering step)",
        'description': 'A set of QC metrics used ChIP-seq experiments (filtering step)',
    })
class ChipSeqFilterQcMetric(QualityMetric):
    item_type = 'chipseq_filter_quality_metric'
    schema = load_schema('encoded:schemas/chipseq_filter_quality_metric.json')


@collection(
    name='bigwigcorrelate-qc-metrics',
    properties={
        'title': "Pearson's Correlation of two bigWig Signal Files.",
        'description': "A set of signal replicate QC metrics from 'bigWigCorrelate'",
    })
class BigwigcorrelateQcMetric(ItemWithAttachment, QualityMetric):
    item_type = 'bigwigcorrelate_quality_metric'
    schema = load_schema('encoded:schemas/bigwigcorrelate_quality_metric.json')


@collection(
    name='dnase-peak-qc-metrics',
    properties={
        'title': "Counts of DNase Regions and Hotspots",
        'description': 'A set of peak QC metrics for regions and hotspots',
    })
class DnasePeakQcMetric(ItemWithAttachment, QualityMetric):
    item_type = 'dnase_peak_quality_metric'
    schema = load_schema('encoded:schemas/dnase_peak_quality_metric.json')


@collection(
    name='edwbamstats-qc-metrics',
    properties={
        'title': "Mapping Quality Metrics from 'edwBamStats'",
        'description': "A set of mapping QC metrics from 'edwBamStats'",
    })
class EdwbamstatsQcMetric(ItemWithAttachment, QualityMetric):
    item_type = 'edwbamstats_quality_metric'
    schema = load_schema('encoded:schemas/edwbamstats_quality_metric.json')


@collection(
    name='edwcomparepeaks-qc-metrics',
    properties={
        'title': "Comparison of two sets of Called Peaks from 'edwComparePeaks'",
        'description': "A set of peak replicate QC metrics from 'edwComparePeaks'",
    })
class EdwcomparepeaksQcMetric(ItemWithAttachment, QualityMetric):
    item_type = 'edwcomparepeaks_quality_metric'
    schema = load_schema('encoded:schemas/edwcomparepeaks_quality_metric.json')


@collection(
    name='hotspot-qc-metrics',
    properties={
        'title': "Peak Quality Metrics from the 'HotSpot' package",
        'description': "A set of peak QC metrics from the 'HotSpot' package",
    })
class HotspotQcMetric(ItemWithAttachment, QualityMetric):
    item_type = 'hotspot_quality_metric'
    schema = load_schema('encoded:schemas/hotspot_quality_metric.json')


@collection(
    name='idr-summary-qc-metrics',
    properties={
        'title': "Irreproducible Discovery Rate (IDR) Summary Quality Metrics",
        'description': "A set of Peak Replicate QC metrics from 'idr'",
    })
class IdrSummaryQcMetric(ItemWithAttachment, QualityMetric):
    item_type = 'idr_summary_quality_metric'
    schema = load_schema('encoded:schemas/idr_summary_quality_metric.json')


@collection(
    name='mad-qc-metrics',
    properties={
        'title': "Replicate Concordance Metrics using Mean Absolute Deviation (MAD)",
        'description': 'A set of QC metrics comparing two quantificiations '
                       'from replicates',
    })
class MadQcMetric(ItemWithAttachment, QualityMetric):
    item_type = 'mad_quality_metric'
    schema = load_schema('encoded:schemas/mad_quality_metric.json')


@collection(
    name='pbc-qc-metrics',
    properties={
        'title': "Quality Metrics 'PCR Bottleneck Coefficient' (PBC) of Mapping Sample",
        'description': 'A set of sampled mapping QC metrics',
    })
class PbcQcMetric(ItemWithAttachment, QualityMetric):
    item_type = 'pbc_quality_metric'
    schema = load_schema('encoded:schemas/pbc_quality_metric.json')


@collection(
    name='phantompeaktooks-spp-qc-metrics',
    properties={
        'title': "Mapping quality metrics from 'phantompeakqualtools run_spp.R'",
        'description': "A set of sampled mapping QC metrics from 'phantompeakqualtools run_spp.R'",
    })
class PhantompeaktoolsSppQcMetric(ItemWithAttachment, QualityMetric):
    item_type = 'phantompeaktools_spp_quality_metric'
    schema = load_schema('encoded:schemas/phantompeaktools_spp_quality_metric.json')


@collection(
    name='samtools-flagstats-qc-metrics',
    properties={
        'title': "Mapping Quality Metrics from 'samtools --flagstats'",
        'description': "A set of mapping QC metrics from 'samtools --flagstats'",
    })
class SamtoolsFlagstatsQcMetric(ItemWithAttachment, QualityMetric):
    item_type = 'samtools_flagstats_quality_metric'
    schema = load_schema('encoded:schemas/samtools_flagstats_quality_metric.json')


@collection(
    name='samtools-stats-qc-metrics',
    properties={
        'title': "Mapping Quality Metrics from the Summary of 'samtools --stats'",
        'description': "A set of mapping QC metrics from 'samtools --stats'",
    })
class SamtoolsStatsQcMetric(ItemWithAttachment, QualityMetric):
    item_type = 'samtools_stats_quality_metric'
    schema = load_schema('encoded:schemas/samtools_stats_quality_metric.json')

