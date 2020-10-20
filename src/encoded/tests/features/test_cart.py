""" These scenarios do not require the workbook fixture, but get it anyway.
"""
import pytest
from pytest_bdd import scenarios

pytestmark = [
    pytest.mark.bdd,
    pytest.mark.usefixtures('index_workbook'),
]

scenarios(
    'cart.feature',
    strict_gherkin=False,
)
