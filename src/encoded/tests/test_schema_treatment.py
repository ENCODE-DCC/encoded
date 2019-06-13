import pytest

@pytest.fixture
def test_treatment_with_bad_prod (testapp,treatment, source):
    item = {
        "treatment_term_name": treatment['treatment_term_name'],
        "treatment_type": treatment['treatment_type'],
        "product_id": " Abcam",
        "source": source['@id']
    }
    return item

def test_treatment_prod_source_id (testapp, test_treatment_with_bad_prod):
    testapp.post_json('/treatment', test_treatment_with_bad_prod, status=422)
    test_treatment_with_bad_prod["product_id"] = "Illumina"
    testapp.post_json('/treatment', test_treatment_with_bad_prod, status=201)