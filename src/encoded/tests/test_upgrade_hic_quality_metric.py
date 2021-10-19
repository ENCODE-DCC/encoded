import pytest


def test_hic_quality_metric_1_2(
    upgrader, hic_quality_metric_paired_ended_2
):
    value = upgrader.upgrade('hic_quality_metric', hic_quality_metric_paired_ended_2, current_version='1', target_version='2')
    assert value['run_type'] == 'paired-ended'
    value = upgrader.upgrade('hic_quality_metric', hic_quality_metric_paired_ended_2, current_version='1', target_version='2')
    assert 'chimeric_ambiguous' not in value
    assert '3_or_more_alignments' in value
