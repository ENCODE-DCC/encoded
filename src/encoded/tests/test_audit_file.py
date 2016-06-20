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
        'status': 'released',
        'date_released': '2016-01-01'
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
        'status': 'released',
        'date_released': '2016-01-01'
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
def file_rep1_2(replicate, file_exp, testapp):
    item = {
        'experiment': file_exp['uuid'],
        'biological_replicate_number': 2,
        'technical_replicate_number': 1
        }
    return testapp.post_json('/replicate', item, status=201).json['@graph'][0]


@pytest.fixture
def file1_2(file_exp, award, lab, file_rep1_2, testapp):
    item = {
        'dataset': file_exp['uuid'],
        'replicate': file_rep1_2['uuid'],
        'file_format': 'fastq',
        'md5sum': '100d8c998f00b204e9r800998ecf8427e',
        'output_type': 'raw data',
        'award': award['uuid'],
        'lab': lab['uuid'],
        'status': 'released'
    }
    return testapp.post_json('/file', item, status=201).json['@graph'][0]


@pytest.fixture
def file2(file_exp2, award, lab, file_rep2, platform1, testapp):
    item = {
        'dataset': file_exp2['uuid'],
        'replicate': file_rep2['uuid'],
        'file_format': 'fastq',
        'md5sum': '100d8c998f00b204e9800998ecf8427e',
        'output_type': 'raw data',
        'platform': platform1['uuid'],
        'award': award['uuid'],
        'lab': lab['uuid'],
        'status': 'released'
    }
    return testapp.post_json('/file', item, status=201).json['@graph'][0]


