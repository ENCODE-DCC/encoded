import pytest


def test_tarball_attachment(testapp, generic_quality_metric):
    # Make sure *.tar files are accepted by the attachment property
    res = testapp.post_json('/generic_quality_metric', generic_quality_metric, expect_errors=False)
    assert res.status_code == 201


def test_json_attachment(testapp, generic_json_quality_metric):
    res = testapp.post_json(
        '/generic_quality_metric',
        generic_json_quality_metric,
        expect_errors=False
    )
    assert res.status_code == 201
