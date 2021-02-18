import pytest


def test_admin_allowed_add_analysis_step_run(testapp, analysis_step_run_with_no_status):
    testapp.post_json('/analysis-step-runs/', analysis_step_run_with_no_status, status=201)


def test_submitter_allowed_add_analysis_step_run(submitter_testapp, analysis_step_run_with_no_status):
    submitter_testapp.post_json('/analysis-step-runs/', analysis_step_run_with_no_status, status=201)