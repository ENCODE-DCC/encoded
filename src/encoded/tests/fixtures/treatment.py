import pytest
from ..constants import *


@pytest.fixture
def treatment(testapp, organism):
    item = {
        'treatment_term_name': 'ethanol',
        'treatment_type': 'chemical'
    }
    return testapp.post_json('/treatment', item).json['@graph'][0]

@pytest.fixture
def treatment_1():
    return {
        'treatment_type': 'chemical',
        'treatment_term_name': 'estradiol',
        'treatment_term_id': 'CHEBI:23965'
    }

@pytest.fixture
def submitter_treatment(submitter, lab):
    return {
        'treatment_type': 'chemical',
        'treatment_term_name': 'estradiol',
        'treatment_term_id': 'CHEBI:23965',
        'submitted_by': submitter['@id']
    }

