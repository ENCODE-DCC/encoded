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

from .shared_calculated_properties import CalculatedAssayTermID


@abstract_collection(
    name='quality-metrics',
    properties={
        'title': "Quality metrics",
        'description': 'Listing of all types of quality metric.',
    })
class QualityMetric(ItemWithAttachment, CalculatedAssayTermID, Item):
    base_types = ['QualityMetric'] + Item.base_types


@collection(
    name='star-quality-metrics',
    properties={
        'title': "STAR mapping Quality Metrics",
        'description': 'A set of QC metrics from STAR RNA-seq mapping',
    })
class StarQualityMetric(QualityMetric, CalculatedAssayTermID):
    item_type = 'star_quality_metric'
    schema = load_schema('encoded:schemas/star_quality_metric.json')


@collection(
    name='bismark-quality-metrics',
    properties={
        'title': "Bismark (WGBS) mapping quality metrics",
        'description': 'A set of QC metrics from Bismark mapping for WGBS',
    })
class BismarkQualityMetric(QualityMetric, CalculatedAssayTermID):
    item_type = 'bismark_quality_metric'
    schema = load_schema('encoded:schemas/bismark_quality_metric.json')


@collection(
    name='cpg-correlation-quality-metrics',
    properties={
        'title': "WGBS replicate correlation CpG quality metrics",
        'description': 'A set of QC metrics from WGBS replicate CpG correlations',
    })
class CpgCorrelationQualityMetric(QualityMetric, CalculatedAssayTermID):
    item_type = 'cpg_correlation_quality_metric'
    schema = load_schema('encoded:schemas/cpg_correlation_quality_metric.json')


@collection(
    name='chipseq-filter-quality-metrics',
    properties={
        'title': "Quality metrics for ChIP-seq (filtering step)",
        'description': 'A set of QC metrics used ChIP-seq experiments (filtering step)',
    })
class ChipSeqFilterQualityMetric(QualityMetric, CalculatedAssayTermID):
    item_type = 'chipseq_filter_quality_metric'
    schema = load_schema('encoded:schemas/chipseq_filter_quality_metric.json')


@collection(
    name='correlation-quality-metrics',
    properties={
        'title': "Correlation of two replicate datasets",
        'description': 'Correlation QC metrics for two replicate sets of items',
    })
class CorrelationQualityMetric(QualityMetric, CalculatedAssayTermID):
    item_type = 'correlation_quality_metric'
    schema = load_schema('encoded:schemas/correlation_quality_metric.json')


@collection(
    name='edwbamstats-quality-metrics',
    properties={
        'title': "Mapping Quality Metrics from 'edwBamStats'",
        'description': "A set of mapping QC metrics from 'edwBamStats'",
    })
class EdwbamstatsQualityMetric(QualityMetric, CalculatedAssayTermID):
    item_type = 'edwbamstats_quality_metric'
    schema = load_schema('encoded:schemas/edwbamstats_quality_metric.json')


@collection(
    name='hotspot-quality-metrics',
    properties={
        'title': "Peak Quality Metrics from the 'HotSpot' package",
        'description': "A set of peak QC metrics from the 'HotSpot' package",
    })
class HotspotQualityMetric(QualityMetric, CalculatedAssayTermID):
    item_type = 'hotspot_quality_metric'
    schema = load_schema('encoded:schemas/hotspot_quality_metric.json')


@collection(
    name='idr-summary-quality-metrics',
    properties={
        'title': "Irreproducible Discovery Rate (IDR) Summary Quality Metrics",
        'description': "A set of Peak Replicate QC metrics from 'idr'",
    })
class IdrSummaryQualityMetric(QualityMetric, CalculatedAssayTermID):
    item_type = 'idr_summary_quality_metric'
    schema = load_schema('encoded:schemas/idr_summary_quality_metric.json')


@collection(
    name='mad-quality-metrics',
    properties={
        'title': "Replicate Concordance Metrics using Mean Absolute Deviation (MAD)",
        'description': 'A set of QC metrics comparing two quantificiations '
                       'from replicates',
    })
