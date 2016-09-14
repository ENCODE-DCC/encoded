import pytest


@pytest.fixture
def control_experiment(testapp, award, lab, target_control):
    item = {
        'assay_term_name': 'ChIP-seq',
        'assay_term_id': 'OBI:0000716',
        'target': target_control['uuid'],
        'award': award['uuid'],
        'lab': lab['uuid']
    }
    return testapp.post_json('/experiment', item).json['@graph'][0]


@pytest.fixture
def experiment_with_control(award, lab, target):
    return {
        'assay_term_name': 'ChIP-seq',
        'assay_term_id': 'OBI:0000716',
        'target': target['uuid'],
        'award': award['uuid'],
        'lab': lab['uuid']
        }


@pytest.fixture
def annotation(testapp, award, lab):
    item = {
        'award': award['@id'],
        'lab': lab['@id'],
        'annotation_type': 'enhancer predictions'
    }
    return testapp.post_json('/annotation', item).json['@graph'][0]


@pytest.fixture
def matched_set(testapp, award, lab, control_experiment):
    item = {
        'award': award['@id'],
        'lab': lab['@id'],
        'related_datasets': [control_experiment['@id']]
    }
    return testapp.post_json('/MatchedSet', item).json['@graph'][0]


def test_experiment_post(testapp, experiment_with_control, control_experiment):
    experiment_with_control.update({'possible_controls': [control_experiment['@id']]})
    testapp.post_json('/experiment', experiment_with_control).json['@graph'][0]
    assert 'Experiment' in control_experiment.get('@type')


def test_experiment_controlled_by_annotation(testapp, experiment_with_control, annotation,
                                             control_experiment):
    experiment_with_control.update({'possible_controls': [annotation['@id']]})
    testapp.post_json('/experiment', experiment_with_control, status=422)


def test_experiment_controlled_by_matched_set(testapp, experiment_with_control, matched_set):
    experiment_with_control.update({'possible_controls': [matched_set['@id']]})
    testapp.post_json('/experiment', experiment_with_control).json['@graph'][0]
    assert 'MatchedSet' in matched_set.get('@type')
