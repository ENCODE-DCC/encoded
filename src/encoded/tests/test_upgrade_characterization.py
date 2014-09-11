import pytest


@pytest.fixture
def antibody_characterization(submitter, award, lab, antibody_lot, target):
    return {
        'award': award['uuid'],
        'lab': lab['uuid'],
        'target': target['uuid'],
        'characterizes': antibody_lot['uuid'],
    }


@pytest.fixture
def biosample_characterization(submitter, award, lab, biosample):
    return {
        'award': award['uuid'],
        'lab': lab['uuid'],
        'characterizes': biosample['uuid'],
    }


@pytest.fixture
def rnai_characterization(submitter, award, lab, rnai):
    return {
        'award': award['uuid'],
        'lab': lab['uuid'],
        'characterizes': rnai['uuid'],
    }


@pytest.fixture
def construct_characterization(submitter, award, lab, construct):
    return {
        'award': award['uuid'],
        'lab': lab['uuid'],
        'characterizes': construct['uuid'],
    }


@pytest.fixture
def antibody_characterization_1(antibody_characterization):
    item = antibody_characterization.copy()
    item.update({
        'schema_version': '1',
        'status': 'SUBMITTED',
        'characterization_method': 'mass spectrometry after IP',
    })
    return item


@pytest.fixture
def antibody_characterization_2(antibody_characterization):
    item = antibody_characterization.copy()
    item.update({
        'schema_version': '3',
        'status': 'COMPLIANT'
    })
    return item


@pytest.fixture
def biosample_characterization_1(biosample_characterization):
    item = biosample_characterization.copy()
    item.update({
        'schema_version': '2',
        'status': 'APPROVED',
        'characterization_method': 'immunofluorescence',
    })
    return item


@pytest.fixture
def rnai_characterization_1(rnai_characterization):
    item = rnai_characterization.copy()
    item.update({
        'schema_version': '2',
        'status': 'INCOMPLETE',
        'characterization_method': 'knockdowns',
    })
    return item


@pytest.fixture
def construct_characterization_1(construct_characterization):
    item = construct_characterization.copy()
    item.update({
        'schema_version': '1',
        'status': 'FAILED',
        'characterization_method': 'western blot',
    })
    return item


@pytest.fixture
def biosample_characterization_2(biosample_characterization):
    item = biosample_characterization.copy()
    item.update({
        'schema_version': '3',
        'status': 'IN PROGRESS',
        'award': '1a4d6443-8e29-4b4a-99dd-f93e72d42418'
    })
    return item


@pytest.fixture
def rnai_characterization_2(rnai_characterization):
    item = rnai_characterization.copy()
    item.update({
        'schema_version': '3',
        'status': 'IN PROGRESS',
        'award': 'ea1f650d-43d3-41f0-a96a-f8a2463d332f'
    })
    return item


@pytest.fixture
def construct_characterization_2(construct_characterization):
    item = construct_characterization.copy()
    item.update({
        'schema_version': '2',
        'status': 'DELETED',
        'award': '1a4d6443-8e29-4b4a-99dd-f93e72d42418'
    })
    return item


@pytest.fixture
def antibody_characterization_3(antibody_characterization):
    item = antibody_characterization.copy()
    item.update({
        'schema_version': '4',
        'characterization_method': 'immunoblot',
    })
    return item


@pytest.fixture
def construct_characterization_3(construct_characterization):
    item = construct_characterization.copy()
    item.update({
        'schema_version': '4',
        'documents': []
    })
    return item


def test_antibody_characterization_upgrade(app, antibody_characterization_1):
    migrator = app.registry['migrator']
    value = migrator.upgrade('antibody_characterization', antibody_characterization_1, target_version='3')
    assert value['schema_version'] == '3'
    assert value['status'] == 'PENDING DCC REVIEW'
    assert value['characterization_method'] == 'immunoprecipitation followed by mass spectrometry'


def test_biosample_characterization_upgrade(app, biosample_characterization_1):
    migrator = app.registry['migrator']
    value = migrator.upgrade('biosample_characterization', biosample_characterization_1, target_version='3')
    assert value['schema_version'] == '3'
    assert value['status'] == 'NOT REVIEWED'
    assert value['characterization_method'] == 'FACs analysis'


def test_construct_characterization_upgrade(app, construct_characterization_1):
    migrator = app.registry['migrator']
    value = migrator.upgrade('construct_characterization', construct_characterization_1, target_version='3')
    assert value['schema_version'] == '3'
    assert value['status'] == 'NOT SUBMITTED FOR REVIEW BY LAB'
    assert value['characterization_method'] == 'immunoblot'


