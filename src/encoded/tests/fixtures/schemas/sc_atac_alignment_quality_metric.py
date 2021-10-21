import pytest


@pytest.fixture
def sc_atac_alignment_quality_metric_1(analysis_step_run, file, award, lab):
    return {
        'award': award['uuid'],
        'lab': lab['uuid'],
        'step_run': analysis_step_run['uuid'],
        'quality_metric_of': [file['uuid']],
        'pct_properly_paired_reads': 0.2,
        'pct_mapped_reads': 0.3,
        'pct_singletons': 0.4
    }
