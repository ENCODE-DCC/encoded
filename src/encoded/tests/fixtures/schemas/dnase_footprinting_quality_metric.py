import pytest


@pytest.fixture
def dnase_footprinting_quality_metric(
    testapp, analysis_step_run_dnase_encode4, GRCh38_file, award, lab
):
    item = {
        'step_run': analysis_step_run_dnase_encode4['@id'],
        'quality_metric_of': [GRCh38_file['@id']],
        'footprint_count': 1,
        'award': award['@id'],
        'lab': lab['@id']
    }

    return testapp.post_json(
        '/dnase_footprinting_quality_metric', item
    ).json['@graph'][0]
