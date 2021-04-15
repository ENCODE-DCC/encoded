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
    schema = load_schema('encoded:schemas/quality_metric.json')
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

    @calculated_property(schema={
        "title": "Read depth",
        "type": "number",
        "description": "Sum of the uniquely mapped reads number and the number of reads mapped to multiple loci.",
        "comment": "Do not submit. The value is extracted from values reported in the STAR quality metric.",
        "notSubmittable": True,
    })
    def read_depth(self, properties=None):
        if properties is None:
            properties = self.upgrade_properties()
        if 'Uniquely mapped reads number' in properties and \
                'Number of reads mapped to multiple loci' in properties:
            unique = properties['Uniquely mapped reads number']
            multi = properties['Number of reads mapped to multiple loci']
            return unique + multi


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

    @calculated_property(schema={
        "title": "FRiP score from optimal peaks",
        "type": "number",
        "description": "Fraction reads in IDR peaks (FRiP) from optimal peaks",
        "comment": "Do not submit. The value is extracted from submitted FRiP scores.",
        "notSubmittable": True,
    })
    def frip(self, request, Fp=None, Ft=None, Np=None, Nt=None):
        if Np is None:
            return Ft
        if Nt is None:
            return Fp
        if Nt >= Np:
            return Ft
        return Fp


@collection(
    name='histone-chipseq-quality-metrics',
    properties={
        'title': "Histone ChIP-seq Quality Metrics",
        'description': "Quality metrics from histone ChIP-seq peak overlap analysis",
    })
class HistoneChipSeqQualityMetric(QualityMetric, CalculatedAssayTermID):
    item_type = 'histone_chipseq_quality_metric'
    schema = load_schema('encoded:schemas/histone_chipseq_quality_metric.json')

    @calculated_property(schema={
        "title": "Best FRiP score",
        "type": "number",
        "description": "Best fraction reads in peaks (FRiP) from peaks",
        "comment": "Do not submit. The value is extracted from submitted FRiP scores.",
        "notSubmittable": True,
    })
    def frip(self, request, Fp=None, Ft=None, F1=None, F2=None):
        frips = [
            f
            for f in [Fp, Ft, F1, F2]
            if f is not None
        ]
        if frips:
            return max(frips)


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
    name='chip-alignment-quality-metrics',
    properties={
        'title': "ChIP-seq Alignment Quality Metric",
    })
class ChipAlignmentQualityMetric(QualityMetric, CalculatedAssayTermID):
    item_type = 'chip_alignment_samstat_quality_metric'
    schema = load_schema('encoded:schemas/chip_alignment_samstat_quality_metric.json')


@collection(
    name='chip-alignment-enrichment-quality-metrics',
    properties={
        'title': "ChIP-seq Alignment Enrichment Quality Metric",
    })
class ChipAlignmentEnrichmentQualityMetric(QualityMetric, CalculatedAssayTermID):
    item_type = 'chip_alignment_enrichment_quality_metric'
    schema = load_schema('encoded:schemas/chip_alignment_enrichment_quality_metric.json')


@collection(
    name='chip-library-quality-metrics',
    properties={
        'title': "ChIP-seq Library Metrics",
    })
class ChipLibraryQualityMetric(QualityMetric, CalculatedAssayTermID):
    item_type = 'chip_library_quality_metric'
    schema = load_schema('encoded:schemas/chip_library_quality_metric.json')


@collection(
    name='chip-peak-enrichment-quality-metrics',
    properties={
        'title': "ChIP-seq Peak Enrichment Quality Metric",
    })
class ChipPeakEnrichmentQualityMetric(QualityMetric, CalculatedAssayTermID):
    item_type = 'chip_peak_enrichment_quality_metric'
    schema = load_schema('encoded:schemas/chip_peak_enrichment_quality_metric.json')


@collection(
    name='chip-replication-quality-metrics',
    properties={
        'title': "ChIP-seq Replication Quality Metric",
    })
class ChipReplicationQualityMetric(QualityMetric, CalculatedAssayTermID):
    item_type = 'chip_replication_quality_metric'
    schema = load_schema('encoded:schemas/chip_replication_quality_metric.json')


@collection(
    name='atac-alignment-quality-metrics',
    properties={
        'title': "ATAC-seq Alignment Quality Metrics",
    })
class AtacAlignmentQualityMetric(QualityMetric, CalculatedAssayTermID):
    item_type = 'atac_alignment_quality_metric'
    schema = load_schema('encoded:schemas/atac_alignment_quality_metric.json')


@collection(
    name='atac-alignment-enrichment-quality-metrics',
    properties={
        'title': "ATAC-seq Alignment Enrichment Quality Metrics",
    })
