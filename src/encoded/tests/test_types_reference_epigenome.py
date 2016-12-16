import pytest


@pytest.fixture
def base_reference_epigenome(testapp, lab, award):
    item = {
        'award': award['uuid'],
        'lab': lab['uuid']
    }
    return testapp.post_json('/reference_epigenome', item, status=201).json['@graph'][0]


@pytest.fixture
def base_experiment_1(testapp, lab, award):
    item = {
        'award': award['uuid'],
        'lab': lab['uuid'],
        'assay_term_name': 'RNA-seq',
        'status': 'started'
    }
    return testapp.post_json('/experiment', item, status=201).json['@graph'][0]


@pytest.fixture
def base_experiment_2(testapp, lab, award):
    item = {
        'award': award['uuid'],
        'lab': lab['uuid'],
        'assay_term_name': 'RNA-seq',
        'status': 'started'
    }
    return testapp.post_json('/experiment', item, status=201).json['@graph'][0]


def test_single_donor(testapp, base_reference_epigenome, donor_1, biosample_1, biosample_2, library_1, library_2, replicate_1_1, replicate_2_1, base_experiment_1, base_experiment_2 ):   
    testapp.patch_json(biosample_1['@id'], {'donor': donor_1['@id']})
    testapp.patch_json(biosample_2['@id'], {'donor': donor_1['@id']})
    testapp.patch_json(library_1['@id'], {'biosample': biosample_1['@id']})
    testapp.patch_json(library_2['@id'], {'biosample': biosample_2['@id']})
    testapp.patch_json(replicate_1_1['@id'], {'library': library_1['@id'], 'experiment': base_experiment_1['@id']})
    testapp.patch_json(replicate_2_1['@id'], {'library': library_2['@id'], 'experiment': base_experiment_2['@id']})
    testapp.patch_json(base_reference_epigenome['@id'], {'related_datasets': [base_experiment_1['@id'], base_experiment_2['@id']]})
    res = testapp.get(base_reference_epigenome['@id']+'@@index-data')
    assert res.json['object']['donor_diversity']=='single'


def test_composite(testapp, base_reference_epigenome, donor_1, donor_2, biosample_1, biosample_2, library_1, library_2, replicate_1_1, replicate_2_1, base_experiment_1, base_experiment_2 ):
    testapp.patch_json(biosample_1['@id'], {'donor': donor_1['@id']})
    testapp.patch_json(biosample_2['@id'], {'donor': donor_2['@id']})
    testapp.patch_json(library_1['@id'], {'biosample': biosample_1['@id']})
    testapp.patch_json(library_2['@id'], {'biosample': biosample_2['@id']})
    testapp.patch_json(replicate_1_1['@id'], {'library': library_1['@id'], 'experiment': base_experiment_1['@id']})
    testapp.patch_json(replicate_2_1['@id'], {'library': library_2['@id'], 'experiment': base_experiment_2['@id']})
    testapp.patch_json(base_reference_epigenome['@id'], {'related_datasets': [base_experiment_1['@id'], base_experiment_2['@id']]})
    res = testapp.get(base_reference_epigenome['@id']+'@@index-data')
    assert res.json['object']['donor_diversity']=='composite'


def test_no_donors(testapp, base_reference_epigenome, donor_1, donor_2, biosample_1, biosample_2, library_1, library_2, replicate_1_1, replicate_2_1, base_experiment_1, base_experiment_2 ):
    testapp.patch_json(library_1['@id'], {'biosample': biosample_1['@id']})
    testapp.patch_json(library_2['@id'], {'biosample': biosample_2['@id']})
    testapp.patch_json(replicate_1_1['@id'], {'library': library_1['@id'], 'experiment': base_experiment_1['@id']})
    testapp.patch_json(replicate_2_1['@id'], {'library': library_2['@id'], 'experiment': base_experiment_2['@id']})
    testapp.patch_json(base_reference_epigenome['@id'], {'related_datasets': [base_experiment_1['@id'], base_experiment_2['@id']]})
    res = testapp.get(base_reference_epigenome['@id']+'@@index-data')
    assert res.json['object']['donor_diversity']=='none'
