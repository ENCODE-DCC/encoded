import pytest

@pytest.fixture
def chip_peak_enrichment_quality_metric_1(award, lab):
    return{
        "step_run": "63b1b347-f008-4103-8d20-0e12f54d1882",
        "award": award["uuid"],
        "lab": lab["uuid"],
        "quality_metric_of": ["ENCFF003COS"],
        "FRiP":  0.253147998729
    }

def test_upgrade_chip_peak_enrichment_quality_metric_1_2(upgrader, chip_peak_enrichment_quality_metric_1):
    value = upgrader.upgrade(
        "chip_peak_enrichment_quality_metric",
        chip_peak_enrichment_quality_metric_1,
        current_version="1",
        target_version="2",
    )
    assert value["schema_version"] == "2"
    assert value.get("frip") == 0.253147998729
    assert 'FRiP' not in value
