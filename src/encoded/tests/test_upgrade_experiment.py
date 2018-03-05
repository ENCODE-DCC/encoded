import pytest


@pytest.fixture
def experiment_0(submitter, lab, award):
    return {
        'award': award['uuid'],
        'lab': lab['uuid'],
        'assay_term_name': 'DNase-seq',
        'biosample_type': 'immortalized cell line'
    }


@pytest.fixture
def experiment_15(experiment_0):
    item = experiment_0.copy()
    return item


def test_upgrade_experiment_15_to_16(upgrader, experiment_15, biosample):
    value = upgrader.upgrade('experiment', experiment_15, current_version='15', target_version='16')
    assert value['biosample_type'] == 'cell line'
