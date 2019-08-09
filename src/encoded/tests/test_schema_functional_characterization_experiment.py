import pytest
from datetime import datetime


@pytest.fixture
def functional_characterization_experiment_item(testapp, lab, award, cell_free):
    item = {
        'lab': lab['@id'],
        'award': award['@id'],
        'assay_term_name': 'STARR-seq',
        'biosample_ontology': cell_free['uuid'],
        'status': 'in progress'
    }
    return item


@pytest.fixture
def functional_characterization_experiment_screen(testapp, lab, award, heart, target):
    item = {
        'lab': lab['@id'],
        'award': award['@id'],
        'assay_term_name': 'CRISPR screen',
        'biosample_ontology': heart['uuid'],
        'status': 'in progress',
        'target': target['uuid']

    }
    return item


@pytest.fixture
def functional_characterization_experiment(testapp, lab, award, cell_free):
    item = {
        'lab': lab['@id'],
        'award': award['@id'],
        'assay_term_name': 'STARR-seq',
        'biosample_ontology': cell_free['uuid'],
        'status': 'in progress'
    }
    return testapp.post_json('/functional_characterization_experiment', item).json['@graph'][0]


def test_valid_functional_characterization_experiment(testapp, functional_characterization_experiment_item):
    testapp.post_json('/functional_characterization_experiment', functional_characterization_experiment_item, status=201)


def test_invalid_functional_characterization_experiment(testapp, functional_characterization_experiment_item):
    functional_characterization_experiment_item['assay_term_name'] = 'ChIP-seq'
    testapp.post_json('/functional_characterization_experiment', functional_characterization_experiment_item, status=422)


def test_functional_characterization_experiment_screen(testapp, functional_characterization_experiment_screen):
    testapp.post_json('/functional_characterization_experiment', functional_characterization_experiment_screen, status=201)
    functional_characterization_experiment_screen['target_expression_range_maximum'] = 45
    testapp.post_json('/functional_characterization_experiment', functional_characterization_experiment_screen, status=422)
    functional_characterization_experiment_screen['target_expression_range_minimum'] = 25
    testapp.post_json('/functional_characterization_experiment', functional_characterization_experiment_screen, status=201)


@pytest.mark.parametrize(
    'status',
    [
        'in progress',
        'submitted',
        'released',
        'archived',
        'deleted',
        'revoked'
    ]
)
def test_functional_characterization_experiment_valid_statuses(status, testapp, functional_characterization_experiment):
    # Need date_released for released/revoked functional_characterization_experiment dependency.
    # Need date_submitted for submitted functional_characterization_experiment dependency.
    testapp.patch_json(
        functional_characterization_experiment['@id'],
        {'date_released': datetime.now().strftime('%Y-%m-%d'),
         'date_submitted': datetime.now().strftime('%Y-%m-%d')}
    )
    testapp.patch_json(functional_characterization_experiment['@id'], {'status': status})
    res = testapp.get(functional_characterization_experiment['@id'] + '@@embedded').json
    assert res['status'] == status


def test_functional_characterization_experiment_possible_controls(testapp, functional_characterization_experiment, experiment):
    testapp.patch_json(
        functional_characterization_experiment['@id'],
        {'possible_controls': [experiment['@id']]},
        status=200)