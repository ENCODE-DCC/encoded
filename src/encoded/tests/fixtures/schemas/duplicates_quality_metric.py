import pytest

@pytest.fixture
def duplicates_quality_metric(testapp, analysis_step_run_bam, file_bam_1_1, lab, award):
    item = {
        'step_run': analysis_step_run_bam['@id'],
        'quality_metric_of': [file_bam_1_1['@id']],
        'Percent Duplication': 0.23,
        'award': award['@id'],
        'lab': lab['@id']
    }

    return testapp.post_json('/duplicates_quality_metric', item).json['@graph'][0]
