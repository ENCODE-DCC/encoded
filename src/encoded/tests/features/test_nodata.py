import pytest
from pytest_bdd import scenarios

pytestmark = [
    pytest.mark.bdd,
]

scenarios(
    'title.feature',
    'toolbar.feature',
)
