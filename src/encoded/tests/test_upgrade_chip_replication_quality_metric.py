import pytest


def test_upgrade_chip_replication_quality_metric_1_2(upgrader, chip_replication_quality_metric_1):
    value = upgrader.upgrade(
        "chip_replication_quality_metric",
        chip_replication_quality_metric_1,
        current_version="1",
        target_version="2",
    )
    assert value["schema_version"] == "2"
    assert value.get("idr_dispersion_plot") == "ENCFF002DSJ.raw.srt.filt.nodup.srt.filt.nodup.sample.15.SE.tagAlign.gz.cc.plot.pdf"
    assert 'IDR_dispersion_plot' not in value