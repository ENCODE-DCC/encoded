import pytest

@pytest.fixture 
def chip_replication_quality_metric_1(award, lab):
    return{
        "step_run": "63b1b347-f008-4103-8d20-0e12f54d1882",
        "award": award["uuid"],
        "lab": lab["uuid"],
        "quality_metric_of": ["ENCFF003COS"],
        "IDR_dispersion_plot": "ENCFF002DSJ.raw.srt.filt.nodup.srt.filt.nodup.sample.15.SE.tagAlign.gz.cc.plot.pdf"
    }

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