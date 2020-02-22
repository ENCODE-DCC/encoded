""" These scenarios do not require the workbook fixture, but get it anyway.
"""
import pytest
from pytest_bdd import scenarios

pytestmark = [
    pytest.mark.bdd,
    pytest.mark.usefixtures('workbook'),
]

scenarios(
    'matrix_entex.feature',
    'matrix_experiment.feature',
    'matrix_reference_epigenome.feature',
    'matrix_chip_seq.feature'
)
