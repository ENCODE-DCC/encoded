import pytest
from ..loadxl import ORDER


@pytest.mark.parametrize('item_type', ORDER)
def test_create_mapping(registry, item_type):
    from contentbase.elasticsearch.create_mapping import type_mapping
    from contentbase import TYPES
    mapping = type_mapping(registry[TYPES], item_type)
    assert mapping
