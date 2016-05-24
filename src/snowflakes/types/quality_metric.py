from snovault import (
    abstract_collection,
    collection,
    calculated_property,
    load_schema,
)
from snovault.attachment import ItemWithAttachment
from .base import (
    Item,
)


@abstract_collection(
    name='quality-metrics',
    properties={
        'title': "Quality metrics",
        'description': 'Listing of all types of quality metric.',
    })
class QualityMetric(ItemWithAttachment, Item):
    base_types = ['QualityMetric'] + Item.base_types


@collection(
    name='star-quality-metrics',
    properties={
        'title': "STAR mapping Quality Metrics",
        'description': 'A set of QC metrics from STAR RNA-seq mapping',
    })
class StarQualityMetric(QualityMetric):
    item_type = 'star_quality_metric'
    schema = load_schema('encoded:schemas/star_quality_metric.json')


@collection(
    name='fastqc-quality-metrics',
    properties={
        'title': "FastQC mapping quality metrics",
        'description': 'A set of QC metrics from FastQC',
    })
class FastqcQualityMetric(QualityMetric):
    item_type = 'fastqc_quality_metric'
    schema = load_schema('encoded:schemas/fastqc_quality_metric.json')


@collection(
    name='bismark-quality-metrics',
    properties={
        'title': "Bismark (WGBS) mapping quality metrics",
        'description': 'A set of QC metrics from Bismark mapping for WGBS',
    })
class BismarkQualityMetric(QualityMetric):
    item_type = 'bismark_quality_metric'
    schema = load_schema('encoded:schemas/bismark_quality_metric.json')


@collection(
    name='cpg-correlation-quality-metrics',
    properties={
        'title': "WGBS replicate correlation CpG quality metrics",
        'description': 'A set of QC metrics from WGBS replicate CpG correlations',
    })
class CpgCorrelationQualityMetric(QualityMetric):
    item_type = 'cpg_correlation_quality_metric'
    schema = load_schema('encoded:schemas/cpg_correlation_quality_metric.json')


@collection(
    name='encode2-chipseq-quality-metrics',
    properties={
        'title': "Quality metrics for ChIP-seq (ENCODE2)",
        'description': 'A set of QC metrics used for ENCODE2 ChIP-seq experiments',
    })
class Encode2ChipSeqQualityMetric(QualityMetric):
    item_type = 'encode2_chipseq_quality_metric'
    schema = load_schema('encoded:schemas/encode2_chipseq_quality_metric.json')


@collection(
    name='chipseq-filter-quality-metrics',
    properties={
        'title': "Quality metrics for ChIP-seq (filtering step)",
        'description': 'A set of QC metrics used ChIP-seq experiments (filtering step)',
    })
class ChipSeqFilterQualityMetric(QualityMetric):
    item_type = 'chipseq_filter_quality_metric'
    schema = load_schema('encoded:schemas/chipseq_filter_quality_metric.json')


@collection(
    name='bigwigcorrelate-quality-metrics',
    properties={
        'title': "Pearson's Correlation of two bigWig Signal Files.",
        'description': "A set of signal replicate QC metrics from 'bigWigCorrelate'",
    })
class BigwigcorrelateQualityMetric(QualityMetric):
    item_type = 'bigwigcorrelate_quality_metric'
    schema = load_schema('encoded:schemas/bigwigcorrelate_quality_metric.json')


@collection(
    name='dnase-peak-quality-metrics',
    properties={
        'title': "Counts of DNase Regions and Hotspots",
        'description': 'A set of peak QC metrics for regions and hotspots',
    })
class DnasePeakQualityMetric(QualityMetric):
    item_type = 'dnase_peak_quality_metric'
    schema = load_schema('encoded:schemas/dnase_peak_quality_metric.json')


@collection(
    name='edwbamstats-quality-metrics',
    properties={
        'title': "Mapping Quality Metrics from 'edwBamStats'",
        'description': "A set of mapping QC metrics from 'edwBamStats'",
    })
class EdwbamstatsQualityMetric(QualityMetric):
    item_type = 'edwbamstats_quality_metric'
    schema = load_schema('encoded:schemas/edwbamstats_quality_metric.json')


