import pytest


@pytest.fixture
def analysis_step_version_3(testapp, analysis_step, software_version):
    item = {
        'schema_version': '3',
        'version': 1,
        'analysis_step': analysis_step['@id'],
        'software_versions': [
            software_version['@id'],
        ],
    }
    return item

def test_analysis_step_version_3_4(upgrader, analysis_step_version_3):
    # http://redmine.encodedcc.org/issues/4987
    # Allow minor versions to start from 0, was previously defaulted to 1. The first version of a step should start as #.0 not #.1
    value = upgrader.upgrade('analysis_step_version', analysis_step_version_3, current_version='3', target_version='4')
    assert value['schema_version'] == '4'
    assert 'version' not in value
    assert 'minor_version' in value
    assert value['minor_version'] == 0
