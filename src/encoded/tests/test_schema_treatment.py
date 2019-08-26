import pytest


def test_treatment_patch_prod_source(testapp, treatment):
    testapp.patch_json(
        treatment['@id'],
        {
            'treatment_term_name': 'ethanol',
            'treatment_type': 'chemical'
        },
        status=200,
    )
def test_treatment_patch_amount_units(testapp, treatment):
    testapp.patch_json(
        treatment['@id'],
        {
            'treatment_type': 'injection',
            'amount': 20,
            'amount_units': 'mg/kg'
        },
        status=200,
    )