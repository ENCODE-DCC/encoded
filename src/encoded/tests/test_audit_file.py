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
        'md5sum': '100d8c998f00b204e9800998ecf8428b',
        'output_type': 'gene quantifications',
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
        'quality_metric_of': [file6['@id']],
        'Uniquely mapped reads number': 1000
    }

    return testapp.post_json('/star_quality_metric', item).json['@graph'][0]


@pytest.fixture
def mad_quality_metric(testapp, analysis_step_run_bam, file7):
    item = {
        'step_run': analysis_step_run_bam['@id'],
        'quality_metric_of':[file7['@id']],
        'Spearman correlation':0.2
    }

    return testapp.post_json('/mad_quality_metric', item).json['@graph'][0]

@pytest.fixture
def chipseq_bam_quality_metric(testapp, analysis_step_run_bam, file6):
    item = {
        'step_run': analysis_step_run_bam['@id'],
        'quality_metric_of':[file6['@id']],
        'total':20000000
    }

    return testapp.post_json('/samtools_flagstats_quality_metric', item).json['@graph'][0]


@pytest.fixture
def chipseq_filter_quality_metric(testapp, analysis_step_run_bam, file6):
    item = {
        'step_run': analysis_step_run_bam['@id'],
        'quality_metric_of':[file6['@id']],
        'NRF': 0.1,
        'PBC1': 0.3,
        'PBC2': 11
    }

    return testapp.post_json('/chipseq-filter-quality-metrics', item).json['@graph'][0]


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


def test_audit_file_read_length_insufficient(testapp, file1):
    testapp.patch_json(file1['@id'], {'read_length': 10})
    res = testapp.get(file1['@id'] + '@@index-data')
    errors = res.json['audit']
    errors_list = []
    for error_type in errors:
        errors_list.extend(errors[error_type])
    assert any(error['category'] == 'insufficient read length' for error in errors_list)


def test_audit_file_read_length_insufficient_excluding_bind_n_seq(testapp, file1, file_exp):
    testapp.patch_json(file_exp['@id'], {'assay_term_name': 'RNA Bind-n-Seq'})
    testapp.patch_json(file1['@id'], {'read_length': 20})
    res = testapp.get(file1['@id'] + '@@index-data')
    errors = res.json['audit']
    errors_list = []
    for error_type in errors:
        errors_list.extend(errors[error_type])
    assert all(error['category'] != 'insufficient read length' for error in errors_list)


def test_audit_file_read_length_sufficient(testapp, file1):
    testapp.patch_json(file1['@id'], {'read_length': 100})
    res = testapp.get(file1['@id'] + '@@index-data')
    errors = res.json['audit']
    errors_list = []
    for error_type in errors:
        errors_list.extend(errors[error_type])
    assert all(error['category'] != 'insufficient read length' for error in errors_list)


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


def test_audit_file_missing_quality_metrics(testapp, file6, analysis_step_run_bam, analysis_step_version_bam, analysis_step_bam, pipeline_bam, software):
    res = testapp.get(file6['@id'] + '@@index-data')
    errors = res.json['audit']
    errors_list = []
    for error_type in errors:
        errors_list.extend(errors[error_type])
    assert any(error['category'] == 'missing quality metrics' for error in errors_list)


def test_audit_file_read_depth(testapp, file6, file4, bam_quality_metric, analysis_step_run_bam,
                               analysis_step_version_bam, analysis_step_bam, pipeline_bam):
    testapp.patch_json(pipeline_bam['@id'],
                       {'title': 'RNA-seq of long RNAs (paired-end, stranded)'})
    testapp.patch_json(file4['@id'], {'run_type': 'single-ended'})
    testapp.patch_json(file6['@id'], {'derived_from': [file4['@id']]})
    res = testapp.get(file6['@id'] + '@@index-data')
    errors = res.json['audit']
    errors_list = []
    for error_type in errors:
        errors_list.extend(errors[error_type])
    assert any(error['category'] == 'insufficient read depth' for error in errors_list)


