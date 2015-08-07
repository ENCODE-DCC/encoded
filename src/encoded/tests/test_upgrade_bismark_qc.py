import pytest


@pytest.fixture
def bismark_qc_metric(quality_metric):
    return {
        'status': "finished",
        'pipeline': pipeline['uuid'],
    }

@pytest.fixture
def bismark_qc_metric_1(bismark_qc_metric):
    item = bismark_qc_metric.copy()
    item.update({
        "step_run": "/analysis-step-runs/1a2e2163-abf9-4770-bca5-33018969810f/"
        "assay_term_name": "whole-genome shotgun bisulfite sequencing",
        "applies_to": [ "fred", "ethyl", "ricky" ],
        'schema_version': '1'
    })
    return item


def test_bismark_qc_metric_upgrade_1(app, bismark_qc_metric_1):
    migrator = app.registry['migrator']
    value = migrator.upgrade('bismark_qc_metric', bismark_qc_metric_1, target_version='2')
    assert value.get('relates_to') is not None
    assert len(value['relates_to']) > 0
    assert value.get('applies_to') is None
