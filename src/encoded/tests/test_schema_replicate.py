import pytest


def test_replicate_rbns_post(testapp, replicate_rbns):
    testapp.post_json('/replicate', replicate_rbns)


def test_replicate_rbns_unit_requirement(testapp, replicate_rbns_no_units):
    testapp.post_json('/replicate', replicate_rbns_no_units, status=422)
