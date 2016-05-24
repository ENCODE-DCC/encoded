import pytest
from pytest_bdd import scenarios

pytestmark = [
    pytest.mark.bdd,
    pytest.mark.usefixtures('workbook', 'submitter_user'),
]


scenarios(
    'user.feature',
)
