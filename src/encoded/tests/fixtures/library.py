import pytest
from ..constants import *


@pytest.fixture
def library(testapp, lab, award, biosample_1):
    item = {
        'nucleic_acid_term_name': 'DNA',
        'lab': lab['@id'],
        'award': award['@id'],
        'biosample': biosample_1['@id'],
    }
    return testapp.post_json('/library', item).json['@graph'][0]

@pytest.fixture
def library_1(testapp, lab, award, base_biosample):
    item = {
        'award': award['uuid'],
        'lab': lab['uuid'],
        'nucleic_acid_term_name': 'DNA',
        'biosample': base_biosample['uuid']
    }
    return testapp.post_json('/library', item, status=201).json['@graph'][0]


@pytest.fixture
def library_2(testapp, lab, award, base_biosample):
    item = {
        'award': award['uuid'],
        'lab': lab['uuid'],
        'nucleic_acid_term_name': 'DNA',
        'biosample': base_biosample['uuid']
    }
    return testapp.post_json('/library', item, status=201).json['@graph'][0]

@pytest.fixture
def library_no_biosample(testapp, lab, award):
    item = {
        'nucleic_acid_term_name': 'DNA',
        'lab': lab['@id'],
        'award': award['@id']
    }
    return testapp.post_json('/library', item).json['@graph'][0]


@pytest.fixture
def base_library(testapp, lab, award, base_biosample):
    item = {
        'award': award['uuid'],
        'lab': lab['uuid'],
        'nucleic_acid_term_name': 'DNA',
        'biosample': base_biosample['uuid']
    }
    return testapp.post_json('/library', item, status=201).json['@graph'][0]

@pytest.fixture
def library_1(testapp, lab, award, base_biosample):
    item = {
        'award': award['uuid'],
        'lab': lab['uuid'],
        'nucleic_acid_term_name': 'DNA',
        'biosample': base_biosample['uuid']
    }
    return testapp.post_json('/library', item, status=201).json['@graph'][0]


@pytest.fixture
def library_2(testapp, lab, award, base_biosample):
    item = {
        'award': award['uuid'],
        'lab': lab['uuid'],
        'nucleic_acid_term_name': 'DNA',
        'biosample': base_biosample['uuid']
    }
    return testapp.post_json('/library', item, status=201).json['@graph'][0]

@pytest.fixture
def library_schema_9(lab, award):
    return {
        'award': award['uuid'],
        'lab': lab['uuid'],
        'extraction_method': 'Trizol (Invitrogen 15596-026)',
        'lysis_method': 'Possibly Trizol',
        'library_size_selection_method': 'Gel',
    }


@pytest.fixture
def library_schema_9b(lab, award):
    return {
        'award': award['uuid'],
        'lab': lab['uuid'],
        'extraction_method': 'see document ',
        'lysis_method': 'test',
    }


@pytest.fixture
def encode_lab(testapp):
    item = {
        'name': 'encode-processing-pipeline',
        'title': 'ENCODE Processing Pipeline',
        'status': 'current',
        'uuid': 'a558111b-4c50-4b2e-9de8-73fd8fd3a67d',
        }
    return testapp.post_json('/lab', item, status=201).json['@graph'][0]

