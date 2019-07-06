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
