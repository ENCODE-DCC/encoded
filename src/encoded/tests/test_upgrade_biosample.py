import pytest

@pytest.fixture
def biosample_1():
    return {
        'schema_version': '1',
        'starting_amount': '1000',
    }


def test_biosample_upgrade(app, biosample_1):
    migrator = app.registry['migrator']
    value = migrator.upgrade('biosample', biosample_1, target_version='2')
    assert value['starting_amount'] == 1000
    assert value['schema_version'] == '2'