def test_rnai_characterization_upgrade(app, rnai_characterization_1):
    migrator = app.registry['migrator']
    value = migrator.upgrade('rnai_characterization', rnai_characterization_1, target_version='3')
    assert value['schema_version'] == '3'
    assert value['status'] == 'IN PROGRESS'
    assert value['characterization_method'] == 'knockdown or knockout'


def test_antibody_characterization_upgrade_status(app, antibody_characterization_2):
    migrator = app.registry['migrator']
    value = migrator.upgrade('antibody_characterization', antibody_characterization_2, target_version='4')
    assert value['schema_version'] == '4'
    assert value['status'] == 'compliant'


def test_biosample_characterization_upgrade_status_encode2(app, biosample_characterization_2):
    migrator = app.registry['migrator']
    value = migrator.upgrade('biosample_characterization', biosample_characterization_2, target_version='4')
    assert value['schema_version'] == '4'
    assert value['status'] == 'released'


def test_rnai_characterization_upgrade_status_encode3(app, rnai_characterization_2):
    migrator = app.registry['migrator']
    value = migrator.upgrade('rnai_characterization', rnai_characterization_2, target_version='4')
    assert value['schema_version'] == '4'
    assert value['status'] == 'in progress'


def test_construct_characterization_upgrade_status_deleted(app, construct_characterization_2):
    migrator = app.registry['migrator']
    value = migrator.upgrade('construct_characterization', construct_characterization_2, target_version='4')
    assert value['schema_version'] == '4'
    assert value['status'] == 'deleted'


def test_antibody_characterization_upgrade_primary(app, antibody_characterization_3):
    migrator = app.registry['migrator']
    value = migrator.upgrade('antibody_characterization', antibody_characterization_3, target_version='5')
    assert value['schema_version'] == '5'
    assert value['primary_characterization_method'] == 'immunoblot'
    assert 'characterization_method' not in value


def test_antibody_characterization_upgrade_secondary(app, antibody_characterization_3):
    antibody_characterization_3['characterization_method'] = 'immunoprecipitation followed by mass spectrometry'
    migrator = app.registry['migrator']
    value = migrator.upgrade('antibody_characterization', antibody_characterization_3, target_version='5')
    assert value['schema_version'] == '5'
    assert value['secondary_characterization_method'] == 'immunoprecipitation followed by mass spectrometry'
    assert 'characterization_method' not in value


def test_antibody_characterization_upgrade_compliant_status(app, antibody_characterization_3):
    antibody_characterization_3['characterization_method'] = 'immunoprecipitation followed by mass spectrometry'
    antibody_characterization_3['status'] = 'compliant'
    migrator = app.registry['migrator']
    value = migrator.upgrade('antibody_characterization', antibody_characterization_3, target_version='5')
    assert value['schema_version'] == '5'
    assert value['secondary_characterization_method'] == 'immunoprecipitation followed by mass spectrometry'
    assert 'characterization_method' not in value
    assert value['reviewed_by'] == '/users/81a6cc12-2847-4e2e-8f2c-f566699eb29e/'
    assert value['documents'] == ['88dc12f7-c72d-4b43-a6cd-c6f3a9d08821']


def test_antibody_characterization_upgrade_not_compliant_status(app, antibody_characterization_3):
    antibody_characterization_3['characterization_method'] = 'immunoprecipitation followed by mass spectrometry'
    antibody_characterization_3['status'] = 'not reviewed'
    migrator = app.registry['migrator']
    value = migrator.upgrade('antibody_characterization', antibody_characterization_3, target_version='5')
    assert value['schema_version'] == '5'
    assert value['secondary_characterization_method'] == 'immunoprecipitation followed by mass spectrometry'
    assert 'characterization_method' not in value
    assert value['reviewed_by'] == '/users/ff7b77e7-bb55-4307-b665-814c9f1e65fb/'


def test_antibody_characterization_upgrade_inline(testapp, root, antibody_characterization_1):
    schema = root.by_item_type['antibody_characterization'].schema

    res = testapp.post_json('/antibody-characterizations?validate=false&render=uuid', antibody_characterization_1)
    location = res.location

    # The properties are stored un-upgraded.
    res = testapp.get(location + '?frame=raw&upgrade=false').maybe_follow()
    assert res.json['schema_version'] == '1'

    # When the item is fetched, it is upgraded automatically.
    res = testapp.get(location).maybe_follow()
    assert res.json['schema_version'] == schema['properties']['schema_version']['default']

    res = testapp.patch_json(location, {})

    # The stored properties are now upgraded.
    res = testapp.get(location + '?frame=raw&upgrade=false').maybe_follow()
    assert res.json['schema_version'] == schema['properties']['schema_version']['default']
