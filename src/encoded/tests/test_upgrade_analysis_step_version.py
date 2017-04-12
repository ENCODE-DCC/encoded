import pytest


@pytest.fixture
def analysis_step_version_2(testapp, software_version, analysis_step):
    item = {
        'title': 'base analysis step version 1-1',
        'analysis_step': analysis_step['@id'],
        'version': 2,
        'software_versions': [
            software_version['@id'],
        ],
    }
    return item

def test_analysis_step_version_2_3(registry, upgrader, analysis_step_version_2):
    # Make sure version is now a string and not an integer
    value = upgrader.upgrade('analysis_step_version', analysis_step_version_2, current_version='2', target_version='3', registry=registry)
    assert isinstance(value['version'], str)
