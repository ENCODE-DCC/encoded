""" These scenarios do not require the workbook fixture, but get it anyway.
"""
import pytest
from pytest_bdd import scenarios

pytestmark = [
    pytest.mark.bdd,
    pytest.mark.usefixtures('workbook'),
]


def test_auditview(testapp, workbook):
    res = testapp.get('/audit/?type=Experiment')
    assert res.json['matrix']


scenarios(
    'audit.feature',
    strict_gherkin=False,
)
