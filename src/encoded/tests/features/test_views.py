""" These scenarios do not require the workbook fixture, but get it anyway.
"""
import pytest
from pytest_bdd import scenarios

pytestmark = [
    pytest.mark.bdd,
    pytest.mark.usefixtures('workbook'),
]


def test_newsview(testapp, workbook):
    res = testapp.get('/news/')
    assert res.json['@graph']


scenarios(
    'views.feature',
    strict_gherkin=False,
)
