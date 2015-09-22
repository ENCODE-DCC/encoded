import pytest


@pytest.fixture
def file_exp(lab, award, testapp, experiment):
    item = {
        'lab': lab['uuid'],
        'award': award['uuid'],
        'assay_term_name': 'RAMPAGE',
        'assay_term_id': 'OBI:0001864',
        'biosample_term_id': 'NTR:000012',
        'biosample_term_name': 'Some body part',
        'possible_controls': [experiment['uuid']],
        'status': 'released'
        }
    return testapp.post_json('/experiment', item, status=201).json['@graph'][0]


@pytest.fixture
def file_rep(replicate, file_exp, testapp):
    item = {
        'experiment': file_exp['uuid'],
        'biological_replicate_number': 1,
        'technical_replicate_number': 1
        }
    return testapp.post_json('/replicate', item, status=201).json['@graph'][0]


@pytest.fixture
def file_exp2(lab, award, testapp):
    item = {
        'lab': lab['uuid'],
        'award': award['uuid'],
        'assay_term_name': 'RAMPAGE',
        'assay_term_id': 'OBI:0001864',
        'biosample_term_id': 'NTR:000013',
        'biosample_term_name': 'Some other body part',
        'status': 'released'
        }
    return testapp.post_json('/experiment', item, status=201).json['@graph'][0]


@pytest.fixture
def file_rep2(replicate, file_exp2, testapp):
    item = {
        'experiment': file_exp2['uuid'],
        'biological_replicate_number': 1,
        'technical_replicate_number': 1
        }
    return testapp.post_json('/replicate', item, status=201).json['@graph'][0]


@pytest.fixture
def file2(file_exp2, award, lab, file_rep2, testapp):
    item = {
        'dataset': file_exp2['uuid'],
        'replicate': file_rep2['uuid'],
        'file_format': 'fastq',
        'md5sum': '100d8c998f00b204e9800998ecf8427e',
        'output_type': 'raw data',
        'award': award['uuid'],
        'lab': lab['uuid'],
        'status': 'released'
    }
    return testapp.post_json('/file', item, status=201).json['@graph'][0]


@pytest.fixture
def file1(file_exp, award, lab, file_rep, file2, testapp):
    item = {
        'dataset': file_exp['uuid'],
        'replicate': file_rep['uuid'],
        'file_format': 'fastq',
        'md5sum': '100d8cd98f00b204e9800998ecf8427e',
        'output_type': 'reads',
        'award': award['uuid'],
        'lab': lab['uuid'],
        'status': 'released',
        'controlled_by': [file2['uuid']]
    }
    return testapp.post_json('/file', item, status=201).json['@graph'][0]


@pytest.fixture
def file3(file_exp, award, lab, file_rep, testapp):
    item = {
        'dataset': file_exp['uuid'],
        'replicate': file_rep['uuid'],
        'file_format': 'fastq',
        'md5sum': '100d8c998f11b204e9800998ecf8427e',
        'output_type': 'reads',
        'award': award['uuid'],
        'lab': lab['uuid'],
        'status': 'released'
    }
    return testapp.post_json('/file', item, status=201).json['@graph'][0]


@pytest.fixture
def file4(file_exp2, award, lab, file_rep2, testapp):
    item = {
        'dataset': file_exp2['uuid'],
        'replicate': file_rep2['uuid'],
        'file_format': 'fastq',
        'md5sum': '100d8c998f00b204e9800908ecf8428c',
        'output_type': 'reads',
        'award': award['uuid'],
        'lab': lab['uuid'],
        'status': 'released'
    }
    return testapp.post_json('/file', item, status=201).json['@graph'][0]

@pytest.fixture
def encode_lab(testapp):
    item = {
        'name': 'encode-processing-pipeline',
        'title': 'ENCODE Processing Pipeline',
        'status': 'current'
        }
    return testapp.post_json('/lab', item, status=201).json['@graph'][0]

@pytest.fixture
def file5(file_exp2, award, encode_lab, testapp):
    item = {
        'dataset': file_exp2['uuid'],
        'file_format': 'bam',
        'file_size': 3,
        'md5sum': '100d8c998f00b204e9800998ecf8428z',
        'output_type': 'alignments',
        'award': award['uuid'],
        'lab': encode_lab['uuid'],
        'status': 'released'
    }
    return testapp.post_json('/file', item, status=201).json['@graph'][0]

@pytest.fixture
def file6(file_exp2, award, encode_lab, testapp, analysis_step_run_bam):
    item = {
        'dataset': file_exp2['uuid'],
        'file_format': 'bam',
        'file_size': 3,
        'md5sum': '100d8c998f00b204e9800998ecf8428b',
        'output_type': 'alignments',
        'award': award['uuid'],
        'lab': encode_lab['uuid'],
        'status': 'released',
        'step_run': analysis_step_run_bam['uuid']
    }
    return testapp.post_json('/file', item, status=201).json['@graph'][0]

@pytest.fixture
def bam_quality_metric(testapp, analysis_step_run_bam, file6):

    item = {
        'step_run': analysis_step_run_bam['@id'],
        'quality_metric_of':[file6['@id']],
        'uniqueMappedCount':1000
    }

    return testapp.post_json('/edwbamstats_quality_metric', item).json['@graph'][0]

