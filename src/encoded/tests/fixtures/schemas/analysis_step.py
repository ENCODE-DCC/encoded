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


@pytest.fixture
def analysis_step_6(base_analysis_step):
    item = base_analysis_step.copy()
    item.update({
        'schema_version': '6',
        'input_file_types': ['alignments', 'candidate regulatory elements'],
        'output_file_types': ['raw signal', 'candidate regulatory elements']
    })
    return item


@pytest.fixture
def analysis_step_7(base_analysis_step):
    item = base_analysis_step.copy()
    item.update({
        'input_file_types': [
            'peaks',
            'optimal idr thresholded peaks',
            'conservative idr thresholded peaks',
            'pseudoreplicated idr thresholded peaks'
        ],
        'output_file_types': [
            'peaks',
            'optimal idr thresholded peaks',
            'conservative idr thresholded peaks',
            'pseudoreplicated idr thresholded peaks'
        ],
    })
    return item


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
def analysis_step_8(testapp):
    item = {
        'schema_version': '8',
        'step_label': 'rdhs-step',
        'title': 'rdhs step',
        'major_version': 1,
        'analysis_step_types': ['QA calculation'],
        'input_file_types': ['representative dnase hypersensitivity sites'],
        'output_file_types': ['representative dnase hypersensitivity sites']
    }
    return item

@pytest.fixture
def analysis_step_chip_encode4(testapp):
    item = {
        'step_label': 'chip-seq-star-align-step',
        'title': 'ChIP seq alignment step',
        'input_file_types': ['reads'],
        'analysis_step_types': ['QA calculation', 'alignment'],
        'major_version': 1
    }
    return testapp.post_json('/analysis_step', item).json['@graph'][0]
