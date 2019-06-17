import pytest

@pytest.fixture
def test_treatment_patch_prod_source(testapp, treatment):
    treatment["product_id"] = "HT-904"
    treatment["source"] = "sigma"
    testapp.patch_json('/treatment', test_treatment_patch_prod_source, status=200)