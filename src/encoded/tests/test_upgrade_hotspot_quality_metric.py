import pytest


def test_upgrade_hotspot_quality_metric_8_9(upgrader, hotspot_quality_metric_8):
    value = upgrader.upgrade(
        'hotspot_quality_metric',
        hotspot_quality_metric_8,
        current_version='8',
        target_version='9',
    )
    assert value['schema_version'] == '9'
    assert 'SPOT1 score' not in value
    assert value['spot1_score'] == 0.5555
