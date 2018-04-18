import pytest

'''
This upgrade test is no longer need as the upgrade was also removed. The test and upgrade will remain
in the code for posterity but they both are no longer valid after versionof: was removed as a valid 
namespace according to http://redmine.encodedcc.org/issues/4748

@pytest.fixture
def analysis_step_version_with_alias(testapp, analysis_step, software_version):
    item = {
        'aliases': ['versionof:' + analysis_step['name']],
        'analysis_step': analysis_step['@id'],
        'software_versions': [
            software_version['@id'],
        ],
    }
    return testapp.post_json('/analysis_step_version', item).json['@graph'][0]


@pytest.fixture
def analysis_step_run_1(analysis_step):
    item = {
        'analysis_step': analysis_step['uuid'],
        'status': 'finished',
        'workflow_run': 'does not exist',
    }
    return item


def test_analysis_step_run_1_2(registry, upgrader, analysis_step_run_1, analysis_step_version_with_alias, threadlocals):
    value = upgrader.upgrade('analysis_step_run', analysis_step_run_1, current_version='1', target_version='2', registry=registry)
    assert value['analysis_step_version'] == analysis_step_version_with_alias['uuid']
    assert 'analysis_step' not in value
    assert 'workflows_run' not in value
'''


@pytest.fixture
def analysis_step_run_3(analysis_step, analysis_step_version):
    item = {
        'analysis_step_version': analysis_step_version['uuid'],
        'status': 'finished'
    }
    return item


@pytest.fixture
def analysis_step_run_4(analysis_step, analysis_step_version):
    item = {
        'analysis_step_version': analysis_step_version['uuid'],
        'status': 'virtual'
    }
    return item


def test_analysis_step_run_3_4(registry, upgrader, analysis_step_run_3):
    value = upgrader.upgrade('analysis_step_run', analysis_step_run_3,
                             current_version='3', target_version='4', registry=registry)
    assert value['schema_version'] == '4'
    assert value['status'] == 'released'


def test_analysis_step_run_4_5(registry, upgrader, analysis_step_run_4):
    assert analysis_step_run_4['status'] == 'virtual'
    value = upgrader.upgrade('analysis_step_run', analysis_step_run_4,
                             current_version='4', target_version='5', registry=registry)
    assert value['schema_version'] == '5'
    assert value['status'] == 'released'
