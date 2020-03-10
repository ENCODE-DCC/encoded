import pytest
from ..constants import *


@pytest.fixture
def replicate(testapp, experiment, library):
    item = {
        'experiment': experiment['@id'],
        'library': library['@id'],
        'biological_replicate_number': 1,
        'technical_replicate_number': 1,
    }
    return testapp.post_json('/replicate', item).json['@graph'][0]


@pytest.fixture
def replicate_dnase(testapp, experiment_dnase, library_1):
    item = {
        'experiment': experiment_dnase['@id'],
        'library': library_1['@id'],
        'biological_replicate_number': 1,
        'technical_replicate_number': 1,
    }
    return testapp.post_json('/replicate', item).json['@graph'][0]


@pytest.fixture
def replicate_rna(testapp, experiment_rna, library_2):
    item = {
        'experiment': experiment_rna['@id'],
        'library': library_2['@id'],
        'biological_replicate_number': 1,
        'technical_replicate_number': 1,
    }
    return testapp.post_json('/replicate', item).json['@graph'][0]

@pytest.fixture
def replicate_1_1(testapp, base_experiment):
    item = {
        'biological_replicate_number': 1,
        'technical_replicate_number': 1,
        'experiment': base_experiment['@id'],
    }
    return testapp.post_json('/replicate', item, status=201).json['@graph'][0]


@pytest.fixture
def replicate_1_2(testapp, base_experiment):
    item = {
        'biological_replicate_number': 1,
        'technical_replicate_number': 2,
        'experiment': base_experiment['@id'],
    }
    return testapp.post_json('/replicate', item, status=201).json['@graph'][0]


@pytest.fixture
def replicate_2_1(testapp, base_experiment):
    item = {
        'biological_replicate_number': 2,
        'technical_replicate_number': 1,
        'experiment': base_experiment['@id'],
    }
    return testapp.post_json('/replicate', item, status=201).json['@graph'][0]


@pytest.fixture
def base_replicate(testapp, base_experiment):
    item = {
        'biological_replicate_number': 1,
        'technical_replicate_number': 1,
        'experiment': base_experiment['@id'],
    }
    return testapp.post_json('/replicate', item, status=201).json['@graph'][0]


@pytest.fixture
def base_replicate_two(testapp, base_experiment):
    item = {
        'biological_replicate_number': 1,
        'technical_replicate_number': 2,
        'experiment': base_experiment['@id'],
    }
    return testapp.post_json('/replicate', item, status=201).json['@graph'][0]

@pytest.fixture
def IgG_ctrl_rep(testapp, ctrl_experiment, IgG_antibody):
    item = {
        'experiment': ctrl_experiment['@id'],
        'biological_replicate_number': 1,
        'technical_replicate_number': 1,
        'antibody': IgG_antibody['@id'],
        'status': 'released'
    }
    return testapp.post_json('/replicate', item, status=201).json['@graph'][0]

@pytest.fixture
def replicate_1_1(testapp, base_experiment):
    item = {
        'biological_replicate_number': 1,
        'technical_replicate_number': 1,
        'experiment': base_experiment['@id'],
    }
    return testapp.post_json('/replicate', item, status=201).json['@graph'][0]


@pytest.fixture
def replicate_2_1(testapp, base_experiment):
    item = {
        'biological_replicate_number': 2,
        'technical_replicate_number': 1,
        'experiment': base_experiment['@id'],
    }
    return testapp.post_json('/replicate', item, status=201).json['@graph'][0]


@pytest.fixture
def replicate_1_2(testapp, base_experiment):
    item = {
        'biological_replicate_number': 1,
        'technical_replicate_number': 2,
        'experiment': base_experiment['@id'],
    }
    return testapp.post_json('/replicate', item, status=201).json['@graph'][0]

@pytest.fixture
def rep1_1(experiment, testapp):
    item = {
        'experiment': experiment['uuid'],
        'biological_replicate_number': 5,
        'technical_replicate_number': 4,
        'status': 'released'
    }
    return testapp.post_json('/replicate', item, status=201).json['@graph'][0]

@pytest.fixture
def replicate_RRBS_1(testapp, reference_experiment_RRBS_1, library_2):
    item = {
        'experiment': reference_experiment_RRBS_1['@id'],
        'library': library_2['@id'],
        'biological_replicate_number': 1,
        'technical_replicate_number': 1,
    }
    return testapp.post_json('/replicate', item).json['@graph'][0]


@pytest.fixture
def replicate_RNA_seq_1(testapp, reference_experiment_RNA_seq_1, library_1):
    item = {
        'experiment': reference_experiment_RNA_seq_1['@id'],
        'library': library_1['@id'],
        'biological_replicate_number': 1,
        'technical_replicate_number': 1,
    }
    return testapp.post_json('/replicate', item).json['@graph'][0]


@pytest.fixture
def file_rep(replicate, file_exp, testapp):
    item = {
        'experiment': file_exp['uuid'],
        'biological_replicate_number': 1,
        'technical_replicate_number': 1
    }
    return testapp.post_json('/replicate', item, status=201).json['@graph'][0]


@pytest.fixture
def file_rep2(replicate, file_exp2, testapp):
    item = {
        'experiment': file_exp2['uuid'],
        'biological_replicate_number': 1,
        'technical_replicate_number': 1
    }
    return testapp.post_json('/replicate', item, status=201).json['@graph'][0]


@pytest.fixture
def file_rep1_2(replicate, file_exp, testapp):
    item = {
        'experiment': file_exp['uuid'],
        'biological_replicate_number': 2,
        'technical_replicate_number': 1
    }
    return testapp.post_json('/replicate', item, status=201).json['@graph'][0]

@pytest.fixture
def replicate2(experiment):
    return {
        'experiment': experiment['uuid'],
        'biological_replicate_number': 1,
        'technical_replicate_number': 1,
    }


@pytest.fixture
def replicate_rbns(replicate2):
    item = replicate2.copy()
    item.update({
        'rbns_protein_concentration': 10,
        'rbns_protein_concentration_units': 'nM',
    })
    return item


@pytest.fixture
def replicate_rbns_no_units(replicate2):
    item = replicate2.copy()
    item.update({
        'rbns_protein_concentration': 10,
    })
    return item