def test_audit_file_missing_quality_metrics_tophat_exclusion(testapp, file6,
                                                             analysis_step_run_bam,
                                                             analysis_step_version_bam,
                                                             analysis_step_bam, pipeline_bam,
                                                             software):
    testapp.patch_json(software['@id'], {'title': 'TopHat'})
    res = testapp.get(file6['@id'] + '@@index-data')
    errors = res.json['audit']
    errors_list = []
    for error_type in errors:
        errors_list.extend(errors[error_type])
    assert all(error['category'] != 'missing quality metrics' for error in errors_list)


def test_audit_file_missing_quality_metrics_WGBS_exclusion(testapp, file6,
                                                           analysis_step_run_bam,
                                                           analysis_step_version_bam,
                                                           analysis_step_bam, pipeline_bam,
                                                           software):
    testapp.patch_json(pipeline_bam['@id'], {'title': 'WGBS single-end pipeline - version 2'})
    res = testapp.get(file6['@id'] + '@@index-data')
    errors = res.json['audit']
    errors_list = []
    for error_type in errors:
        errors_list.extend(errors[error_type])
    assert all(error['category'] != 'missing quality metrics' for error in errors_list)


def test_audit_file_read_depth_inclusion_of_shRNA(testapp, file_exp, file6, file4,
                                                  bam_quality_metric, analysis_step_run_bam,
                                                  analysis_step_version_bam, analysis_step_bam,
                                                  pipeline_bam):
    testapp.patch_json(pipeline_bam['@id'],
                       {'title': 'RNA-seq of long RNAs (paired-end, stranded)'})
    testapp.patch_json(file_exp['@id'], {'assay_term_name': 'shRNA knockdown followed by RNA-seq'})
    testapp.patch_json(file6['@id'], {'dataset': file_exp['@id']})
    testapp.patch_json(file4['@id'], {'run_type': 'single-ended'})
    testapp.patch_json(file6['@id'], {'derived_from': [file4['@id']]})
    res = testapp.get(file6['@id'] + '@@index-data')
    errors = res.json['audit']
    errors_list = []
    for error_type in errors:
        errors_list.extend(errors[error_type])
    assert any(error['category'] == 'insufficient read depth' for error in errors_list)


def test_audit_file_read_depth_chip_seq_paired_end_no_target(testapp, file_exp, file6, file4,
                                                             chipseq_bam_quality_metric,
                                                             analysis_step_run_bam,
                                                             analysis_step_version_bam,
                                                             analysis_step_bam,
                                                             pipeline_bam):
    testapp.patch_json(file6['@id'], {'dataset': file_exp['@id']})
    testapp.patch_json(file4['@id'], {'run_type': 'paired-ended'})
    testapp.patch_json(file6['@id'], {'derived_from': [file4['@id']]})
    res = testapp.get(file6['@id'] + '@@index-data')
    errors = res.json['audit']
    errors_list = []
    for error_type in errors:
        errors_list.extend(errors[error_type])
    assert any(error['category'] == 'ChIP-seq missing target' for error in errors_list)


def test_audit_file_library_complexity_chip_seq(testapp, file_exp, file6, file4,
                                                chipseq_filter_quality_metric,
                                                analysis_step_run_bam,
                                                analysis_step_version_bam,
                                                analysis_step_bam,
                                                pipeline_bam):
    testapp.patch_json(file6['@id'], {'dataset': file_exp['@id']})
    testapp.patch_json(file4['@id'], {'run_type': 'paired-ended'})
    testapp.patch_json(file6['@id'], {'derived_from': [file4['@id']]})
    res = testapp.get(file6['@id'] + '@@index-data')
    errors = res.json['audit']
    errors_list = []
    for error_type in errors:
        errors_list.extend(errors[error_type])
    assert any(error['category'] == 'insufficient library complexity' for error in errors_list)


def test_audit_file_good_library_complexity_chip_seq(testapp, file_exp, file6, file4,
                                                     chipseq_filter_quality_metric,
                                                     analysis_step_run_bam,
                                                     analysis_step_version_bam,
                                                     analysis_step_bam,
                                                     pipeline_bam):
    testapp.patch_json(chipseq_filter_quality_metric['@id'],
                       {'NRF': 0.98, 'PBC1': 0.97})
    testapp.patch_json(file6['@id'], {'dataset': file_exp['@id']})
    testapp.patch_json(file4['@id'], {'run_type': 'paired-ended'})
    testapp.patch_json(file6['@id'], {'derived_from': [file4['@id']]})
    res = testapp.get(file6['@id'] + '@@index-data')
    errors = res.json['audit']
    errors_list = []
    for error_type in errors:
        errors_list.extend(errors[error_type])
    assert all(error['category'] != 'insufficient library complexity' for error in errors_list)