class MadQualityMetric(QualityMetric, CalculatedAssayTermID):
    item_type = 'mad_quality_metric'
    schema = load_schema('encoded:schemas/mad_quality_metric.json')


@collection(
    name='complexity-xcorr-quality-metrics',
    properties={
        'title': "Quality Metrics for library complexity and cross-correlation of Mapping Sample",
        'description': 'A set of sampled mapping QC metrics',
    })
class ComplexityXcorrQualityMetric(QualityMetric, CalculatedAssayTermID):
    item_type = 'complexity_xcorr_quality_metric'
    schema = load_schema('encoded:schemas/complexity_xcorr_quality_metric.json')


@collection(
    name='duplicates-quality-metrics',
    properties={
        'title': "Quality Metrics for duplicates as counted by Picard (non-UMI) or stampipes (UMI).",
        'description': "A set of duplicate read QC metrics as detected by 'picard mark_duplicates' or 'stampipes mark_umi_dups'",
    })
class DuplicatesQualityMetric(QualityMetric, CalculatedAssayTermID):
    item_type = 'duplicates_quality_metric'
    schema = load_schema('encoded:schemas/duplicates_quality_metric.json')


@collection(
    name='filtering-quality-metrics',
    properties={
        'title': "Read Filtering Quality Metrics",
        'description': 'QC metrics documenting bam file read filtering',
    })
class FilteringQualityMetric(QualityMetric, CalculatedAssayTermID):
    item_type = 'filtering_quality_metric'
    schema = load_schema('encoded:schemas/filtering_quality_metric.json')


@collection(
    name='trimming-quality-metrics',
    properties={
        'title': "Read Trimming Quality Metrics",
        'description': 'QC metrics for documenting fastq file read trimming',
    })
class TrimmingQualityMetric(QualityMetric, CalculatedAssayTermID):
    item_type = 'trimming_quality_metric'
    schema = load_schema('encoded:schemas/trimming_quality_metric.json')


@collection(
    name='samtools-flagstats-quality-metrics',
    properties={
        'title': "Mapping Quality Metrics from 'samtools --flagstats'",
        'description': "A set of mapping QC metrics from 'samtools --flagstats'",
    })
class SamtoolsFlagstatsQualityMetric(QualityMetric, CalculatedAssayTermID):
    item_type = 'samtools_flagstats_quality_metric'
    schema = load_schema('encoded:schemas/samtools_flagstats_quality_metric.json')


@collection(
    name='samtools-stats-quality-metrics',
    properties={
        'title': "Mapping Quality Metrics from the Summary of 'samtools --stats'",
        'description': "A set of mapping QC metrics from 'samtools --stats'",
    })
class SamtoolsStatsQualityMetric(QualityMetric, CalculatedAssayTermID):
    item_type = 'samtools_stats_quality_metric'
    schema = load_schema('encoded:schemas/samtools_stats_quality_metric.json')


@collection(
    name='idr-quality-metrics',
    properties={
        'title': "IDR Metrics",
        'description': "Quality metrics from Irreproducible Discovery Rate (IDR) analysis",
    })
class IDRQualityMetric(QualityMetric, CalculatedAssayTermID):
    item_type = 'idr_quality_metric'
    schema = load_schema('encoded:schemas/idr_quality_metric.json')


@collection(
    name='histone-chipseq-quality-metrics',
    properties={
        'title': "Histone ChIP-seq Quality Metrics",
        'description': "Quality metrics from histone ChIP-seq peak overlap analysis",
    })
class HistoneChipSeqQualityMetric(QualityMetric, CalculatedAssayTermID):
    item_type = 'histone_chipseq_quality_metric'
    schema = load_schema('encoded:schemas/histone_chipseq_quality_metric.json')


@collection(
    name='generic-quality-metrics',
    properties={
        'title': "Generic Quality Metric",
        'description': "Generic quality metric",
    })
class GenericQualityMetric(QualityMetric, CalculatedAssayTermID):
    item_type = 'generic_quality_metric'
    schema = load_schema('encoded:schemas/generic_quality_metric.json')
