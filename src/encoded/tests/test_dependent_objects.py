""" Referencing object invalidation

Objects embed referenced objects for search and display. When a referenced
object is updated all referencing objects must be reindexed.
"""


def referencing(root, uuid):
    from uuid import UUID
    from ..indexing import add_dependent_objects
    existing = set()
    add_dependent_objects(root, {UUID(uuid)}, existing)
    return {str(uuid) for uuid in existing}


def test_reverse_dependency(root, experiment, replicate):
    assert experiment['uuid'] in referencing(root, replicate['uuid'])


def test_experiment_invalidation(root, experiment, replicate, library, biosample, organism):
    assert experiment['uuid'] in referencing(root, experiment['uuid'])
    assert experiment['uuid'] in referencing(root, replicate['uuid'])
    assert experiment['uuid'] in referencing(root, library['uuid'])
    assert experiment['uuid'] in referencing(root, biosample['uuid'])
    assert experiment['uuid'] in referencing(root, organism['uuid'])
