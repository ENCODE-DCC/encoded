import pytest
from pytest_bdd import scenarios

pytestmark = [
    pytest.mark.bdd,
    pytest.mark.usefixtures('index_workbook'),
]

scenarios(
    'cart_public.feature',
    strict_gherkin=False,
)
