import pytest
from datetime import datetime


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


def test_functional_characterization_experiment_control(testapp, functional_characterization_experiment):
    testapp.patch_json(functional_characterization_experiment['@id'], {'control_type': 'control'})
    res = testapp.get(functional_characterization_experiment['@id']+'@@index-data')
    assert res.json['object']['assay_title']=='Control STARR-seq'


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


def test_functional_characterization_experiment_target_expression_dependency(testapp, functional_characterization_experiment_4, target):
    # the property target_expression_percentile can't be specified without target
    testapp.post_json('/functional_characterization_experiment', functional_characterization_experiment_4, status=422)
    functional_characterization_experiment_4.update({'target': target['uuid']})
    testapp.post_json('/functional_characterization_experiment', functional_characterization_experiment_4, status=201)
    # the property also may not coexist with target_expression_range_maximum
    functional_characterization_experiment_4.update({'target_expression_range_maximum': 90})
    testapp.post_json('/functional_characterization_experiment', functional_characterization_experiment_4, status=422)


def test_functional_characterization_experiment_examined_loci_dependency(testapp, functional_characterization_experiment_6, ctcf):
    # the property examined_loci may specify a single gene, without expression properties
    testapp.post_json('/functional_characterization_experiment', functional_characterization_experiment_6, status=201)

    # the property examined_loci may not specify expression_percentile AND expression_range_maximum, expression_range_minimum for each item
    functional_characterization_experiment_6.update({'examined_loci': [{'gene': ctcf['uuid'], 'expression_percentile': 80, 'expression_range_minimum': 50, 'expression_range_maximum': 100}]})
    testapp.post_json('/functional_characterization_experiment', functional_characterization_experiment_6, status=422)

    # expression_range_maximum and expression_range_minimum must be included together
    functional_characterization_experiment_6.update({'examined_loci': [{'gene': ctcf['uuid'], 'expression_range_maximum': 100}]})
    testapp.post_json('/functional_characterization_experiment', functional_characterization_experiment_6, status=422)
    functional_characterization_experiment_6.update({'examined_loci': [{'gene': ctcf['uuid'], 'expression_range_minimum': 50, 'expression_range_maximum': 100}]})
    testapp.post_json('/functional_characterization_experiment', functional_characterization_experiment_6, status=201)

    # expression_percentile may be specified with gene, but not in combination with a single range property
    functional_characterization_experiment_6.update({'examined_loci': [{'gene': ctcf['uuid'], 'expression_percentile': 100, 'expression_range_minimum': 50}]})
    testapp.post_json('/functional_characterization_experiment', functional_characterization_experiment_6, status=422)
    functional_characterization_experiment_6.update({'examined_loci': [{'gene': ctcf['uuid'], 'expression_percentile': 100}]})
    testapp.post_json('/functional_characterization_experiment', functional_characterization_experiment_6, status=201)


def test_functional_characterization_experiment_target_import_items(testapp, submitter_testapp, functional_characterization_experiment_item, target):
    # Target can not be submitted without admin permissions
    res = testapp.post_json('/functional_characterization_experiment', functional_characterization_experiment_item, status=201)
    submitter_testapp.patch_json(res.json['@graph'][0]['@id'], {'target': target['uuid']}, status=422)
    testapp.patch_json(res.json['@graph'][0]['@id'], {'target': target['uuid']}, status=200)
