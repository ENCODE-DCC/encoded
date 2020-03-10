import pytest
from ..constants import *



@pytest.fixture
def software_version(testapp, software):
    item = {
        'version': 'v0.11.2',
        'software': software['@id'],
    }
    return testapp.post_json('/software_version', item).json['@graph'][0]


@pytest.fixture
def analysis_step(testapp):
    item = {
        'step_label': 'fastqc-step',
        'title': 'fastqc step',
        'major_version': 1,
        'input_file_types': ['reads'],
        'analysis_step_types': ['QA calculation'],

    }
    return testapp.post_json('/analysis_step', item).json['@graph'][0]


@pytest.fixture
def analysis_step_version(testapp, analysis_step, software_version):
    item = {
        'analysis_step': analysis_step['@id'],
        'minor_version': 0,
        'software_versions': [
            software_version['@id'],
        ],
    }
    return testapp.post_json('/analysis_step_version', item).json['@graph'][0]


@pytest.fixture
def analysis_step_run(testapp, analysis_step_version):
    item = {
        'analysis_step_version': analysis_step_version['@id'],
        'status': 'released',
    }
    return testapp.post_json('/analysis_step_run', item).json['@graph'][0]

@pytest.fixture
def analysis_step_bam(testapp):
    item = {
        'step_label': 'bamqc-step',
        'title': 'bamqc step',
        'input_file_types': ['reads'],
        'analysis_step_types': ['QA calculation'],
        'major_version': 2
    }
    return testapp.post_json('/analysis_step', item).json['@graph'][0]


@pytest.fixture
def analysis_step_version_bam(testapp, analysis_step_bam, software_version):
    item = {
        'analysis_step': analysis_step_bam['@id'],
        'minor_version': 0,
        'software_versions': [
            software_version['@id'],
        ],
    }
    return testapp.post_json('/analysis_step_version', item).json['@graph'][0]

@pytest.fixture
def analysis_step_run_bam(testapp, analysis_step_version_bam):
    item = {
        'analysis_step_version': analysis_step_version_bam['@id'],
        'status': 'released',
        'aliases': ['modern:chip-seq-bwa-alignment-step-run-v-1-released']
    }
    return testapp.post_json('/analysis_step_run', item).json['@graph'][0]

@pytest.fixture
def analysis_step_bam(testapp):
    item = {
        'step_label': 'bamqc-step',
        'title': 'bamqc step',
        'major_version': 1,
        'input_file_types': ['reads'],
        'analysis_step_types': ['QA calculation']
    }
    return testapp.post_json('/analysis_step', item).json['@graph'][0]

