import pytest


def test_hic_qc_single_ended_dependencies(testapp, hic_quality_metric_single_ended_1):
    testapp.post_json('/hic_quality_metric', hic_quality_metric_single_ended_1)


def test_hic_qc_paired_ended_dependencies(testapp, hic_quality_metric_paired_ended_1):
    testapp.post_json('/hic_quality_metric', hic_quality_metric_paired_ended_1)
