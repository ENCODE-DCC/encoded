import pytest


@pytest.fixture
def annotation_8(award, lab):
    return {
        'award': award['@id'],
        'lab': lab['@id'],
        'schema_version': '8',
        'annotation_type': 'encyclopedia'
    }


def test_annotation_upgrade_1(registry, annotation_8):
    from snovault import UPGRADER
    upgrader = registry[UPGRADER]
    value = upgrader.upgrade('annotation',
                             annotation_8, registry=registry,
                             current_version='8', target_version='9')
    assert value['annotation_type'] == 'other'


def test_annotation_upgrade_2(registry, annotation_8):
    annotation_8['annotation_type'] = 'enhancer prediction'
    from snovault import UPGRADER
    upgrader = registry[UPGRADER]
    value = upgrader.upgrade('annotation',
                             annotation_8, registry=registry,
                             current_version='8', target_version='9')
    assert value['annotation_type'] == 'enhancer predictions'


def test_annotation_upgrade_3(registry, annotation_8):
    annotation_8['annotation_type'] = 'segmentation'
    from snovault import UPGRADER
    upgrader = registry[UPGRADER]
    value = upgrader.upgrade('annotation',
                             annotation_8, registry=registry,
                             current_version='8', target_version='9')
    assert value['annotation_type'] == 'chromatin state'
