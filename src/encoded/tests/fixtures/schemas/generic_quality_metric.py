import pytest
from ...constants import TAR_BALL


@pytest.fixture
def generic_quality_metric(analysis_step_run, file, award, lab):
    return {
        'award': award['uuid'],
        'lab': lab['uuid'],
        'name': 'Generic QC',
        'step_run': analysis_step_run['uuid'],
        'quality_metric_of': [file['uuid']],
        'attachment': {
            'download': 'test.tgz',
            'type': 'application/x-tar',
            'href': TAR_BALL
        }
    }