@collection(
    name='edwcomparepeaks-quality-metrics',
    properties={
        'title': "Comparison of two sets of Called Peaks from 'edwComparePeaks'",
        'description': "A set of peak replicate QC metrics from 'edwComparePeaks'",
    })
class EdwcomparepeaksQualityMetric(QualityMetric):
    item_type = 'edwcomparepeaks_quality_metric'
    schema = load_schema('encoded:schemas/edwcomparepeaks_quality_metric.json')


@collection(
    name='hotspot-quality-metrics',
    properties={
        'title': "Peak Quality Metrics from the 'HotSpot' package",
        'description': "A set of peak QC metrics from the 'HotSpot' package",
    })
class HotspotQualityMetric(QualityMetric):
    item_type = 'hotspot_quality_metric'
    schema = load_schema('encoded:schemas/hotspot_quality_metric.json')


@collection(
    name='idr-summary-quality-metrics',
    properties={
        'title': "Irreproducible Discovery Rate (IDR) Summary Quality Metrics",
        'description': "A set of Peak Replicate QC metrics from 'idr'",
    })
class IdrSummaryQualityMetric(QualityMetric):
    item_type = 'idr_summary_quality_metric'
    schema = load_schema('encoded:schemas/idr_summary_quality_metric.json')


@collection(
    name='mad-quality-metrics',
    properties={
        'title': "Replicate Concordance Metrics using Mean Absolute Deviation (MAD)",
        'description': 'A set of QC metrics comparing two quantificiations '
                       'from replicates',
    })
class MadQualityMetric(QualityMetric):
    item_type = 'mad_quality_metric'
    schema = load_schema('encoded:schemas/mad_quality_metric.json')


@collection(
    name='pbc-quality-metrics',
    properties={
        'title': "Quality Metrics 'PCR Bottleneck Coefficient' (PBC) of Mapping Sample",
        'description': 'A set of sampled mapping QC metrics',
    })
class PbcQualityMetric(QualityMetric):
    item_type = 'pbc_quality_metric'
    schema = load_schema('encoded:schemas/pbc_quality_metric.json')


@collection(
    name='phantompeaktooks-spp-quality-metrics',
    properties={
        'title': "Mapping quality metrics from 'phantompeakqualtools run_spp.R'",
        'description': "A set of sampled mapping QC metrics from 'phantompeakqualtools run_spp.R'",
    })
class PhantompeaktoolsSppQualityMetric(QualityMetric):
    item_type = 'phantompeaktools_spp_quality_metric'
    schema = load_schema('encoded:schemas/phantompeaktools_spp_quality_metric.json')


@collection(
    name='samtools-flagstats-quality-metrics',
    properties={
        'title': "Mapping Quality Metrics from 'samtools --flagstats'",
        'description': "A set of mapping QC metrics from 'samtools --flagstats'",
    })
class SamtoolsFlagstatsQualityMetric(QualityMetric):
    item_type = 'samtools_flagstats_quality_metric'
    schema = load_schema('encoded:schemas/samtools_flagstats_quality_metric.json')


@collection(
    name='samtools-stats-quality-metrics',
    properties={
        'title': "Mapping Quality Metrics from the Summary of 'samtools --stats'",
        'description': "A set of mapping QC metrics from 'samtools --stats'",
    })
class SamtoolsStatsQualityMetric(QualityMetric):
    item_type = 'samtools_stats_quality_metric'
    schema = load_schema('encoded:schemas/samtools_stats_quality_metric.json')


@collection(
    name='idr-quality-metrics',
    properties={
        'title': "IDR Metrics",
        'description': "Quality metrics from Irreproducible Discovery Rate (IDR) analysis",
    })
class IDRQualityMetric(QualityMetric):
    item_type = 'idr_quality_metric'
    schema = load_schema('encoded:schemas/idr_quality_metric.json')


@collection(
    name='generic-quality-metrics',
    properties={
        'title': "Generic Quality Metric",
        'description': "Generic quality metric",
    })
class GenericQualityMetric(QualityMetric):
    item_type = 'generic_quality_metric'
    schema = load_schema('encoded:schemas/generic_quality_metric.json')
