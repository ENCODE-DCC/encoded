import pytest


def test_genetic_modification_upgrade_1_2(upgrader, gene_type_quantification_quality_metric_1):
    value = upgrader.upgrade('gene_type_quantification_quality_metric', gene_type_quantification_quality_metric_1,
                             current_version='1', target_version='2')
    assert value['schema_version'] == '2'
    assert 'protein_coding' in value
    assert 'pseudogene' not in value
