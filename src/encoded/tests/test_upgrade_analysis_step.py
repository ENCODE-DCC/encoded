import pytest


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


def test_analysis_step_6_7(upgrader, analysis_step_6):
    value = upgrader.upgrade('analysis_step', analysis_step_6, current_version='6', target_version='7')
    assert value['schema_version'] == '7'
    assert 'candidate regulatory elements' not in value['input_file_types']
    assert 'candidate regulatory elements' not in value['output_file_types']
    assert 'candidate Cis-Regulatory Elements' in value['input_file_types']
    assert 'candidate Cis-Regulatory Elements' in value['output_file_types']


def test_analysis_step_7_8(upgrader, analysis_step_7):
    expectation = sorted([
        'peaks',
        'optimal IDR thresholded peaks',
        'conservative IDR thresholded peaks',
        'pseudoreplicated IDR thresholded peaks'
    ])
    value = upgrader.upgrade(
        'analysis_step',
        analysis_step_7,
        current_version='7',
        target_version='8'
    )
    assert value['schema_version'] == '8'
    assert sorted(value['input_file_types']) == expectation
    assert sorted(value['output_file_types']) == expectation


def test_analysis_step_8_9(upgrader, analysis_step_8):
    value = upgrader.upgrade('analysis_step', analysis_step_8, current_version='8', target_version='9')
    assert value['schema_version'] == '9'
    assert 'representative dnase hypersensitivity sites' not in value['input_file_types']
    assert 'representative dnase hypersensitivity sites' not in value['output_file_types']
    assert 'representative DNase hypersensitivity sites (rDHSs)' in value['input_file_types']
    assert 'representative DNase hypersensitivity sites (rDHSs)' in value['output_file_types']


def test_analysis_step_9_10(upgrader, analysis_step_9):
    value = upgrader.upgrade('analysis_step', analysis_step_9, current_version='9', target_version='10')
    assert value['schema_version'] == '10'
    assert 'spike-in sequence' not in value['input_file_types']
    assert 'spike-in sequence' not in value['output_file_types']
    assert 'spike-ins' in value['input_file_types']
    assert 'spike-ins' in value['output_file_types']
