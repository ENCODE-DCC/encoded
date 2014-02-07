import pytest

SCHEMA_DIR = 'src/encoded/schemas/'

@pytest.fixture
def biosample(submitter, lab, award, source, organism):
    return {
        'award': award['uuid'],
        'biosample_term_id': 'UBERON:349829',
        'biosample_type': 'tissue',
        'lab': lab['uuid'],
        'organism': organism['uuid'],
        'source': source['uuid'],
    }

@pytest.fixture
def biosample_1(biosample):
    item = biosample.copy()
    item.update({
        'schema_version': '1',
        'starting_amount': '1000',
    })
    return item

@pytest.fixture
def biosample_2(biosample):
    item = biosample.copy()
    item.update({
        'schema_version': '2',
        'subcellular_fraction': 'nucleus',
    })
    return item

def test_biosample_upgrade(app, biosample_1):
    migrator = app.registry['migrator']
    value = migrator.upgrade('biosample', biosample_1, target_version='2')
    assert value['schema_version'] == '2'
    assert value['starting_amount'] == 1000


def test_biosample_upgrade_unknown(app, biosample_1):
    biosample_1['starting_amount'] = 'Unknown'
    migrator = app.registry['migrator']
    value = migrator.upgrade('biosample', biosample_1, target_version='2')
    assert value['schema_version'] == '2'
    assert 'starting_amount' not in value


def test_biosample_upgrade_empty_string(app, biosample_1):
    biosample_1['starting_amount'] = ''
    migrator = app.registry['migrator']
    value = migrator.upgrade('biosample', biosample_1, target_version='2')
    assert value['schema_version'] == '2'
    assert 'starting_amount' not in value


def test_biosample_upgrade_exponent(app, biosample_1):
    biosample_1['starting_amount'] = '1 X 10^5'
    migrator = app.registry['migrator']
    value = migrator.upgrade('biosample', biosample_1, target_version='2')
    assert value['schema_version'] == '2'
    assert value['starting_amount'] == 1e5

def test_biosample_upgrade_number(app, biosample_1):
    biosample_1['starting_amount'] = -1
    migrator = app.registry['migrator']
    value = migrator.upgrade('biosample', biosample_1, target_version='2')
    assert value['schema_version'] == '2'
    assert value['starting_amount'] == -1


def test_biosample_upgrade_subcellular_fraction(app, biosample_2):
    migrator = app.registry['migrator']
    value = migrator.upgrade('biosample', biosample_2, target_version='3')
    assert value['schema_version'] == '3'
    assert value['subcellular_fraction_term_name'] == 'nucleus'
    assert value['subcellular_fraction_term_id'] == 'GO:0005634'
    assert 'subcellular_fraction' not in value

def test_biosample_upgrade_subcellular_fraction_membrane(app, biosample_2):
    biosample_2['subcellular_fraction'] = 'membrane fraction'
    migrator = app.registry['migrator']
    value = migrator.upgrade('biosample', biosample_2, target_version='3')
    assert value['schema_version'] == '3'
    assert value['subcellular_fraction_term_name'] == 'membrane'
    assert value['subcellular_fraction_term_id'] == 'GO:0016020'
    assert 'subcellular_fraction' not in value


def test_biosample_upgrade_inline(testapp, biosample_1):
    from encoded.schema_utils import load_schema
    schema = load_schema('biosample.json')
    res = testapp.post_json('/biosample?validate=false&render=uuid', biosample_1)
    location = res.location

    # The properties are stored un-upgraded.
    res = testapp.get(location+'?raw=true&upgrade=false').maybe_follow()
    assert res.json['schema_version'] == '1'

    # When the item is fetched, it is upgraded automatically.
    res = testapp.get(location).maybe_follow()
    assert res.json['schema_version'] == schema['properties']['schema_version']['default']

    res = testapp.patch_json(location, {})

    # The stored properties are now upgraded.
    res = testapp.get(location+'?raw=true&upgrade=false').maybe_follow()
    assert res.json['schema_version'] == schema['properties']['schema_version']['default']


def test_biosample_upgrade_inline_unknown(testapp, biosample_1):
    from encoded.schema_utils import load_schema
    schema = load_schema('biosample.json')
    biosample_1['starting_amount'] = 'Unknown'
    res = testapp.post_json('/biosample?validate=false&render=uuid', biosample_1)
    location = res.location
    res = testapp.patch_json(location, {})
    res = testapp.get(location+'?raw=true&upgrade=false').maybe_follow()
    assert res.json['schema_version'] == schema['properties']['schema_version']['default']
    assert 'starting_amount' not in res.json
