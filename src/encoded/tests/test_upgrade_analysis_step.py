import pytest


@pytest.fixture
def base_analysis_step(testapp, software_version):
    item = {
        'name': 'lrna-pe-star-alignment-step-v-2-0',
        'title': 'Long RNA-seq STAR paired-ended alignment step v2.0',
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
        'aliases': ["dnanexus:align-star-se-v-2"],
        'uuid': '8eda9dfa-b9f1-4d58-9e80-535a5e4aaab1',
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
    assert value['title'] == 'Long RNA-seq STAR single-ended alignment step'
    assert value['step_label'] == 'deleted-lrna-se-star-alignment-step'
    assert 'encode:deleted-lrna-se-star-alignment-step-v-2' in value['aliases']
    assert value['major_version'] == 2
