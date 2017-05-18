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
        ]
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


@pytest.fixture
def analysis_step_5(base_analysis_step):
    item = base_analysis_step.copy()
    item.update({
        'schema_version': '5',
        'uuid': '9476dd4e-24b9-4e8d-9317-4e57edffac8f',
        'status': 'in progress',
        'analysis_step_types': ['pooling', 'signal generation', 'file format conversion', 'quantification'],
        'input_file_types': ['alignments'],
        'output_file_types': ['methylation state at CHG', 'methylation state at CHH', 'raw signal', 'methylation state at CpG']
    })
    return item

def test_analysis_step_2_3(registry, upgrader, analysis_step_1, threadlocals):
    value = upgrader.upgrade('analysis_step', analysis_step_1, current_version='2', target_version='3', registry=registry)
    assert 'signal of all reads' in value['output_file_types']
    assert 'signal of multi-mapped reads' not in value['output_file_types']


def test_analysis_step_unique_array(upgrader, analysis_step_3):
    value = upgrader.upgrade('analysis_step', analysis_step_3, current_version='3', target_version='4')
    assert value['schema_version'] == '4'
    assert len(value['analysis_step_types']) == len(set(value['analysis_step_types']))
    assert len(value['input_file_types']) == len(set(value['input_file_types']))
    assert len(value['output_file_types']) == len(set(value['output_file_types']))


def test_analysis_step_5_6(upgrader, analysis_step_5):
    value = upgrader.upgrade('analysis_step', analysis_step_5, current_version='5', target_version='6')
    assert value['schema_version'] == '6'
    assert value['major_version'] == 1
    assert value['status'] == 'released'
