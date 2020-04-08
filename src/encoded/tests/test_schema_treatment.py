import pytest


def test_treatment_patch_prod_source(testapp, treatment_5):
    testapp.patch_json(
        treatment_5['@id'],
        {
            'treatment_term_name': 'ethanol',
            'treatment_type': 'chemical'
        },
        status=200,
    )
def test_treatment_patch_amount_units(testapp, treatment_5):
    testapp.patch_json(
        treatment_5['@id'],
        {
            'treatment_type': 'injection',
            'amount': 20,
            'amount_units': 'μg/kg'
        },
        status=200,
    )