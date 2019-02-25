""" These scenarios do not require the workbook fixture, but get it anyway.
"""
import pytest
from pytest_bdd import scenarios

pytestmark = [
    pytest.mark.bdd,
]

scenarios(
    'title.feature',
    'toolbar.feature',
    strict_gherkin=False
)
