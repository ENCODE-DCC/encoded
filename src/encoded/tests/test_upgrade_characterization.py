import pytest
    
SCHEMA_DIR = 'src/encoded/schemas/'


@pytest.fixture
def antibody_characterization(submitter, award, lab, characterizes, target):
    return {
        'award': award['uuid'],
        'lab': lab['uuid'],
        'target': target['uuid'],
        'characterizes': antibody_lot['uuid'],
    }

@pytest.fixture
def biosample_characterization(submitter, award, lab, characterizes):
    return {
        'award': award['uuid'],
        'lab': lab['uuid'],
        'characterizes': biosample['uuid'],
    }

@pytest.fixture
def rnai_characterization(submitter, award, lab, characterizes):
    return {
        'award': award['uuid'],
        'lab': lab['uuid'],
        'characterizes': rnai['uuid'],
    }

@pytest.fixture
def construct_characterization(submitter, award, lab, characterizes):
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

def test_antibody_characterization_upgrade(app, antibody_characterization_1):
    from encoded.schema_utils import load_schema
    schema = load_schema('antibody_characterization.json')
    migrator = app.registry['migrator']
    value = migrator.upgrade('antibody_characterization', antibody_characterization_1, target_version='3')
    assert value['schema_version'] == schema['properties']['schema_version']
    assert value['status'] == 'PENDING DCC REVIEW'
    assert value['characterization_method'] == 'immunoprecipitation followed by mass spectrometry'


def test_biosample_characterization_upgrade(app, biosample_characterization_1):
    from encoded.schema_utils import load_schema
    schema = load_schema('biosample_characterization.json')
    migrator = app.registry['migrator']
    value = migrator.upgrade('biosample_characterization', biosample_characterization_1, target_version='3')
    assert value['schema_version'] == schema['properties']['schema_version']
    assert value['status'] == 'NOT REVIEWED'
    assert value['characterization_method'] == 'FACs analysis'

def test_construct_characterization_upgrade(app, construct_characterization_1):
    from encoded.schema_utils import load_schema
    schema = load_schema('construct_characterization.json')
    migrator = app.registry['migrator']
    value = migrator.upgrade('construct_characterization', construct_characterization_1, target_version='3')
    assert value['schema_version'] == schema['properties']['schema_version']
    assert value['status'] == 'NOT SUBMITTED FOR REVIEW BY LAB'
    assert value['characterization_method'] == 'immunoblot'

def test_rnai_characterization_upgrade(app, rnai_characterization_1):
    from encoded.schema_utils import load_schema
    schema = load_schema('rnai_characterization.json')
    migrator = app.registry['migrator']
    value = migrator.upgrade('rnai_characterization', rnai_characterization_1, target_version='3')
    assert value['schema_version'] == schema['properties']['schema_version']
    assert value['status'] == 'IN PROGRESS'
    assert value['characterization_method'] == 'knockdown or knockout'

def test_antibody_characterization_upgrade_inline(testapp, antibody_characterization_1):
    from encoded.schema_utils import load_schema
    schema = load_schema('antibody_characterization.json')

    res = testapp.post_json('/antibody-characterizations?validate=false&render=uuid', antibody_characterization_1)
    location = res.location

    # The properties are stored un-upgraded.
    res = testapp.get(location+'?raw=true&upgrade=false').maybe_follow()
    assert res.json['schema_version'] == '1'

    # When the item is fetched, it is upgraded automatically.
    res = testapp.get(location).maybe_follow()
    assert res.json['schema_version'] == schema['properties']['schema_version']

    res = testapp.patch_json(location, {})

    # The stored properties are now upgraded.
    res = testapp.get(location+'?raw=true&upgrade=false').maybe_follow()
    assert res.json['schema_version'] == schema['properties']['schema_version']