@pytest.fixture
def analysis_step_bam(testapp):
    item = {
        'name': 'bamqc',
        'title': 'bamqc',
        'input_file_types': ['reads'],
        'analysis_step_types': ['QA calculation']
    }
    return testapp.post_json('/analysis_step', item).json['@graph'][0]

@pytest.fixture
def pipeline_bam(testapp, lab, award, analysis_step_bam ):
    item = {
        'award': award['uuid'],
        'lab': lab['uuid'],
        'title': "ChIP-seq of histone modifications",
        'analysis_steps': [analysis_step_bam['@id']]
    }
    return testapp.post_json('/pipeline', item).json['@graph'][0]

@pytest.fixture
def analysis_step_version_bam(testapp, analysis_step_bam, software_version):
    item = {
        'analysis_step': analysis_step_bam['@id'],
        'software_versions': [
            software_version['@id'],
        ],
    }
    return testapp.post_json('/analysis_step_version', item).json['@graph'][0]


@pytest.fixture
def analysis_step_run_bam(testapp, analysis_step_version_bam):
    item = {
        'analysis_step_version': analysis_step_version_bam['@id'],
        'status': 'finished',
    }
    return testapp.post_json('/analysis_step_run', item).json['@graph'][0]


def test_audit_paired_with(testapp, file1):
    testapp.patch_json(file1['@id'], {'paired_end': '1'})
    res = testapp.get(file1['@id'] + '@@index-data')
    errors = res.json['audit']
    errors_list = []
    for error_type in errors:
        errors_list.extend(errors[error_type])
    assert any(error['category'] == 'missing paired_with' for error in errors_list)


def test_audit_mismatched_paired_with(testapp, file1, file4):
    testapp.patch_json(file1['@id'], {'paired_end': '2', 'paired_with': file4['uuid']})
    res = testapp.get(file1['@id'] + '@@index-data')
    errors = res.json['audit']
    errors_list = []
    for error_type in errors:
        errors_list.extend(errors[error_type])
    assert any(error['category'] == 'mismatched paired_with' for error in errors_list)


def test_audit_file_size(testapp, file1):
    res = testapp.get(file1['@id'] + '@@index-data')
    errors = res.json['audit']
    errors_list = []
    for error_type in errors:
        errors_list.extend(errors[error_type])
    assert any(error['category'] == 'missing file_size' for error in errors_list)


def test_audit_read_length(testapp, file1):
    res = testapp.get(file1['@id'] + '@@index-data')
    errors = res.json['audit']
    errors_list = []
    for error_type in errors:
        errors_list.extend(errors[error_type])
    assert any(error['category'] == 'missing read_length' for error in errors_list)


def test_audit_file_missing_controlled_by(testapp, file3):
    res = testapp.get(file3['@id'] + '@@index-data')
    errors = res.json['audit']
    errors_list = []
    for error_type in errors:
        errors_list.extend(errors[error_type])
    assert any(error['category'] == 'missing controlled_by' for error in errors_list)


def test_audit_file_mismatched_controlled_by(testapp, file1):
    res = testapp.get(file1['@id'] + '@@index-data')
    errors = res.json['audit']
    errors_list = []
    for error_type in errors:
        errors_list.extend(errors[error_type])
    assert any(error['category'] == 'mismatched controlled_by' for error in errors_list)


def test_audit_file_replicate_match(testapp, file1, file_rep2):
    testapp.patch_json(file1['@id'], {'replicate': file_rep2['uuid']})
    res = testapp.get(file1['@id'] + '@@index-data')
    errors = res.json['audit']
    errors_list = []
    for error_type in errors:
        errors_list.extend(errors[error_type])
    assert any(error['category'] == 'mismatched replicate' for error in errors_list)


def test_audit_file_paired_ended_run_type1(testapp, file2, file_rep2):
    testapp.patch_json(file2['@id'] + '?validate=false', {'run_type': 'paired-ended', 'output_type': 'reads', 'file_size': 23498234})
    res = testapp.get(file2['@id'] + '@@index-data')
    errors = res.json['audit']
    errors_list = []
    for error_type in errors:
        errors_list.extend(errors[error_type])
    assert any(error['category'] == 'missing paired_end' for error in errors_list)


def test_audit_file_paired_ended_run_type2(testapp, file2, file_rep2):
    testapp.patch_json(file2['@id'] + '?validate=false', {'run_type': 'paired-ended', 'output_type': 'reads', 'file_size': 23498234, 'paired_end': 1})
    res = testapp.get(file2['@id'] + '@@index-data')
    errors = res.json['audit']
    errors_list = []
    for error_type in errors:
        errors_list.extend(errors[error_type])
    assert any(error['category'] == 'missing mate pair' for error in errors_list)


def test_missing_quality_metrics(testapp, file5):
    res = testapp.get(file5['@id'] + '@@index-data')
    errors = res.json['audit']
    errors_list = []
    for error_type in errors:
        errors_list.extend(errors[error_type])
    assert any(error['category'] == 'missing quality metrics' for error in errors_list)


def test_audit_file_read_depth(testapp, file6, bam_quality_metric, analysis_step_run_bam, analysis_step_version_bam, analysis_step_bam, pipeline_bam):
    res = testapp.get(file6['@id'] + '@@index-data')
    errors = res.json['audit']
    errors_list = []
    for error_type in errors:       
        errors_list.extend(errors[error_type])
    assert any(error['category'] == 'not sufficient read depth' for error in errors_list)
