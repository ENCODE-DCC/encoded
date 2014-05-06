import pytest


@pytest.fixture
def user():
    return{
        'first_name': 'Benjamin',
        'last_name': 'Hitz',
        'email': 'hitz@stanford.edu',
    }


@pytest.fixture
def user_1(user):
    item = user.copy()
    item.update({
        'schema_version': '2',
        'status': 'CURRENT'
    })
    return item


def test_user_upgrade(app, user_1):
    migrator = app.registry['migrator']
    value = migrator.upgrade('user', user_1, target_version='3')
    assert value['schema_version'] == '3'
    assert value['status'] == 'current'
