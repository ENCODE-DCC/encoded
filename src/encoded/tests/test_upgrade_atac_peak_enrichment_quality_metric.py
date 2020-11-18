

def test_upgrade_atac_peak_enrichment_quality_metric_1_2(
    upgrader, atac_peak_enrichment_quality_metric_1
):
    value = upgrader.upgrade(
        'atac_peak_enrichment_quality_metric',
        atac_peak_enrichment_quality_metric_1,
        current_version='1',
        target_version='2',
    )
    assert value['schema_version'] == '2'
    assert 'fri_blacklist'not in value
    assert 'fri_dhs'not in value
    assert 'fri_enh'not in value
    assert 'fri_prom'not in value
    assert value['notes'] == '{"fri_blacklist": 0.0013046877081284722, "fri_dhs": 0.5850612112943434, "fri_enh": 0.37244791482996753, "fri_prom": 0.21434770162962138}'
