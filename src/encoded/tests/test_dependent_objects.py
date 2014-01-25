def test_dependent_objects(root, experiment, replicate):
    from uuid import UUID
    from ..indexing import add_dependent_objects
    existing = set()
    add_dependent_objects(root, {UUID(replicate['uuid'])}, existing)
    assert UUID(experiment['uuid']) in existing
