import pytest


@pytest.fixture
def antibody_approval(submitter, award, lab, antibody_lot, target):
    return {
        'award': award['uuid'],
        'lab': lab['uuid'],
        'target': target['uuid'],
        'antibody': antibody_lot['uuid'],
    }

@pytest.fixture
def antibody_approval_1(antibody_approval):
    item = antibody_approval.copy()
    item.update({
        'schema_version': '1',
        'status': 'SUBMITTED',
    })
    return item


def test_antibody_approval_upgrade(app, antibody_approval_1):
    migrator = app.registry['migrator']
    value = migrator.upgrade('antibody_approval', antibody_approval_1, target_version='2')
    assert value['schema_version'] == '2'
    assert value['status'] == 'PENDING DCC REVIEW'


def test_antibody_approval_upgrade_inline(testapp, root, antibody_approval_1):
    schema = root.by_item_type['antibody_approval'].schema

    res = testapp.post_json('/antibodies?validate=false&render=uuid', antibody_approval_1)
    location = res.location

    # The properties are stored un-upgraded.
    res = testapp.get(location+'?frame=raw&upgrade=false').maybe_follow()
    assert res.json['schema_version'] == '1'

    # When the item is fetched, it is upgraded automatically.
    res = testapp.get(location).maybe_follow()
    assert res.json['schema_version'] == schema['properties']['schema_version']['default']

    res = testapp.patch_json(location, {})

    # The stored properties are now upgraded.
    res = testapp.get(location+'?frame=raw&upgrade=false').maybe_follow()
    assert res.json['schema_version'] == schema['properties']['schema_version']['default']
