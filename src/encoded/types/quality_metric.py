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
    set_status_up = [
        'step_run',
        ]
    set_status_down = []


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


@collection(
    name='micro-rna-quantification-quality-metrics',
    properties={
        'title': "microRNA Quantification Quality Metrics",
        'description': 'A set of microRNA pipeline quantification QC metrics',
    })
class MicroRnaQuantificationQualityMetric(QualityMetric, CalculatedAssayTermID):
    item_type = 'micro_rna_quantification_quality_metric'
    schema = load_schema('encoded:schemas/micro_rna_quantification_quality_metric.json')


@collection(
    name='micro-rna-mapping-quality-metrics',
    properties={
        'title': "microRNA Mapping Quality Metrics",
        'description': 'A set of microRNA pipeline quantification QC metrics',
    })
class MicroRnaMappingQualityMetric(QualityMetric, CalculatedAssayTermID):
    item_type = 'micro_rna_mapping_quality_metric'
    schema = load_schema('encoded:schemas/micro_rna_mapping_quality_metric.json')


@collection(
    name='long-read-rna-mapping-quality-metrics',
    properties={
        'title': "long read RNA Mapping Quality Metrics",
        'description': 'A set of long read RNA pipeline mapping QC metrics',
    })
class LongReadRnaMappingQualityMetric(QualityMetric, CalculatedAssayTermID):
    item_type = 'long_read_rna_mapping_quality_metric'
    schema = load_schema('encoded:schemas/long_read_rna_mapping_quality_metric.json')


@collection(
    name='long-read-rna-quantification-quality-metrics',
    properties={
        'title': "long read RNA Quantification Quality Metrics",
        'description': 'A set of long read RNA pipeline quantification QC metrics',
    })
class LongReadRnaQuantificationQualityMetric(QualityMetric, CalculatedAssayTermID):
    item_type = 'long_read_rna_quantification_quality_metric'
    schema = load_schema('encoded:schemas/long_read_rna_quantification_quality_metric.json')


@collection(
    name='gencode-category-quality-metrics',
    properties={
        'title': "GENCODE Category Quality Metrics",
        'description': 'A set of GENCODE category QC metrics each indicating counts per annotated biotype',
    })
class GencodeCategoryQualityMetric(QualityMetric, CalculatedAssayTermID):
    item_type = 'gencode_category_quality_metric'
    schema = load_schema('encoded:schemas/gencode_category_quality_metric.json')


@collection(
    name='atac-duplication-quality-metrics',
    properties={
        'title': "ATAC Duplication Quality Metric",
        'description': "ATAC Duplication quality metric",
    })
class AtacDuplicationQualityMetric(QualityMetric, CalculatedAssayTermID):
    item_type = 'atac_duplication_quality_metric'
    schema = load_schema('encoded:schemas/atac_duplication_quality_metric.json')


@collection(
    name='atac-frip-quality-metrics',
    properties={
        'title': "ATAC FRiP Quality Metric",
        'description': "ATAC FRiP quality metric",
    })
class AtacFRiPQualityMetric(QualityMetric, CalculatedAssayTermID):
    item_type = 'atac_frip_quality_metric'
    schema = load_schema('encoded:schemas/atac_frip_quality_metric.json')


@collection(
    name='atac-pbc-quality-metrics',
    properties={
        'title': "ATAC PBC Quality Metric",
        'description': "ATAC PBC quality metric",
    })
class AtacPbcQualityMetric(QualityMetric, CalculatedAssayTermID):
    item_type = 'atac_pbc_quality_metric'
    schema = load_schema('encoded:schemas/atac_pbc_quality_metric.json')


@collection(
    name='atac-reproducibility-quality-metrics',
    properties={
        'title': "ATAC Reproducibility Quality Metric",
        'description': "ATAC Reproducibility quality metric",
    })
class AtacReproducibilityQualityMetric(QualityMetric, CalculatedAssayTermID):
    item_type = 'atac_reproducibility_quality_metric'
    schema = load_schema('encoded:schemas/atac_reproducibility_quality_metric.json')


@collection(
    name='ataq-xcor-score-quality-metrics',
    properties={
        'title': "ATAC Cross Correlation Quality Metric",
        'description': "ATAC cross correlation quality metric",
    })
class AtacXcorScoreQualityMetric(QualityMetric, CalculatedAssayTermID):
    item_type = 'atac_xcor_score_quality_metric'
    schema = load_schema('encoded:schemas/atac_xcor_score_quality_metric.json')


@collection(
    name='ataqc-quality-metrics',
    properties={
        'title': "ATAC Quality Metric",
        'description': "ATAC quality metric",
    })
class AtaqcQualityMetric(QualityMetric, CalculatedAssayTermID):
    item_type = 'ataqc_quality_metric'
    schema = load_schema('encoded:schemas/ataqc_quality_metric.json')
