import pytest


@pytest.mark.parametrize('qc_type, old_version, new_version', [
    ('bismark_quality_metric', '8', '9'),
    ('chipseq_filter_quality_metric', '7', '8'),
    ('complexity_xcorr_quality_metric', '7', '8'),
    ('correlation_quality_metric', '7', '8'),
    ('cpg_correlation_quality_metric', '7', '8'),
    ('duplicates_quality_metric', '6', '7'),
    ('edwbamstats_quality_metric', '7', '8'),
    ('filtering_quality_metric', '7', '8'),
    ('gencode_category_quality_metric', '1', '2'),
    ('generic_quality_metric', '7', '8'),
    ('histone_chipseq_quality_metric', '1', '2'),
    ('hotspot_quality_metric', '7', '8'),
    ('idr_quality_metric', '6', '7'),
    ('idr_summary_quality_metric', '7', '8'),
    ('long_read_rna_mapping_quality_metric', '1', '2'),
    ('long_read_rna_quantification_quality_metric', '1', '2'),
    ('mad_quality_metric', '6', '7'),
    ('micro_rna_mapping_quality_metric', '1', '2'),
    ('micro_rna_quantification_quality_metric', '1', '2'),
    ('samtools_flagstats_quality_metric', '7', '8'),
    ('samtools_stats_quality_metric', '7', '8'),
    ('star_quality_metric', '7', '8'),
    ('trimming_quality_metric', '7', '8')
])
def test_upgrade_snATAC_name(upgrader, quality_metric_1, qc_type, old_version, new_version):
    quality_metric_1['schema_version'] = old_version
    quality_metric_1['assay_term_name'] = 'single-nuclei ATAC-seq'
    value = upgrader.upgrade(qc_type, quality_metric_1, current_version=old_version, target_version=new_version)
    assert value['assay_term_name'] == 'single-nucleus ATAC-seq'
    assert value['schema_version'] == new_version
    value['assay_term_name'] = 'HiC'
    value = upgrader.upgrade(qc_type, quality_metric_1, current_version=old_version, target_version=new_version)
    assert value['assay_term_name'] != 'single-nucleus ATAC-seq'