@pytest.fixture
def file1(file_exp, award, lab, file_rep, file2, platform1, testapp):
    item = {
        'dataset': file_exp['uuid'],
        'replicate': file_rep['uuid'],
        'file_format': 'fastq',
        'md5sum': '100d8cd98f00b204e9800998ecf8427e',
        'output_type': 'reads',
        'platform': platform1['uuid'],
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
def file7(file_exp2, award, encode_lab, testapp, analysis_step_run_bam):
    item = {
        'dataset': file_exp2['uuid'],
        'file_format': 'tsv',
        'file_size': 3,
        'md5sum': '100d8c998f00b2204e9800998ecf8428b',
        'output_type': 'gene quantifications',
        'award': award['uuid'],
        'lab': encode_lab['uuid'],
        'status': 'released',
        'step_run': analysis_step_run_bam['uuid']
    }
    return testapp.post_json('/file', item, status=201).json['@graph'][0]


@pytest.fixture
def platform1(testapp):
    item = {
        'term_id': 'OBI:0002001',
        'term_name': 'HiSeq2000'
    }
    return testapp.post_json('/platform', item).json['@graph'][0]


@pytest.fixture
def platform2(testapp):
    item = {
        'term_id': 'OBI:0002049',
        'term_name': 'HiSeq4000'
    }
    return testapp.post_json('/platform', item).json['@graph'][0]


@pytest.fixture
def chipseq_bam_quality_metric(testapp, analysis_step_run_bam, file6, lab, award):
    item = {
        'step_run': analysis_step_run_bam['@id'],
        'award': award['@id'],
        'lab': lab['@id'],
        'quality_metric_of': [file6['@id']],
        'total': 20000000
    }

    return testapp.post_json('/samtools_flagstats_quality_metric', item).json['@graph'][0]


@pytest.fixture
def chipseq_bam_quality_metric_2(testapp, analysis_step_run_bam, file7, lab, award):
    item = {
        'step_run': analysis_step_run_bam['@id'],
        'award': award['@id'],
        'lab': lab['@id'],
        'quality_metric_of': [file7['@id']],
        'total': 20000000
    }

    return testapp.post_json('/samtools_flagstats_quality_metric', item).json['@graph'][0]


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
def pipeline_short_rna(testapp, lab, award, analysis_step_bam):
    item = {
        'award': award['uuid'],
        'lab': lab['uuid'],
        'title': "Small RNA-seq single-end pipeline",
        'analysis_steps': [analysis_step_bam['@id']]
    }
    return testapp.post_json('/pipeline', item).json['@graph'][0]


def test_audit_file_paired_with(testapp, file1):
    testapp.patch_json(file1['@id'], {'paired_end': '1'})
    res = testapp.get(file1['@id'] + '@@index-data')
    errors = res.json['audit']
    errors_list = []
    for error_type in errors:
        errors_list.extend(errors[error_type])
    assert any(error['category'] == 'missing paired_with' for error in errors_list)


def test_audit_file_mismatched_paired_with(testapp, file1, file4):
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


def test_audit_read_length_zero(testapp, file1):
    testapp.patch_json(file1['@id'], {'read_length': 0})
    res = testapp.get(file1['@id'] + '@@index-data')
    errors = res.json['audit']
    errors_list = []
    for error_type in errors:
        errors_list.extend(errors[error_type])
    assert any(error['category'] == 'missing read_length' for error in errors_list)


def test_audit_run_type(testapp, file1):
    res = testapp.get(file1['@id'] + '@@index-data')
    errors = res.json['audit']
    errors_list = []
    for error_type in errors:
        errors_list.extend(errors[error_type])
    assert any(error['category'] == 'missing run_type' for error in errors_list)


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
    assert any(error['category'] == 'mismatched control' for error in errors_list)


def test_audit_file_inconsistent_controlled_by(testapp, file1,
                                               file2, file3,
                                               file_rep1_2,
                                               file_rep2):
    testapp.patch_json(file1['@id'], {'replicate': file_rep2['@id']})
    testapp.patch_json(file3['@id'], {'replicate': file_rep1_2['@id']})
    testapp.patch_json(file1['@id'], {'controlled_by': [file2['@id'], file3['@id']]})

    res = testapp.get(file1['@id'] + '@@index-data')
    errors = res.json['audit']
    errors_list = []
    for error_type in errors:
        errors_list.extend(errors[error_type])
    assert any(error['category'] == 'inconsistent controlled_by replicates' for
                                    error in errors_list)


def test_audit_file_missing_paired_controlled_by(testapp, file1,
                                                 file2, file3,
                                                 file_rep2):
    testapp.patch_json(file3['@id'], {'replicate': file_rep2['@id'],
                                      'paired_with': file2['@id'],
                                      'run_type': 'paired-ended',
                                      'paired_end': '2'})
    testapp.patch_json(file2['@id'], {'replicate': file_rep2['@id'],
                                      'run_type': 'paired-ended',
                                      'paired_end': '1'})
    testapp.patch_json(file1['@id'], {'controlled_by': [file2['@id']]})

    res = testapp.get(file1['@id'] + '@@index-data')
    errors = res.json['audit']
    errors_list = []
    for error_type in errors:
        errors_list.extend(errors[error_type])
    assert any(error['category'] == 'missing paired_with in controlled_by' for
                                    error in errors_list)


def test_audit_file_mismatched_platform_controlled_by(testapp, file1, file2, file_exp,
                                                      file_exp2, platform2):
    testapp.patch_json(file_exp['@id'], {'possible_controls': [file_exp2['@id']],
                                         'biosample_term_id': 'NTR:000013'})
    testapp.patch_json(file2['@id'], {'platform': platform2['@id']})
    res = testapp.get(file1['@id'] + '@@index-data')
    errors = res.json['audit']
    errors_list = []
    for error_type in errors:
        errors_list.extend(errors[error_type])
    assert any(error['category'] == 'mismatched control platform' for error in errors_list)


def test_audit_file_replicate_match(testapp, file1, file_rep2):
    testapp.patch_json(file1['@id'], {'replicate': file_rep2['uuid']})
    res = testapp.get(file1['@id'] + '@@index-data')
    errors = res.json['audit']
    errors_list = []
    for error_type in errors:
        errors_list.extend(errors[error_type])
    assert any(error['category'] == 'mismatched replicate' for error in errors_list)


def test_audit_file_paired_ended_run_type1(testapp, file2, file_rep2):
    testapp.patch_json(file2['@id'] + '?validate=false', {'run_type': 'paired-ended',
                                                          'output_type': 'reads',
                                                          'file_size': 23498234})
    res = testapp.get(file2['@id'] + '@@index-data')
    errors = res.json['audit']
    errors_list = []
    for error_type in errors:
        errors_list.extend(errors[error_type])
    assert any(error['category'] == 'missing paired_end' for error in errors_list)


def test_audit_file_paired_ended_run_type2(testapp, file2, file_rep2):
    testapp.patch_json(file2['@id'] + '?validate=false', {'run_type': 'paired-ended',
                                                          'output_type': 'reads',
                                                          'file_size': 23498234,
                                                          'paired_end': 1})
    res = testapp.get(file2['@id'] + '@@index-data')
    errors = res.json['audit']
    errors_list = []
    for error_type in errors:
        errors_list.extend(errors[error_type])
    assert any(error['category'] == 'missing paired_with' for error in errors_list)


def test_audit_file_insufficient_control_read_depth_chip_seq_paired_end(
    testapp,
    file_exp,
    file_exp2,
    file6,
    file2,
    file7,
    file4,
    chipseq_bam_quality_metric,
    chipseq_bam_quality_metric_2,
    analysis_step_run_bam,
    analysis_step_version_bam,
    analysis_step_bam,
    target_H3K27ac,
    target_control,
        pipeline_bam):
    testapp.patch_json(file_exp['@id'], {'target': target_H3K27ac['@id']})
    testapp.patch_json(file_exp2['@id'], {'target': target_control['@id']})
    testapp.patch_json(chipseq_bam_quality_metric['@id'], {'total': 1000})
    testapp.patch_json(chipseq_bam_quality_metric_2['@id'], {'total': 1000})
    testapp.patch_json(file2['@id'], {'dataset': file_exp2['@id']})
    testapp.patch_json(file7['@id'], {'dataset': file_exp2['@id'],
                                      'file_format': 'bam',
                                      'output_type': 'alignments',
                                      'assembly': 'hg19',
                                      'derived_from': [file2['@id']]})

    testapp.patch_json(file4['@id'], {'dataset': file_exp['@id'],
                                      'controlled_by': [file2['@id']]})
    testapp.patch_json(file6['@id'], {'dataset': file_exp['@id'],
                                      'assembly': 'hg19',
                                      'derived_from': [file4['@id']]})
    testapp.patch_json(file4['@id'], {'run_type': 'paired-ended'})
    testapp.patch_json(file2['@id'], {'run_type': 'paired-ended'})
    testapp.patch_json(file7['@id'], {})
    res = testapp.get(file6['@id'] + '@@index-data')
    errors = res.json['audit']
    errors_list = []
    for error_type in errors:
        errors_list.extend(errors[error_type])
    assert any(error['category'] == 'control insufficient read depth' for error in errors_list)


def test_audit_modERN_missing_step_run(testapp, file_exp, file3, award):
    testapp.patch_json(award['@id'], {'rfa': 'modERN'})
    testapp.patch_json(file_exp['@id'], {'assay_term_id': 'OBI:0000716', 'assay_term_name': 'ChIP-seq'})
    testapp.patch_json(file3['@id'], {'dataset': file_exp['@id'], 'file_format': 'bam', 'output_type': 'alignments'})
    res = testapp.get(file3['@id'] + '@@index-data')
    errors = res.json['audit']
    errors_list = []
    for error_type in errors:
        errors_list.extend(errors[error_type])
    assert any(error['category'] == 'missing step_run' for error in errors_list)


def test_audit_modERN_missing_derived_from(testapp, file_exp, file3, award, analysis_step_version_bam, analysis_step_bam, analysis_step_run_bam):
    testapp.patch_json(award['@id'], {'rfa': 'modERN'})
    testapp.patch_json(file_exp['@id'], {'assay_term_id': 'OBI:0000716', 'assay_term_name': 'ChIP-seq'})
    testapp.patch_json(file3['@id'], {'dataset': file_exp['@id'], 'file_format': 'bam', 'output_type': 'alignments', 'step_run': analysis_step_run_bam['@id']})
    res = testapp.get(file3['@id'] + '@@index-data')
    errors = res.json['audit']
    errors_list = []
    for error_type in errors:
        errors_list.extend(errors[error_type])
    assert any(error['category'] == 'missing derived_from' for error in errors_list)


def test_audit_modERN_wrong_step_run(testapp, file_exp, file3, file4, award, analysis_step_version_bam, analysis_step_bam, analysis_step_run_bam):
    testapp.patch_json(award['@id'], {'rfa': 'modERN'})
    testapp.patch_json(file_exp['@id'], {'assay_term_id': 'OBI:0000716', 'assay_term_name': 'ChIP-seq'})
    testapp.patch_json(file3['@id'], {'dataset': file_exp['@id'], 'file_format': 'bed', 'file_format_type': 'narrowPeak', 'output_type': 'peaks', 'step_run': analysis_step_run_bam['@id'], 'derived_from': [file4['@id']]})
    res = testapp.get(file3['@id'] + '@@index-data')
    errors = res.json['audit']
    errors_list = []
    for error_type in errors:
        errors_list.extend(errors[error_type])
    assert any(error['category'] == 'wrong step_run for peaks' for error in errors_list)


def test_audit_modERN_unexpected_step_run(testapp, file_exp, file2, award, analysis_step_run_bam):
    testapp.patch_json(award['@id'], {'rfa': 'modERN'})
    testapp.patch_json(file_exp['@id'], {'assay_term_id': 'OBI:0000716', 'assay_term_name': 'ChIP-seq'})
    testapp.patch_json(file2['@id'], {'dataset': file_exp['@id'], 'step_run': analysis_step_run_bam['@id']})
    res = testapp.get(file2['@id'] + '@@index-data')
    errors = res.json['audit']
    errors_list = []
    for error_type in errors:
        errors_list.extend(errors[error_type])
    assert any(error['category'] == 'unexpected step_run' for error in errors_list)


def test_audit_file_biological_replicate_number_match(testapp,
                                                      file_exp,
                                                      file_rep,
                                                      file1,
                                                      file_rep1_2,
                                                      file1_2):
    testapp.patch_json(file1['@id'], {'derived_from': [file1['@id']]})
    res = testapp.get(file1['@id'] + '@@index-data')
    errors = res.json['audit']
    errors_list = []
    for error_type in errors:
        errors_list.extend(errors[error_type])
    assert all(error['category'] != 'inconsistent biological replicate number'
               for error in errors_list)


def test_audit_file_biological_replicate_number_mismatch(testapp,
                                                         file_exp,
                                                         file_rep,
                                                         file1,
                                                         file_rep1_2,
                                                         file1_2):
    testapp.patch_json(file1['@id'], {'derived_from': [file1_2['@id']]})
    res = testapp.get(file1['@id'] + '@@index-data')
    errors = res.json['audit']
    errors_list = []
    for error_type in errors:
        errors_list.extend(errors[error_type])
    assert any(error['category'] == 'inconsistent biological replicate number'
               for error in errors_list)


def test_audit_file_fastq_assembly(testapp, file4):
    testapp.patch_json(file4['@id'], {'assembly': 'GRCh38'})
    res = testapp.get(file4['@id'] + '@@index-data')
    errors = res.json['audit']
    errors_list = []
    for error_type in errors:
        errors_list.extend(errors[error_type])
    assert any(error['category'] == 'erroneous property'
               for error in errors_list)


def test_audit_file_assembly(testapp, file6, file7):
    testapp.patch_json(file6['@id'], {'assembly': 'GRCh38'})
    testapp.patch_json(file7['@id'], {'derived_from': [file6['@id']],
                                      'assembly': 'hg19'})
    res = testapp.get(file7['@id'] + '@@index-data')
    errors = res.json['audit']
    errors_list = []
    for error_type in errors:
        errors_list.extend(errors[error_type])
    assert any(error['category'] == 'mismatched assembly'
               for error in errors_list)


def test_audit_file_missing_assembly_no_derived(testapp, file6):
    res = testapp.get(file6['@id'] + '@@index-data')
    errors = res.json['audit']
    errors_list = []
    for error_type in errors:
        errors_list.extend(errors[error_type])
    assert any(error['category'] == 'missing assembly'
               for error in errors_list)


def test_audit_file_missing_assembly(testapp, file6, file7):
    testapp.patch_json(file6['@id'], {'assembly': 'GRCh38'})
    testapp.patch_json(file7['@id'], {'derived_from': [file6['@id']]})
    res = testapp.get(file7['@id'] + '@@index-data')
    errors = res.json['audit']
    errors_list = []
    for error_type in errors:
        errors_list.extend(errors[error_type])
    assert any(error['category'] == 'missing assembly'
               for error in errors_list)


def test_audit_file_derived_from_revoked(testapp, file6, file7):
    testapp.patch_json(file6['@id'], {'status': 'revoked'})
    testapp.patch_json(file7['@id'], {'derived_from': [file6['@id']],
                                      'status': 'released'})
    res = testapp.get(file7['@id'] + '@@index-data')
    errors = res.json['audit']
    errors_list = []
    for error_type in errors:
        errors_list.extend(errors[error_type])
    assert any(error['category'] == 'mismatched file status'
               for error in errors_list)


def test_audit_file_derived_from_empty(testapp, file7):
    res = testapp.get(file7['@id'] + '@@index-data')
    errors = res.json['audit']
    errors_list = []
    for error_type in errors:
        errors_list.extend(errors[error_type])
    assert any(error['category'] == 'missing derived_from'
               for error in errors_list)


def test_audit_file_bam_derived_from_no_fastq(testapp, file7, file6):
    testapp.patch_json(file6['@id'], {'derived_from': [file7['@id']],
                                      'status': 'released',
                                      'file_format': 'bam'})
    testapp.patch_json(file7['@id'], {'file_format': 'bam'})
    res = testapp.get(file6['@id'] + '@@index-data')
    errors = res.json['audit']
    errors_list = []
    for error_type in errors:
        errors_list.extend(errors[error_type])
    assert any(error['category'] == 'missing derived_from'
               for error in errors_list)


def test_audit_file_bam_derived_from_different_experiment(testapp, file6, file4, file_exp):
    testapp.patch_json(file4['@id'], {'dataset': file_exp['@id']})
    testapp.patch_json(file6['@id'], {'derived_from': [file4['@id']],
                                      'status': 'released'})
    res = testapp.get(file6['@id'] + '@@index-data')
    errors = res.json['audit']
    errors_list = []
    for error_type in errors:
        errors_list.extend(errors[error_type])
    assert any(error['category'] == 'mismatched derived_from'
               for error in errors_list)
