import pytest


def test_sc_atac_library_complexity_quality_metric_1_2(upgrader, sc_atac_library_complexity_quality_metric_1):
    value = upgrader.upgrade('sc_atac_library_complexity_quality_metric', sc_atac_library_complexity_quality_metric_1, current_version='1', target_version='2')
    assert 'pct_duplicate_reads' not in value
    assert 'frac_duplicate_reads' in value
