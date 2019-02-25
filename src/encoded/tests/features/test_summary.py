""" These scenarios do not require the workbook fixture, but get it anyway.
"""
import pytest
from pytest_bdd import scenarios

pytestmark = [
    pytest.mark.bdd,
    pytest.mark.usefixtures('workbook'),
]


def test_summaryview(testapp, workbook):
    res = testapp.get('/summary/?type=Experiment&status=released')
    assert res.json['summary']


scenarios(
    'summary.feature',
    strict_gherkin=False,
)
