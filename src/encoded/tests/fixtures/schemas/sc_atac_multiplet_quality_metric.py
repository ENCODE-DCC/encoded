import pytest
from ...constants import TSV_GZ


@pytest.fixture
def sc_atac_multiplet_quality_metric(analysis_step_run, file, award, lab):
    return {
        'award': award['uuid'],
        'lab': lab['uuid'],
        'step_run': analysis_step_run['uuid'],
        'quality_metric_of': [file['uuid']],
        'barcode_pairs_expanded': {
            'download': 'test.tsv.gz',
            'type': 'application/x-gzip',
            'href': TSV_GZ
        }
    }
