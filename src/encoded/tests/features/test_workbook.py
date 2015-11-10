import pytest
from pytest_bdd import scenarios

pytestmark = [
    pytest.mark.bdd,
    pytest.mark.usefixtures('workbook'),
]

scenarios(
    'antibodies.feature',
    'biosamples.feature',
    'experiments.feature',
    'search.feature',
    'targets.feature',
)
