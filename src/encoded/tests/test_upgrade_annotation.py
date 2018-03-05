import pytest


@pytest.fixture
def annotation_0(submitter, lab, award):
    return {
        'award': award['uuid'],
        'lab': lab['uuid'],
    }


@pytest.fixture
def annotation_16(annotation_0):
    item = annotation_0.copy()
    item.update({
        'biosample_type': 'immortalized cell line'
    })
    return item


def test_upgrade_annotation_16_to_17(upgrader, annotation_16, biosample):
    value = upgrader.upgrade('annotation', annotation_16, current_version='16', target_version='17')
    assert value['biosample_type'] == 'cell line'
