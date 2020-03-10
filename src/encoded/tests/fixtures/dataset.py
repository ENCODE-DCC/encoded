import pytest
from ..constants import *


@pytest.fixture
def dataset_reference_1(lab, award):
    return {
        'award': award['uuid'],
        'lab': lab['uuid'],
        'dbxrefs': ['UCSC-ENCODE-hg19:wgEncodeEH000325', 'IHEC:IHECRE00004703'],
    }


@pytest.fixture
def dataset_reference_2(lab, award):
    return {
        'award': award['uuid'],
        'lab': lab['uuid'],
        'dbxrefs': ['IHEC:IHECRE00004703'],
        'notes': 'preexisting comment.'
    }
