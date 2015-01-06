import pytest
from ..loadxl import ORDER


@pytest.mark.parametrize('item_type', ORDER)
def test_create_mapping(root, registry, item_type):
    from ..commands.create_mapping import collection_mapping
    collection = root[item_type]
    calculated_properties = registry['calculated_properties']
    mapping = collection_mapping(calculated_properties, collection)
    assert mapping
