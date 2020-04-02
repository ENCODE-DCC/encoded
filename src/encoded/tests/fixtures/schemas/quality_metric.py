import pytest


@pytest.fixture
def quality_metric_1(pipeline, analysis_step_run):
    return {
        'status': 'released',
        'pipeline': pipeline['uuid'],
        'step_run': analysis_step_run['uuid'],
        'schema_version': '1'
    }


@pytest.fixture
def gene_type_quantification_quality_metric_1(
    testapp,
    lab,
    award,
    analysis_step_run_bam,
    file_bam
):
    return {
        'award': award['uuid'],
        'lab': lab['uuid'],
        'quality_metric_of': [file_bam['@id']],
        'step_run': analysis_step_run_bam['@id'],
        'protein_coding': 602,
        'pseudogene': 981,
        'schema_version': '1'
    }
