import pytest
from pytest_bdd import scenarios

pytestmark = [
    pytest.mark.bdd,
    pytest.mark.usefixtures('index_workbook', 'submitter_user'),
]


scenarios(
    'user.feature',
    strict_gherkin=False,
)
