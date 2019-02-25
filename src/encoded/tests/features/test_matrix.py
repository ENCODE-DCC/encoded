""" These scenarios do not require the workbook fixture, but get it anyway.
"""
import pytest
from pytest_bdd import scenarios

pytestmark = [
    pytest.mark.bdd,
    pytest.mark.usefixtures('workbook'),
]


@pytest.mark.parametrize('url', [
    '/matrix/?type=Experiment&status=released',
    '/matrix/?type=Annotation&encyclopedia_version=4',
])
def test_matrixview(testapp, workbook, url):
    res = testapp.get(url)
    assert res.json['matrix']


scenarios(
    'matrix_entex.feature',
    'matrix_experiment.feature',
    'matrix_reference_epigenome.feature'
    'matrix.feature',
    strict_gherkin=False,
)