class AtacAlignmentEnrichmentQualityMetric(QualityMetric, CalculatedAssayTermID):
    item_type = 'atac_alignment_enrichment_quality_metric'
    schema = load_schema('encoded:schemas/atac_alignment_enrichment_quality_metric.json')


@collection(
    name='atac-library-quality-metrics',
    properties={
        'title': "ATAC-seq Library Metrics",
    })
class AtacLibraryQualityMetric(QualityMetric, CalculatedAssayTermID):
    item_type = 'atac_library_complexity_quality_metric'
    schema = load_schema('encoded:schemas/atac_library_complexity_quality_metric.json')


@collection(
    name='atac-peak-enrichment-quality-metrics',
    properties={
        'title': "ATAC-seq Peak Enrichment Quality Metrics",
    })
class AtacPeakEnrichmentQualityMetric(QualityMetric, CalculatedAssayTermID):
    item_type = 'atac_peak_enrichment_quality_metric'
    schema = load_schema('encoded:schemas/atac_peak_enrichment_quality_metric.json')


@collection(
    name='atac-replication-quality-metrics',
    properties={
        'title': "ATAC-seq Replication Quality Metrics",
    })
class AtacReplicationQualityMetric(QualityMetric, CalculatedAssayTermID):
    item_type = 'atac_replication_quality_metric'
    schema = load_schema('encoded:schemas/atac_replication_quality_metric.json')


@collection(
    name='gene-quantification-quality-metrics',
    properties={
        'title': "RNA-seq Gene Quantification Quality Metric",
    })
class GeneQuantificationQualityMetric(QualityMetric, CalculatedAssayTermID):
    item_type = 'gene_quantification_quality_metric'
    schema = load_schema('encoded:schemas/gene_quantification_quality_metric.json')


@collection(
    name='gene-type-quantification-quality-metrics',
    properties={
        'title': "RNA-seq Gene Type Quantification Quality Metric",
    })
class GeneTypeQuantificationQualityMetric(QualityMetric, CalculatedAssayTermID):
    item_type = 'gene_type_quantification_quality_metric'
    schema = load_schema('encoded:schemas/gene_type_quantification_quality_metric.json')


@collection(
    name='dnase-alignment-quality-metrics',
    properties={
        'title': "DNase Alignment Quality Metrics",
    })
class DnaseAlignmentQualityMetric(QualityMetric, CalculatedAssayTermID):
    item_type = 'dnase_alignment_quality_metric'
    schema = load_schema('encoded:schemas/dnase_alignment_quality_metric.json')


@collection(
    name='dnase-footprinting-quality-metrics',
    properties={
        'title': "DNase Footprinting Quality Metrics",
    })
class DnaseFootprintingQualityMetric(QualityMetric, CalculatedAssayTermID):
    item_type = 'dnase_footprinting_quality_metric'
    schema = load_schema('encoded:schemas/dnase_footprinting_quality_metric.json')


@collection(
    name='gembs-alignment-quality-metrics',
    properties={
        'title': "gemBS Alignment Quality Metrics",
    })
class GembsAlignmentQualityMetric(QualityMetric, CalculatedAssayTermID):
    item_type = 'gembs_alignment_quality_metric'
    schema = load_schema('encoded:schemas/gembs_alignment_quality_metric.json')


@collection(
    name='chia-pet-alignment-quality-metrics',
    properties={
        'title': "ChIA-PET Alignment Quality Metrics",
    })
class ChiaPetAlignmentQualityMetric(QualityMetric, CalculatedAssayTermID):
    item_type = 'chia_pet_alignment_quality_metric'
    schema = load_schema('encoded:schemas/chia_pet_alignment_quality_metric.json')


@collection(
    name='chia-pet-chr-interactions-quality-metrics',
    properties={
        'title': "ChIA-PET Chromatin Interactions Quality Metrics",
    })
class ChiaPetChrInteractionsQualityMetric(QualityMetric, CalculatedAssayTermID):
    item_type = 'chia_pet_chr_interactions_quality_metric'
    schema = load_schema('encoded:schemas/chia_pet_chr_interactions_quality_metric.json')


@collection(
    name='chia-pet-peak-enrichment-quality-metrics',
    properties={
        'title': "ChIA-PET Peak Enrichment Quality Metrics",
    })
class ChiaPetPeakEnrichmentQualityMetric(QualityMetric, CalculatedAssayTermID):
    item_type = 'chia_pet_peak_enrichment_quality_metric'
    schema = load_schema('encoded:schemas/chia_pet_peak_enrichment_quality_metric.json')
