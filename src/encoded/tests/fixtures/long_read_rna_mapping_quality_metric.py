import pytest
from ..constants import *


@pytest.fixture
def long_read_rna_quantification_quality_metric_1_2(testapp, analysis_step_run_bam, file_tsv_1_2, award, lab):
    item = {
        'step_run': analysis_step_run_bam['@id'],
        'quality_metric_of': [file_tsv_1_2['@id']],
        'genes_detected': 5000,
        'award': award['@id'],
        'lab': lab['@id']
    }
    return testapp.post_json('/long_read_rna_quantification_quality_metric', item).json['@graph'][0]


@pytest.fixture
def long_read_rna_mapping_quality_metric_2_1(
    testapp,
    analysis_step_run_bam,
    file_bam_2_1,
    award,
    lab
):
    item = {
        'step_run': analysis_step_run_bam['@id'],
        'quality_metric_of': [file_bam_2_1['@id']],
        'full_length_non_chimeric_read_count': 500000,
        'mapping_rate': 0.5,
        'award': award['@id'],
        'lab': lab['@id']
    }
    return testapp.post_json('/long_read_rna_mapping_quality_metric', item).json['@graph'][0]

