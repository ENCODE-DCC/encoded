import pytest


def test_star_quality_metric_upgrade(registry, star_quality_metric_0,
                                     bam_file, lab, award):
    from snovault import UPGRADER
    upgrader = registry[UPGRADER]
    value = upgrader.upgrade('star_quality_metric',
                             star_quality_metric_0, registry=registry,
                             current_version='2', target_version='3')
    assert value['lab'] == lab['@id'] and value['award'] == award['@id']