def test_audit_file_infinity_library_complexity_chip_seq(testapp, file_exp, file6, file4,
                                                         chipseq_filter_quality_metric,
                                                         analysis_step_run_bam,
                                                         analysis_step_version_bam,
                                                         analysis_step_bam,
                                                         pipeline_bam):
    testapp.patch_json(chipseq_filter_quality_metric['@id'],
                       {'NRF': 0.98, 'PBC1': 0.97, 'PBC2': 'Infinity'})
    testapp.patch_json(file6['@id'], {'dataset': file_exp['@id']})
    testapp.patch_json(file4['@id'], {'run_type': 'paired-ended'})
    testapp.patch_json(file6['@id'], {'derived_from': [file4['@id']]})
    res = testapp.get(file6['@id'] + '@@index-data')
    errors = res.json['audit']
    errors_list = []
    for error_type in errors:
        errors_list.extend(errors[error_type])
    assert all(error['category'] != 'insufficient library complexity' for error in errors_list)


def test_audit_file_read_depth_chip_seq_paired_end(testapp, file_exp, file6, file4,
                                                   chipseq_bam_quality_metric,
                                                   analysis_step_run_bam,
                                                   analysis_step_version_bam,
                                                   analysis_step_bam, target_H3K27ac,
                                                   pipeline_bam):
    testapp.patch_json(file_exp['@id'], {'target': target_H3K27ac['@id']})
    testapp.patch_json(file6['@id'], {'dataset': file_exp['@id']})
    testapp.patch_json(file4['@id'], {'run_type': 'paired-ended'})
    testapp.patch_json(file6['@id'], {'derived_from': [file4['@id']]})
    res = testapp.get(file6['@id'] + '@@index-data')
    errors = res.json['audit']
    errors_list = []
    for error_type in errors:
        errors_list.extend(errors[error_type])
    assert any(error['category'] == 'low read depth' for error in errors_list)


def test_audit_file_insufficient_read_depth_chip_seq_paired_end(testapp, file_exp, file6, file4,
                                                                chipseq_bam_quality_metric,
                                                                analysis_step_run_bam,
                                                                analysis_step_version_bam,
                                                                analysis_step_bam, target_H3K27ac,
                                                                pipeline_bam):
    testapp.patch_json(file_exp['@id'], {'target': target_H3K27ac['@id']})
    testapp.patch_json(chipseq_bam_quality_metric['@id'], {'total': 10000000})
    testapp.patch_json(file6['@id'], {'dataset': file_exp['@id']})
    testapp.patch_json(file4['@id'], {'run_type': 'paired-ended'})
    testapp.patch_json(file6['@id'], {'derived_from': [file4['@id']]})
    res = testapp.get(file6['@id'] + '@@index-data')
    errors = res.json['audit']
    errors_list = []
    for error_type in errors:
        errors_list.extend(errors[error_type])
    assert any(error['category'] == 'insufficient read depth' for error in errors_list)


def test_audit_file_mad_qc_spearman_correlation(testapp, pipeline_bam,
                                                base_experiment, file7,
                                                donor_1, mad_quality_metric,
                                                donor_2,
                                                biosample_1,
                                                biosample_2,
                                                library_1,
                                                library_2,
                                                replicate_1_1,
                                                replicate_2_1):
    testapp.patch_json(biosample_1['@id'], {'donor': donor_1['@id']})
    testapp.patch_json(biosample_2['@id'], {'donor': donor_1['@id']})
    testapp.patch_json(library_1['@id'], {'biosample': biosample_1['@id']})
    testapp.patch_json(library_2['@id'], {'biosample': biosample_2['@id']})
    testapp.patch_json(replicate_1_1['@id'], {'library': library_1['@id']})
    testapp.patch_json(replicate_2_1['@id'], {'library': library_2['@id']})
    testapp.patch_json(base_experiment['@id'], {'replicates': [replicate_1_1['@id'],
                                                               replicate_2_1['@id']]})
    testapp.patch_json(pipeline_bam['@id'], {'title': 'RAMPAGE (paired-end, stranded)'})
    testapp.patch_json(base_experiment['@id'], {'assay_term_name': 'RNA-seq'})
    testapp.patch_json(file7['@id'], {'dataset': base_experiment['@id']})
    res = testapp.get(file7['@id'] + '@@index-data')
    errors = res.json['audit']
    errors_list = []
    for error_type in errors:
        errors_list.extend(errors[error_type])
    assert any(error['category'] == 'insufficient spearman correlation' for error in errors_list)


