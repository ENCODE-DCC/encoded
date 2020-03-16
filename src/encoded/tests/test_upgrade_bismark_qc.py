import pytest


def test_bismark_quality_metric_upgrade_1(registry, bismark_quality_metric_1, bigbed):
    from snovault import UPGRADER
    upgrader = registry[UPGRADER]
    value = upgrader.upgrade('bismark_quality_metric',
                             bismark_quality_metric_1, registry=registry,
                             current_version='1', target_version='2')
    assert value['quality_metric_of'] == [bigbed['uuid']]


def test_bismark_quality_metric_upgrade_2(registry, bismark_quality_metric_2, bigbed, lab, award):
    from snovault import UPGRADER
    upgrader = registry[UPGRADER]
    value = upgrader.upgrade('bismark_quality_metric',
                             bismark_quality_metric_2, registry=registry,
                             current_version='3', target_version='4')
    assert value['lab'] == lab['@id'] and value['award'] == award['@id']
