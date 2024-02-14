def test_upgrade_atac_alignment_enrichment_quality_metric_1_2(
    upgrader, atac_alignment_enrichment_quality_metric_1
):
    value = upgrader.upgrade(
        'atac_alignment_enrichment_quality_metric',
        atac_alignment_enrichment_quality_metric_1,
        current_version='1',
        target_version='2',
    )
    assert value['schema_version'] == '2'
    assert 'fri_blacklist' not in value
    assert value['fri_exclusion_list'] == 0.0013046877081284722

