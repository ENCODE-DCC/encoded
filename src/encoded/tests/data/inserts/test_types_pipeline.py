import pytest

def test_analysis_step_version_name_calcprop(testapp, analysis_step_version):
    assert analysis_step_version['minor_version'] == 0
    assert analysis_step_version['name'] == 'fastqc-step-v-1-0'
    assert analysis_step_version['@id'] == '/analysis-step-versions/fastqc-step-v-1-0/'
