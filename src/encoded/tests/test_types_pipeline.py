import pytest


def test_analysis_step_name_calcprop(testapp, analysis_step):
    assert analysis_step['@id'] == '/analysis-steps/fastqc-step-v-1/'
    assert analysis_step['name'] == 'fastqc-step-v-1'
    assert analysis_step['major_version'] == 1

def test_analysis_step_version_name_calcprop(testapp, analysis_step, analysis_step_version):
    assert analysis_step_version['minor_version'] == 0
    assert analysis_step_version['name'] == 'fastqc-step-v-1-0'
    assert analysis_step_version['@id'] == '/analysis-step-versions/fastqc-step-v-1-0/'
