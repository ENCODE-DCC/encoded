import pytest


def test_sc_atac_alignment_quality_metric_1_2(
    upgrader, sc_atac_alignment_quality_metric_1
):
    value = upgrader.upgrade('sc_atac_alignment_quality_metric', sc_atac_alignment_quality_metric_1, current_version='1', target_version='2')
    assert 'pct_properly_paired_reads' not in value
    assert 'frac_properly_paired_reads' in value
    value = upgrader.upgrade('sc_atac_alignment_quality_metric', sc_atac_alignment_quality_metric_1, current_version='1', target_version='2')
    assert 'pct_mapped_reads' not in value
    assert 'frac_mapped_reads' in value
    value = upgrader.upgrade('sc_atac_alignment_quality_metric', sc_atac_alignment_quality_metric_1, current_version='1', target_version='2')
    assert 'pct_singletons' not in value
    assert 'frac_singletons' in value
