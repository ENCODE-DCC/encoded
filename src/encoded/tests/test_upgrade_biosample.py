import pytest

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


def test_biosample_upgrade(app, biosample_1):
    migrator = app.registry['migrator']
    value = migrator.upgrade('biosample', biosample_1, target_version='2')
    assert value['starting_amount'] == 1000
    assert value['schema_version'] == '2'


def test_biosample_upgrade_inline(testapp, biosample_1):
    res = testapp.post_json('/biosample?validate=false&render=uuid', biosample_1)
    location = res.location

    # The properties are stored un-upgraded.
    res = testapp.get(location+'?raw=true&upgrade=false').maybe_follow()
    assert res.json['schema_version'] == '1'

    # When the item is fetched, it is upgraded automatically.
    res = testapp.get(location).maybe_follow()
    assert res.json['schema_version'] == '2'

    res = testapp.patch_json(location, {})

    # The stored properties are now upgraded.
    res = testapp.get(location+'?raw=true&upgrade=false').maybe_follow()
    assert res.json['schema_version'] == '2'
