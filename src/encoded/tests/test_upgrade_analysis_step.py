import pytest


@pytest.fixture
def base_analysis_step(testapp, software_version):
    item = {
        'name': 'base_analysis_step_v_1',
        'title': 'base_analysis_step_v_1 title',
        'analysis_step_types': ['alignments'],
        'input_file_types': ['reads'],
        'software_versions': [
            software_version['@id'],
        ],
    }
    return item


@pytest.fixture
def analysis_step_1(base_analysis_step):

    item = base_analysis_step.copy()
    item.update({
        'schema_version': '2',
        'output_file_types': ['signal of multi-mapped reads']
    })
    return item

@pytest.fixture
def analysis_step_3(base_analysis_step):
    item = base_analysis_step.copy()
    item.update({
        'schema_version': '3',
        'analysis_step_types': ['alignment', 'alignment'],
        'input_file_types': ['reads', 'reads'],
        'output_file_types': ['transcriptome alignments', 'transcriptome alignments']
    })
    return item


def test_analysis_step_run_2_3(registry, upgrader, analysis_step_1, threadlocals):
    value = upgrader.upgrade('analysis_step', analysis_step_1, current_version='2', target_version='3', registry=registry)
    assert 'signal of all reads' in value['output_file_types']
    assert 'signal of multi-mapped reads' not in value['output_file_types']


def test_analysis_step_unique_array(upgrader, analysis_step_3):
    value = upgrader.upgrade('analysis_step', analysis_step_3, current_version='3', target_version='4')
    assert value['schema_version'] == '4'
    assert len(value['analysis_step_types']) == len(set(value['analysis_step_types']))
    assert len(value['input_file_types']) == len(set(value['input_file_types']))
    assert len(value['output_file_types']) == len(set(value['output_file_types']))
