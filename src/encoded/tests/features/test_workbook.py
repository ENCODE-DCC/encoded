import pytest
from pytest_bdd import scenarios

pytestmark = [
    pytest.mark.bdd,
    pytest.mark.usefixtures('index_workbook'),
]

scenarios(
    'antibodies.feature',
    'biosamples.feature',
    'experiments.feature',
    'search.feature',
    'advanced_query_search.feature',
    'targets.feature',
    'no_at_type.feature',
    strict_gherkin=False,
)
