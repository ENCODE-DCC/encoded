import pytest


@pytest.fixture
def analysis_step_run_with_no_status(analysis_step_version):
    return {
        'analysis_step_version': analysis_step_version['@id']
    }


@pytest.fixture
def analysis_step_run(testapp, analysis_step_version):
    item = {
        'analysis_step_version': analysis_step_version['@id'],
        'status': 'released',
    }
    return testapp.post_json('/analysis_step_run', item).json['@graph'][0]


@pytest.fixture
def step_run(testapp, lab, award):
    software = {
        'name': 'do-thing',
        'description': 'It does the thing',
        'title': 'THING_DOER',
        'award': award['@id'],
        'lab': lab['@id']
    }
    sw = testapp.post_json('/software', software, status=201).json['@graph'][0]

    software_version = {
        'version': '0.1',
        'software': sw['@id']
    }
    swv = testapp.post_json('/software-versions', software_version, status=201).json['@graph'][0]

    analysis_step = {
        'step_label': 'do-thing-step',
        'major_version': 1,
        'title': 'Do The Thing Step By Step',
        'analysis_step_types': ["QA calculation"],
        'input_file_types':  ['raw data']
    }
    astep = testapp.post_json('/analysis-steps', analysis_step, status=201).json['@graph'][0]

    as_version = {
        'software_versions': [swv['@id']],
        'analysis_step':  astep['@id'],
        'minor_version': 1
    }
    asv = testapp.post_json('/analysis-step-versions', as_version, status=201).json['@graph'][0]

    step_run = {
        'analysis_step_version': asv['@id'],
        'status': "released"
    }
    return testapp.post_json('/analysis-step-runs', step_run, status=201).json['@graph'][0]


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


@pytest.fixture
def analysis_step_run_bam(testapp, analysis_step_version_bam):
    item = {
        'analysis_step_version': analysis_step_version_bam['@id'],
        'status': 'released',
        'aliases': ['modern:chip-seq-bwa-alignment-step-run-v-1-released']
    }
    return testapp.post_json('/analysis_step_run', item).json['@graph'][0]


@pytest.fixture
def analysis_step_run_chip_encode4(testapp, analysis_step_version_chip_encode4):
    item = {
        'analysis_step_version': analysis_step_version_chip_encode4['@id'],
        'status': 'released'
    }
    return testapp.post_json('/analysis_step_run', item).json['@graph'][0]


@pytest.fixture
def analysis_step_run_dnase_encode4(testapp, analysis_step_version_dnase_encode4):
    item = {
        'analysis_step_version': analysis_step_version_dnase_encode4['@id'],
        'status': 'released'
    }
    return testapp.post_json('/analysis_step_run', item).json['@graph'][0]


@pytest.fixture
def analysis_step_run_atac_encode4_alignment(testapp, analysis_step_version_atac_encode4_alignment):
    item = {
        'analysis_step_version': analysis_step_version_atac_encode4_alignment['@id'],
        'status': 'released'
    }
    return testapp.post_json('/analysis_step_run', item).json['@graph'][0]


@pytest.fixture
def analysis_step_run_atac_encode4_partition_concordance(testapp,
                    analysis_step_version_atac_encode4_partition_concordance):
    item = {
        'analysis_step_version': analysis_step_version_atac_encode4_partition_concordance['@id'],
        'status': 'released'
    }
    return testapp.post_json('/analysis_step_run', item).json['@graph'][0]


@pytest.fixture
def analysis_step_run_atac_encode4_pseudoreplicate_concordance(testapp,
                    analysis_step_version_atac_encode4_pseudoreplicate_concordance):
    item = {
        'analysis_step_version': analysis_step_version_atac_encode4_pseudoreplicate_concordance['@id'],
        'status': 'released'
    }
    return testapp.post_json('/analysis_step_run', item).json['@graph'][0]


@pytest.fixture
def analysis_step_run_chia_alignment(testapp, analysis_step_version_chia_alignment):
    item = {
        'analysis_step_version': analysis_step_version_chia_alignment['@id'],
        'status': 'released'
    }
    return testapp.post_json('/analysis_step_run', item).json['@graph'][0]


@pytest.fixture
def analysis_step_run_chia_peak_calling(testapp, analysis_step_version_chia_peak_calling):
    item = {
        'analysis_step_version': analysis_step_version_chia_peak_calling['@id'],
        'status': 'released'
    }
    return testapp.post_json('/analysis_step_run', item).json['@graph'][0]


@pytest.fixture
def analysis_step_run_chia_interaction_calling(testapp, analysis_step_version_chia_interaction_calling):
    item = {
        'analysis_step_version': analysis_step_version_chia_interaction_calling['@id'],
        'status': 'released'
    }
    return testapp.post_json('/analysis_step_run', item).json['@graph'][0]