def test_audit_file_mad_qc_spearman_correlation_2(testapp, file7,  file_exp,
                                                  mad_quality_metric,
                                                  analysis_step_run_bam,
                                                  analysis_step_version_bam, analysis_step_bam,
                                                  pipeline_bam):
    testapp.patch_json(mad_quality_metric['@id'], {'Spearman correlation': 0.99})
    testapp.patch_json(pipeline_bam['@id'], {'title': 'RAMPAGE (paired-end, stranded)'})
    testapp.patch_json(file_exp['@id'], {'assay_term_name': 'RNA-seq'})
    testapp.patch_json(file7['@id'], {'dataset': file_exp['@id']})
    res = testapp.get(file7['@id'] + '@@index-data')
    errors = res.json['audit']
    errors_list = []
    for error_type in errors:
        errors_list.extend(errors[error_type])
    assert all(error['category'] != 'insufficient spearman correlation' for error in errors_list)


def test_audit_file_mad_qc_spearman_correlation_silver(testapp, pipeline_bam,
                                                       base_experiment, file7,
                                                       donor_1, mad_quality_metric,
                                                       donor_2,
                                                       biosample_1,
                                                       biosample_2,
                                                       library_1,
                                                       library_2,
                                                       replicate_1_1,
                                                       replicate_2_1):
    testapp.patch_json(biosample_1['@id'], {'donor': donor_1['@id']})
    testapp.patch_json(biosample_2['@id'], {'donor': donor_1['@id']})
    testapp.patch_json(library_1['@id'], {'biosample': biosample_1['@id']})
    testapp.patch_json(library_2['@id'], {'biosample': biosample_2['@id']})
    testapp.patch_json(replicate_1_1['@id'], {'library': library_1['@id']})
    testapp.patch_json(replicate_2_1['@id'], {'library': library_2['@id']})
    testapp.patch_json(base_experiment['@id'], {'replicates': [replicate_1_1['@id'],
                                                               replicate_2_1['@id']]})
    testapp.patch_json(mad_quality_metric['@id'], {'Spearman correlation': 0.891})
    testapp.patch_json(pipeline_bam['@id'], {'title': 'RAMPAGE (paired-end, stranded)'})
    testapp.patch_json(base_experiment['@id'], {'assay_term_name': 'RNA-seq'})
    testapp.patch_json(file7['@id'], {'dataset': base_experiment['@id']})
    res = testapp.get(file7['@id'] + '@@index-data')
    errors = res.json['audit']
    errors_list = []
    for error_type in errors:
        if error_type == 'WARNING':
            errors_list.extend(errors[error_type])
    assert any(error['category'] == 'low spearman correlation' for error in errors_list)


def test_audit_file_mad_qc_spearman_correlation_silver_2(testapp, file7,  file_exp,
                                                         mad_quality_metric,
                                                         analysis_step_run_bam,
                                                         analysis_step_version_bam,
                                                         analysis_step_bam,
                                                         pipeline_bam):
    testapp.patch_json(mad_quality_metric['@id'], {'Spearman correlation': 0.891})
    testapp.patch_json(pipeline_bam['@id'], {'title': 'RAMPAGE (paired-end, stranded)'})
    testapp.patch_json(file_exp['@id'], {'assay_term_name': 'RNA-seq'})
    testapp.patch_json(file7['@id'], {'dataset': file_exp['@id']})
    res = testapp.get(file7['@id'] + '@@index-data')
    errors = res.json['audit']
    errors_list = []
    for error_type in errors:
        if error_type != 'WARNING':
            errors_list.extend(errors[error_type])
    assert all(error['category'] != 'low spearman correlation' for error in errors_list)


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
