import pytest


@pytest.fixture
def replicate(submitter, award, lab, experiment):
    return {
        'experiment': experiment['uuid'],
        'biological_replicate_number': 1,
        'technical_replicate_number': 1
    }

@pytest.fixture
def replicate_2(replicate):
    item = replicate.copy()
    item.update({
        'schema_version': '2',
       'paired_ended': False
    })
    return item


def test_replicate_upgrade(app, replicate_2):
    migrator = app.registry['migrator']
    value = migrator.upgrade('replicate', replicate_2, target_version='3')
    assert value['schema_version'] == '3'
    assert 'paired_ended' not in value

def test_replicate_upgrade_read_length(app, replicate_2):
    replicate_2['read_length'] = 36
    replicate_2['read_length_units'] = 'nt'
    migrator = app.registry['migrator']
    value = migrator.upgrade('replicate', replicate_2, target_version='3')
    assert value['schema_version'] == '3'
    assert value['paired_ended'] == False
