def test_analysis_step_run_qc_metrics(testapp, quality_metric):
    step_run = testapp.get(quality_metric['step_run'] + '@@object').json
    assert quality_metric['@id'] in step_run['qc_metrics']
