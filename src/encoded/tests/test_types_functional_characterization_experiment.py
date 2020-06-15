import pytest


def test_fcc_replicate_type(
    testapp, functional_characterization_experiment, pooled_clone_sequencing
):
    res = testapp.get(
        functional_characterization_experiment['@id']+'@@index-data'
    )
    assert res.json['object']['replication_type'] == 'unreplicated'
    res = testapp.get(
        pooled_clone_sequencing['@id']+'@@index-data'
    )
    assert 'replication_type' not in res.json['object']
