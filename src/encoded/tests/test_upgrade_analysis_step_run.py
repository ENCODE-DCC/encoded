import pytest


def test_analysis_step_run_3_4(registry, upgrader, analysis_step_run_3):
    value = upgrader.upgrade('analysis_step_run', analysis_step_run_3,
                             current_version='3', target_version='4', registry=registry)
    assert value['schema_version'] == '4'
    assert value['status'] == 'released'


def test_analysis_step_run_4_5(registry, upgrader, analysis_step_run_4):
    assert analysis_step_run_4['status'] == 'virtual'
    value = upgrader.upgrade('analysis_step_run', analysis_step_run_4,
                             current_version='4', target_version='5', registry=registry)
    assert value['schema_version'] == '5'
    assert value['status'] == 'released'
