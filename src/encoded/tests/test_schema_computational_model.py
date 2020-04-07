import pytest


def test_unique_software(testapp, computational_model_unique_software):
    #import pdb; pdb.set_trace()
    res = testapp.post_json('/computational_model', computational_model_unique_software, expect_errors=True)
    assert res.status_code == 201

def test_non_unique_software(testapp, computational_model_non_unique_software):
    #import pdb; pdb.set_trace()
    res = testapp.post_json('/computational_model',computational_model_non_unique_software, expect_errors=True)
    assert res.status_code == 422
