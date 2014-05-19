import pytest


@pytest.fixture
def chip_experiment(submitter, lab, award):
    return {
        'award': award['uuid'],
        'biosample_term_name': 'NTR:0000022',
        'biosample_term_name': 'myocyte',
        'biosample_type': 'in vitro differentiated cells',
        'lab': lab['uuid'],
        'submitted_by': submitter['uuid'],
        'assay_term_name': 'ChIP-seq',
        'assay_term_id': "OBI:0000716",
    }

@pytest.fixture
def base_experiment(lab, award):
    return {
        'award': award['uuid'],
        'biosample_term_name': 'UBERON:349829',
        'biosample_term_name': "liver",
        'biosample_type': 'tissue',
        'lab': lab['uuid'],
        'assay_term_name': 'ChIP-seq',
        'assay_term_id': "OBI:0000716",
        'aliases': ['encode:base-experiment']
    }


@pytest.fixture
def base_library(lab, award, biosample):
    return {
        'award': award['uuid'],
        'lab': lab['uuid'],
        'nucleic_acid_term_id': 'SO:0000352',
        'nucleic_acid_term_name': 'DNA',
        'aliases': ['encode:base-library']
    }


@pytest.fixture
def base_replicate(award, lab, experiment):
    return {
        'experiment': experiment['uuid'],
        'biological_replicate_number': 1,
        'technical_replicate_number': 1,
        'experiment': 'encode:base-experiment',
        'library': 'encode:base-library'
    }


def test_audit_experiment_target(testapp, chip_experiment):
    res = testapp.post_json('/experiment', chip_experiment)
    res = testapp.get(res.location + '@@index-data')
    error, = res.json['audit']
    assert error['category'] == 'missing target'


def test_audit_experiment_paired_ended(testapp, base_experiment, base_library, base_replicate):
    res = testapp.post_json('/experiment', base_experiment)
    lib = testapp.post_json('/library', base_library)
    rep = testapp.post_json('/replicate', base_replicate)
    res = testapp.get(res.location + '@@index-data')
    error, = res.json['audit']
