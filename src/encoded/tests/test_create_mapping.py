import pytest
from ..loadxl import ORDER


@pytest.mark.parametrize('item_type', ORDER)
def test_create_mapping(root, item_type):
    from ..commands.create_mapping import collection_mapping
    collection = root[item_type]
    mapping = collection_mapping(collection)
    assert mapping
