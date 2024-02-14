import pytest


def test_gene_upgrade_remove_go_annotations(
    upgrader,
    gene_1,
):
    new_gene = upgrader.upgrade(
        'gene', gene_1, current_version='1', target_version='2'
    )
    assert new_gene['schema_version'] == '2'
    assert 'go_annotations' not in new_gene

def test_gene_upgrade_remove_go_annotations(
    upgrader,
    gene_2,
):
    new_gene = upgrader.upgrade(
        'gene', gene_2, current_version='2', target_version='3'
    )
    assert new_gene['schema_version'] == '3'
    assert 'locations' not in new_gene
