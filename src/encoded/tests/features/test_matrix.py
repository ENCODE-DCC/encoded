""" These scenarios do not require the workbook fixture, but get it anyway.
"""
import pytest
from pytest_bdd import scenarios

pytestmark = [
    pytest.mark.bdd,
    pytest.mark.usefixtures('index_workbook'),
]

scenarios(
    'matrix_entex.feature',
    'matrix_experiment.feature',
    'matrix_reference_epigenome.feature',
    'matrix_chip_seq.feature',
    'matrix_mouse_development.feature',
    'matrix_reference_epigenome_homo_sapien_all.feature',
    'matrix_reference_epigenome_homo_sapien_nonroadmap.feature',
    'matrix_reference_epigenome_mus_musculus.feature',
    'matrix_sescc_stem_cell.feature',
    'matrix_encore.feature',
    strict_gherkin=False,
)
