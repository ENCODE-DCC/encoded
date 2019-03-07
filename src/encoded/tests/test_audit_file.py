import pytest


@pytest.fixture
def file_exp(lab, award, testapp, experiment, ileum):
    item = {
        'lab': lab['uuid'],
        'award': award['uuid'],
        'assay_term_name': 'RAMPAGE',
        'biosample_ontology': ileum['uuid'],
        'possible_controls': [experiment['uuid']],
        'status': 'released',
        'date_released': '2016-01-01',
        'experiment_classification': ['functional genomics assay']
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
def file_exp2(lab, award, testapp, ileum):
    item = {
        'lab': lab['uuid'],
        'award': award['uuid'],
        'assay_term_name': 'RAMPAGE',
        'biosample_ontology': ileum['uuid'],
        'status': 'released',
        'date_released': '2016-01-01',
        'experiment_classification': ['functional genomics assay']
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
def file1_2(file_exp, award, lab, file_rep1_2, platform1, testapp):
    item = {
        'dataset': file_exp['uuid'],
        'replicate': file_rep1_2['uuid'],
        'file_format': 'fastq',
        'platform': platform1['@id'],
        'md5sum': '91be74b6e11515393507f4ebfa66d58a',
        'output_type': 'raw data',
        'file_size': 34,
        'run_type': 'single-ended',
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
        'md5sum': '91be74b6e11515393507f4ebfa66d58b',
        'output_type': 'raw data',
        'file_size': 34,
        'run_type': 'single-ended',
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
        'md5sum': '91be74b6e11515393507f4ebfa66d58c',
        'output_type': 'reads',
        "read_length": 50,
        'file_size': 34,
        'run_type': 'single-ended',
        'platform': platform1['uuid'],
        'award': award['uuid'],
        'lab': lab['uuid'],
        'status': 'released',
        'controlled_by': [file2['uuid']]
    }
    return testapp.post_json('/file', item, status=201).json['@graph'][0]


@pytest.fixture
def file3(file_exp, award, lab, file_rep, platform1, testapp):
    item = {
        'dataset': file_exp['uuid'],
        'replicate': file_rep['uuid'],
        'file_format': 'fastq',
        'file_size': 34,
        'md5sum': '91be74b6e11515393507f4ebfa56d78d',
        'output_type': 'reads',
        "read_length": 50,
        'platform': platform1['uuid'],
        'run_type': 'single-ended',
        'award': award['uuid'],
        'lab': lab['uuid'],
        'status': 'released'
    }
    return testapp.post_json('/file', item, status=201).json['@graph'][0]


@pytest.fixture
def file4(file_exp2, award, lab, file_rep2, platform1, testapp):
    item = {
        'dataset': file_exp2['uuid'],
        'replicate': file_rep2['uuid'],
        'file_format': 'fastq',
        'md5sum': '91ae74b6e11515393507f4ebfa66d78a',
        'output_type': 'reads',
        'platform': platform1['uuid'],
        "read_length": 50,
        'file_size': 34,
        'run_type': 'single-ended',
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
        'md5sum': '91ce74b6e11515393507f4ebfa66d78a',
        'output_type': 'alignments',
        'award': award['uuid'],
        'file_size': 34,
        'assembly': 'hg19',
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
        'md5sum': '91be74b6e11515394507f4ebfa66d78a',
        'output_type': 'gene quantifications',
        'award': award['uuid'],
        'lab': encode_lab['uuid'],
        'status': 'released',
        'step_run': analysis_step_run_bam['uuid']
    }
    return testapp.post_json('/file', item, status=201).json['@graph'][0]


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
        'step_label': 'bamqc-step',
        'title': 'bamqc step',
        'major_version': 1,
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


@pytest.fixture
def analysis1(testapp, experiment):
    return testapp.post_json(
        '/analyses',
        {'dataset': experiment['@id']},
        status=201
    ).json['@graph'][0]


@pytest.fixture
def analysis2(testapp, experiment):
    return testapp.post_json(
        '/analyses',
        {'dataset': experiment['@id']},
        status=201
    ).json['@graph'][0]


def test_audit_file_mismatched_paired_with(testapp, file1, file4):
    testapp.patch_json(file1['@id'], {
                       'run_type': 'paired-ended', 'paired_end': '2', 'paired_with': file4['uuid']})
    res = testapp.get(file1['@id'] + '@@index-data')
    errors = res.json['audit']
    errors_list = []
    for error_type in errors:
        errors_list.extend(errors[error_type])
    assert any(error['category'] ==
               'inconsistent paired_with' for error in errors_list)


def test_audit_file_inconsistent_read_count_paired_with(testapp, file1, file4):
    testapp.patch_json(file1['@id'], {
                       'run_type': 'paired-ended',
                       'read_count': 20,
                       'paired_end': '2',
                       'paired_with': file4['uuid']})
    testapp.patch_json(file4['@id'], {
                       'read_count': 21})
    res = testapp.get(file1['@id'] + '@@index-data')
    errors = res.json['audit']
    errors_list = []
    for error_type in errors:
        errors_list.extend(errors[error_type])
    assert any(error['category'] ==
               'inconsistent read count' for error in errors_list)
    testapp.patch_json(file4['@id'], {
                       'read_count': 20})
    res2 = testapp.get(file1['@id'] + '@@index-data')
    errors = res2.json['audit']
    errors_list = []
    for error_type in errors:
        errors_list.extend(errors[error_type])
    assert all(error['category'] !=
               'inconsistent read count' for error in errors_list)


def test_audit_file_missing_controlled_by(testapp, file3):
    res = testapp.get(file3['@id'] + '@@index-data')
    errors = res.json['audit']
    errors_list = []
    for error_type in errors:
        errors_list.extend(errors[error_type])
    assert any(error['category'] ==
               'missing controlled_by' for error in errors_list)


def test_audit_file_mismatched_controlled_by(testapp, file1):
    res = testapp.get(file1['@id'] + '@@index-data')
    errors = res.json['audit']
    errors_list = []
    for error_type in errors:
        errors_list.extend(errors[error_type])
    assert any(error['category'] ==
               'inconsistent control' for error in errors_list)


def test_audit_file_read_length_controlled_by(testapp, file1_2,
                                              file2, file_exp,
                                              file_exp2, ileum):
    testapp.patch_json(file1_2['@id'], {'read_length': 50,
                                        'run_type': 'single-ended'})
    testapp.patch_json(file2['@id'], {'read_length': 150,
                                      'run_type': 'single-ended'})
    testapp.patch_json(file1_2['@id'], {'controlled_by': [file2['@id']]})
    testapp.patch_json(file_exp['@id'], {
                       'possible_controls': [file_exp2['@id']]})
    testapp.patch_json(file_exp2['@id'], {'assay_term_name': 'RAMPAGE',
                                          'biosample_ontology': ileum['uuid']})
    res = testapp.get(file1_2['@id'] + '@@index-data')
    errors = res.json['audit']
    errors_list = []
    for error_type in errors:
        errors_list.extend(errors[error_type])
    assert any(error['category'] ==
               'inconsistent control read length' for error in errors_list)


def test_audit_file_read_length_controlled_by_exclusion(testapp, file1_2,
                                                        file2, file_exp,
                                                        file_exp2, ileum):
    testapp.patch_json(file1_2['@id'], {'read_length': 50,
                                        'run_type': 'single-ended'})
    testapp.patch_json(file2['@id'], {'read_length': 52,
                                      'run_type': 'single-ended'})
    testapp.patch_json(file1_2['@id'], {'controlled_by': [file2['@id']]})
    testapp.patch_json(file_exp['@id'], {
                       'possible_controls': [file_exp2['@id']]})
    testapp.patch_json(file_exp2['@id'], {'assay_term_name': 'RAMPAGE',
                                          'biosample_ontology': ileum['uuid']})
    res = testapp.get(file1_2['@id'] + '@@index-data')
    errors = res.json['audit']
    errors_list = []
    for error_type in errors:
        errors_list.extend(errors[error_type])
    assert any(error['category'] !=
               'inconsistent control read length' for error in errors_list)


def test_audit_file_replicate_match_inconsistent(testapp, file1, file_rep2):
    testapp.patch_json(file1['@id'], {'replicate': file_rep2['uuid']})
    res = testapp.get(file1['@id'] + '@@index-data')
    errors = res.json['audit']
    errors_list = []
    for error_type in errors:
        errors_list.extend(errors[error_type])
    assert any(error['category'] ==
               'inconsistent replicate' for error in errors_list)


def test_audit_file_replicate_match_consistent(testapp, file1, file_rep2):
    #testapp.patch_json(file1['@id'], {'replicate': file_rep2['uuid']})
    res = testapp.get(file1['@id'] + '@@index-data')
    errors = res.json['audit']
    errors_list = []
    for error_type in errors:
        errors_list.extend(errors[error_type])
    assert all(error['category'] !=
               'inconsistent replicate' for error in errors_list)


'''
def test_audit_modERN_missing_step_run(testapp, file_exp, file3, award):
    testapp.patch_json(award['@id'], {'rfa': 'modERN'})
    testapp.patch_json(file_exp['@id'], {'assay_term_name': 'ChIP-seq'})
    testapp.patch_json(file3['@id'], {'dataset': file_exp['@id'], 'file_format': 'bam',
                                      'assembly': 'ce10', 'output_type': 'alignments'})
    res = testapp.get(file3['@id'] + '@@index-data')
    errors = res.json['audit']
    errors_list = []
    for error_type in errors:
        errors_list.extend(errors[error_type])
    assert any(error['category'] == 'missing step_run' for error in errors_list)


def test_audit_modERN_missing_derived_from(testapp, file_exp, file3, award, analysis_step_version_bam, analysis_step_bam, analysis_step_run_bam):
    testapp.patch_json(award['@id'], {'rfa': 'modERN'})
    testapp.patch_json(file_exp['@id'], {'assay_term_name': 'ChIP-seq'})
    testapp.patch_json(file3['@id'], {'dataset': file_exp['@id'], 'file_format': 'bam', 'assembly': 'ce10',
                                      'output_type': 'alignments', 'step_run': analysis_step_run_bam['@id']})
    res = testapp.get(file3['@id'] + '@@index-data')
    errors = res.json['audit']
    errors_list = []
    for error_type in errors:
        errors_list.extend(errors[error_type])
    assert any(error['category'] == 'missing derived_from' for error in errors_list)


def test_audit_modERN_wrong_step_run(testapp, file_exp, file3, file4, award, analysis_step_version_bam, analysis_step_bam, analysis_step_run_bam):
    testapp.patch_json(award['@id'], {'rfa': 'modERN'})
    testapp.patch_json(file_exp['@id'], {'assay_term_name': 'ChIP-seq'})
    testapp.patch_json(file3['@id'], {'dataset': file_exp['@id'], 'file_format': 'bed',
                                      'file_format_type': 'narrowPeak', 'output_type': 'peaks',
                                      'step_run': analysis_step_run_bam['@id'], 'assembly': 'ce11',
                                      'derived_from': [file4['@id']]})
    res = testapp.get(file3['@id'] + '@@index-data')
    errors = res.json['audit']
    errors_list = []
    for error_type in errors:
        errors_list.extend(errors[error_type])
    assert any(error['category'] == 'wrong step_run for peaks' for error in errors_list)


def test_audit_modERN_unexpected_step_run(testapp, file_exp, file2, award, analysis_step_run_bam):
    testapp.patch_json(award['@id'], {'rfa': 'modERN'})
    testapp.patch_json(file_exp['@id'], {'assay_term_name': 'ChIP-seq'})
    testapp.patch_json(file2['@id'], {'dataset': file_exp['@id'], 'step_run': analysis_step_run_bam['@id']})
    res = testapp.get(file2['@id'] + '@@index-data')
    errors = res.json['audit']
    errors_list = []
    for error_type in errors:
        errors_list.extend(errors[error_type])
    assert any(error['category'] == 'unexpected step_run' for error in errors_list)
'''


def test_audit_file_assembly(testapp, file6, file7):
    testapp.patch_json(file6['@id'], {'assembly': 'GRCh38'})
    testapp.patch_json(file7['@id'], {'derived_from': [file6['@id']],
                                      'assembly': 'hg19'})
    res = testapp.get(file7['@id'] + '@@index-data')
    errors = res.json['audit']
    errors_list = []
    for error_type in errors:
        errors_list.extend(errors[error_type])
    assert any(error['category'] == 'inconsistent assembly'
               for error in errors_list)


def test_audit_file_step_run(testapp, bam_file, analysis_step_run_bam):
    res = testapp.get(bam_file['@id'] + '@@index-data')
    errors = res.json['audit']
    errors_list = []
    for error_type in errors:
        errors_list.extend(errors[error_type])
    assert any(error['category'] == 'missing analysis_step_run'
               for error in errors_list)
    testapp.patch_json(bam_file['@id'], {'step_run': analysis_step_run_bam['@id']})
    res = testapp.get(bam_file['@id'] + '@@index-data')
    errors = res.json['audit']
    errors_list = []
    for error_type in errors:
        errors_list.extend(errors[error_type])
    assert all(error['category'] != 'missing analysis_step_run'
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
                                      'file_format': 'bam',
                                      'assembly': 'hg19'})
    testapp.patch_json(
        file7['@id'], {'file_format': 'tsv', 'assembly': 'hg19'})
    res = testapp.get(file6['@id'] + '@@index-data')
    errors = res.json['audit']
    errors_list = []
    for error_type in errors:
        errors_list.extend(errors[error_type])
    assert any(error['category'] == 'missing derived_from'
               for error in errors_list)


def test_audit_file_bam_derived_from_fastq(testapp, file4, file6):
    testapp.patch_json(file6['@id'], {'derived_from': [file4['@id']],
                                      'status': 'released',
                                      'file_format': 'bam',
                                      'assembly': 'hg19'})
    res = testapp.get(file6['@id'] + '@@index-data')
    errors = res.json['audit']
    errors_list = []
    for error_type in errors:
        errors_list.extend(errors[error_type])
    assert all(error['category'] != 'missing derived_from'
               for error in errors_list)


def test_audit_file_bam_derived_from_csfasta(testapp, file4, file6):
    testapp.patch_json(file6['@id'], {'derived_from': [file4['@id']],
                                      'status': 'released',
                                      'file_format': 'bam',
                                      'assembly': 'hg19'})
    testapp.patch_json(file4['@id'], {'file_format': 'csfasta'})
    res = testapp.get(file6['@id'] + '@@index-data')
    errors = res.json['audit']
    errors_list = []
    for error_type in errors:
        errors_list.extend(errors[error_type])
    assert all(error['category'] != 'missing derived_from'
               for error in errors_list)


def test_audit_file_bam_derived_from_csqual(testapp, file4, file6):
    testapp.patch_json(file6['@id'], {'derived_from': [file4['@id']],
                                      'status': 'released',
                                      'file_format': 'bam',
                                      'assembly': 'hg19'})
    testapp.patch_json(file4['@id'], {'file_format': 'csqual'})
    res = testapp.get(file6['@id'] + '@@index-data')
    errors = res.json['audit']
    errors_list = []
    for error_type in errors:
        errors_list.extend(errors[error_type])
    assert all(error['category'] != 'missing derived_from'
               for error in errors_list)


def test_audit_file_released_bam_derived_from_revoked_fastq(testapp, file4, file6):
    testapp.patch_json(file6['@id'], {'derived_from': [file4['@id']],
                                      'status': 'released',
                                      'file_format': 'bam',
                                      'assembly': 'hg19'})

    testapp.patch_json(file4['@id'], {'status': 'revoked'})
    res = testapp.get(file6['@id'] + '@@index-data')
    errors = res.json['audit']
    errors_list = []
    for error_type in errors:
        errors_list.extend(errors[error_type])
    assert any(error['category'] == 'missing derived_from'
               for error in errors_list)


def test_audit_file_deleted_bam_derived_from_revoked_fastq(testapp, file4, file6):
    testapp.patch_json(file6['@id'], {'derived_from': [file4['@id']],
                                      'status': 'deleted',
                                      'file_format': 'bam',
                                      'assembly': 'hg19'})

    testapp.patch_json(file4['@id'], {'status': 'revoked'})
    res = testapp.get(file6['@id'] + '@@index-data')
    errors = res.json['audit']
    errors_list = []
    for error_type in errors:
        errors_list.extend(errors[error_type])
    assert all(error['category'] != 'missing derived_from'
               for error in errors_list)


def test_audit_file_released_bam_derived_from_deleted_fastq(testapp, file4, file6):
    testapp.patch_json(file6['@id'], {'derived_from': [file4['@id']],
                                      'status': 'released',
                                      'file_format': 'bam',
                                      'assembly': 'hg19'})

    testapp.patch_json(file4['@id'], {'status': 'deleted'})
    res = testapp.get(file6['@id'] + '@@index-data')
    errors = res.json['audit']
    errors_list = []
    for error_type in errors:
        errors_list.extend(errors[error_type])
    assert any(error['category'] == 'missing derived_from'
               for error in errors_list)


def test_audit_file_deleted_bam_derived_from_deleted_fastq(testapp, file4, file6):
    testapp.patch_json(file6['@id'], {'derived_from': [file4['@id']],
                                      'status': 'deleted',
                                      'file_format': 'bam',
                                      'assembly': 'hg19'})

    testapp.patch_json(file4['@id'], {'status': 'deleted'})
    res = testapp.get(file6['@id'] + '@@index-data')
    errors = res.json['audit']
    errors_list = []
    for error_type in errors:
        errors_list.extend(errors[error_type])
    assert all(error['category'] != 'missing derived_from'
               for error in errors_list)


def test_audit_file_deleted_bam_derived_from_released_fastq(testapp, file4, file6):
    testapp.patch_json(file6['@id'], {'derived_from': [file4['@id']],
                                      'status': 'deleted',
                                      'file_format': 'bam',
                                      'assembly': 'hg19'})

    testapp.patch_json(file4['@id'], {'status': 'released'})
    res = testapp.get(file6['@id'] + '@@index-data')
    errors = res.json['audit']
    errors_list = []
    for error_type in errors:
        errors_list.extend(errors[error_type])
    assert all(error['category'] != 'missing derived_from'
               for error in errors_list)


def test_audit_file_missing_derived_from_ignores_replaced_bams(testapp, file4, file6):
    testapp.patch_json(file6['@id'], {'derived_from': [file4['@id']],
                                      'status': 'replaced',
                                      'file_format': 'bam',
                                      'assembly': 'hg19'})
    testapp.patch_json(file4['@id'], {'status': 'deleted'})
    res = testapp.get('/{}/@@index-data'.format(file6['uuid']))
    errors = res.json['audit']
    errors_list = []
    for error_type in errors:
        errors_list.extend(errors[error_type])
    assert all(error['category'] != 'missing derived_from'
               for error in errors_list)


def test_audit_file_bam_derived_from_bam_no_fastq(testapp, file7, file6):
    testapp.patch_json(file6['@id'], {'derived_from': [file7['@id']],
                                      'status': 'released',
                                      'file_format': 'bam',
                                      'assembly': 'hg19'})
    testapp.patch_json(
        file7['@id'], {'file_format': 'bam', 'assembly': 'hg19'})
    res = testapp.get(file6['@id'] + '@@index-data')
    errors = res.json['audit']
    errors_list = []
    for error_type in errors:
        errors_list.extend(errors[error_type])
    assert all(error['category'] != 'missing derived_from'
               for error in errors_list)


def test_audit_file_bam_derived_from_revoked_bam_no_fastq(testapp, file7, file6):
    testapp.patch_json(file6['@id'], {'derived_from': [file7['@id']],
                                      'status': 'released',
                                      'file_format': 'bam',
                                      'assembly': 'hg19'})
    testapp.patch_json(file7['@id'], {'file_format': 'bam',
                                      'assembly': 'hg19',
                                      'status': 'revoked'})
    res = testapp.get(file6['@id'] + '@@index-data')
    errors = res.json['audit']
    errors_list = []
    for error_type in errors:
        errors_list.extend(errors[error_type])
    assert any(error['category'] == 'missing derived_from'
               for error in errors_list)


def test_audit_file_revoked_bam_derived_from_revoked_bam_no_fastq(testapp, file7, file6):
    testapp.patch_json(file6['@id'], {'derived_from': [file7['@id']],
                                      'status': 'revoked',
                                      'file_format': 'bam',
                                      'assembly': 'hg19'})
    testapp.patch_json(file7['@id'], {'file_format': 'bam',
                                      'assembly': 'hg19',
                                      'status': 'revoked'})
    res = testapp.get(file6['@id'] + '@@index-data')
    errors = res.json['audit']
    errors_list = []
    for error_type in errors:
        errors_list.extend(errors[error_type])
    assert all(error['category'] != 'missing derived_from'
               for error in errors_list)


def test_audit_file_bam_derived_from_different_experiment(testapp, file6, file4, file_exp):
    testapp.patch_json(file4['@id'], {'dataset': file_exp['@id']})
    testapp.patch_json(file6['@id'], {'derived_from': [file4['@id']],
                                      'assembly': 'hg19',
                                      'status': 'released'})
    res = testapp.get(file6['@id'] + '@@index-data')
    errors = res.json['audit']
    errors_list = []
    for error_type in errors:
        errors_list.extend(errors[error_type])
    assert any(error['category'] == 'inconsistent derived_from'
               for error in errors_list)


'''
def test_audit_file_md5sum(testapp, file1):
    testapp.patch_json(file1['@id'], {'md5sum': 'some_random_text'})
    res = testapp.get(file1['@id'] + '@@index-data')
    errors = res.json['audit']
    errors_list = []
    for error_type in errors:
        errors_list.extend(errors[error_type])
    assert any(error['category'] == 'inconsistent md5sum'
               for error in errors_list)
'''


def test_audit_file_missing_derived_from_audit_with_made_up_status(testapp, file4, file6):
    # This tests that a status that's not in STATUS_LEVEL dict won't break missing derived_from
    # audit.
    testapp.patch_json(file6['@id'], {'derived_from': [file4['@id']],
                                      'status': 'released',
                                      'file_format': 'bam',
                                      'assembly': 'hg19'})

    testapp.patch_json(file4['@id'] + '?validate=false',
                       {'status': 'new made up status'})
    res = testapp.get(file6['@id'] + '@@index-data')
    errors = res.json['audit']
    errors_list = []
    for error_type in errors:
        errors_list.extend(errors[error_type])
    assert all(error['category'] != 'missing derived_from'
               for error in errors_list)


def test_audit_file_duplicate_quality_metrics(testapp,
                                              file_exp,
                                              file2,
                                              file6,
                                              chipseq_bam_quality_metric,
                                              chipseq_bam_quality_metric_2,
                                              analysis_step_run_bam):
    testapp.patch_json(
        file_exp['@id'],
        {
            'assay_term_name': 'ChIP-seq'
        }
    )
    testapp.patch_json(
        chipseq_bam_quality_metric['@id'],
        {
            'quality_metric_of': [file6['@id']],
            'processing_stage': 'filtered'
        }
    )
    testapp.patch_json(
        chipseq_bam_quality_metric_2['@id'],
        {
            'quality_metric_of': [file6['@id']],
            'processing_stage': 'filtered'
        }
    )
    testapp.patch_json(
        file6['@id'],
        {
            'dataset': file_exp['@id'],
            'file_format': 'bam',
            'output_type': 'alignments',
            'assembly': 'GRCh38',
            'derived_from': [file2['@id']],
            'step_run': analysis_step_run_bam['@id']
        }
    )
    res = testapp.get(file6['@id'] + '@@index-data')
    errors = res.json['audit']
    errors_list = [error for v in errors.values() for error in v]
    assert any(
        error['category'] == 'duplicate quality metric'
        for error in errors_list
    )


def test_audit_file_no_duplicate_quality_metrics(testapp,
                                                 file_exp,
                                                 file2,
                                                 file6,
                                                 chipseq_bam_quality_metric,
                                                 chipseq_bam_quality_metric_2,
                                                 analysis_step_run_bam):
    testapp.patch_json(
        file_exp['@id'],
        {
            'assay_term_name': 'ChIP-seq'
        }
    )
    testapp.patch_json(
        chipseq_bam_quality_metric['@id'],
        {
            'quality_metric_of': [file6['@id']],
            'processing_stage': 'filtered'
        }
    )
    testapp.patch_json(
        chipseq_bam_quality_metric_2['@id'],
        {
            'quality_metric_of': [file6['@id']],
            'processing_stage': 'unfiltered'
        }
    )
    testapp.patch_json(
        file6['@id'],
        {
            'dataset': file_exp['@id'],
            'file_format': 'bam',
            'output_type': 'alignments',
            'assembly': 'GRCh38',
            'derived_from': [file2['@id']],
            'step_run': analysis_step_run_bam['@id']
        }
    )
    res = testapp.get(file6['@id'] + '@@index-data')
    errors = res.json['audit']
    errors_list = [error for v in errors.values() for error in v]
    assert all(
        error['category'] != 'duplicate quality metric'
        for error in errors_list
    )


def test_audit_public_file_in_private_bucket(testapp, dummy_request, file_with_external_sheet):
    testapp.patch_json(
        file_with_external_sheet['@id'],
        {
            'status': 'released'
        }
    )
    dummy_request.registry.settings['pds_public_bucket'] = 'pds_public_bucket_test'
    dummy_request.registry.settings['pds_private_bucket'] = 'pds_private_bucket_test'
    res = testapp.get(file_with_external_sheet['@id'] + '@@index-data')
    errors = res.json['audit']
    errors_list = [error for v in errors.values() for error in v if error['category'] == 'incorrect file bucket']
    assert errors_list
    assert errors_list[0]['detail'].split('to')[-1].strip() == 's3://pds_public_bucket_test/xyz.bed'


def test_audit_public_file_in_public_bucket(testapp, dummy_request, public_file_with_public_external_sheet):
    dummy_request.registry.settings['pds_public_bucket'] = 'pds_public_bucket_test'
    dummy_request.registry.settings['pds_private_bucket'] = 'pds_private_bucket_test'
    res = testapp.get(public_file_with_public_external_sheet['@id'] + '@@index-data')
    errors = res.json['audit']
    errors_list = [error for v in errors.values() for error in v]
    assert all([
        error['category'] != 'incorrect file bucket'
        for error in errors_list]
    )


def test_audit_private_file_in_public_bucket(testapp, dummy_request, file_with_external_sheet):
    testapp.patch_json(
        file_with_external_sheet['@id'],
        {
            'status': 'deleted'
        }
    )
    dummy_request.registry.settings['pds_public_bucket'] = 'pds_public_bucket_test'
    dummy_request.registry.settings['pds_private_bucket'] = 'pds_private_bucket_test'
    res = testapp.get(file_with_external_sheet['@id'] + '@@index-data')
    errors = res.json['audit']
    errors_list = [error for v in errors.values() for error in v]
    assert errors_list
    assert errors_list[0]['detail'].split('to')[-1].strip() == 's3://pds_private_bucket_test/xyz.bed'


def test_audit_file_statuses_in_s3_statuses(testapp):
    # Make sure public_s3_statuses and private_s3_statuses lists in File item include
    # all statuses in File schema, except upload failed and content error.
    from ..types.file import File
    public_s3_statuses = File.public_s3_statuses
    private_s3_statuses = File.private_s3_statuses
    assert public_s3_statuses
    assert private_s3_statuses
    file_schema = testapp.get('/profiles/file.json').json
    file_statuses = file_schema.get('properties', {}).get('status', {}).get('enum')
    assert file_statuses
    file_statuses = [f for f in file_statuses if f not in ['content error', 'upload failed']]
    # If this fails sync public/private_s3_statuses with statuses in file schema.
    assert not set(file_statuses) - set(public_s3_statuses + private_s3_statuses)


def test_audit_incorrect_bucket_file_no_external_sheet(testapp, dummy_request, file_with_no_external_sheet):
    testapp.patch_json(
        file_with_no_external_sheet['@id'],
        {
            'status': 'released'
        }
    )
    dummy_request.registry.settings['pds_public_bucket'] = 'pds_public_bucket_test'
    dummy_request.registry.settings['pds_private_bucket'] = 'pds_private_bucket_test'
    res = testapp.get(file_with_no_external_sheet['@id'] + '@@index-data')
    errors = res.json['audit']
    errors_list = [error for v in errors.values() for error in v if error['category'] == 'incorrect file bucket']
    assert not errors_list


def test_audit_file_analysis(testapp,
                             analysis1, analysis2,
                             analysis_step_run, analysis_step_run_bam,
                             file_exp2, file6, file7):
    res = testapp.get(file6['@id'] + '@@index-data')
    errors = res.json['audit']
    assert all(e['category'] not in ['miss output_from_step_run',
                                     'inconsistent analysis',
                                     'multiple analyses']
               for v in errors.values() for e in v)

    testapp.patch_json(file6['@id'], {'dataset': analysis1['uuid']})
    res = testapp.get(file6['@id'] + '@@index-data')
    errors = res.json['audit']
    assert any(e['category'] == 'miss output_from_step_run'
               for v in errors.values() for e in v)

    testapp.patch_json(analysis_step_run['@id'],
                       {'analysis': analysis2['uuid'],
                        'output_files': [file6['uuid']]})
    res = testapp.get(file6['@id'] + '@@index-data')
    errors = res.json['audit']
    assert any(e['category'] == 'inconsistent analysis'
               for v in errors.values() for e in v)

    testapp.patch_json(analysis_step_run_bam['@id'],
                       {'analysis': analysis1['uuid'],
                        'output_files': [file6['uuid']]})
    res = testapp.get(file6['@id'] + '@@index-data')
    errors = res.json['audit']
    assert any(e['category'] == 'multiple analyses'
               for v in errors.values() for e in v)


def test_audit_incorrect_file_bucket_no_audit_restricted_file(testapp, dummy_request, file_with_external_sheet):
    testapp.patch_json(
        file_with_external_sheet['@id'],
        {
            'status': 'released',
            'restricted': True
        }
    )
    dummy_request.registry.settings['pds_public_bucket'] = 'pds_public_bucket_test'
    dummy_request.registry.settings['pds_private_bucket'] = 'pds_private_bucket_test'
    res = testapp.get(file_with_external_sheet['@id'] + '@@index-data')
    errors = res.json['audit']
    errors_list = [error for v in errors.values() for error in v if error['category'] == 'incorrect file bucket']
    assert not errors_list


def test_audit_incorrect_file_bucket_no_audit_no_file_available_true(testapp, dummy_request, file_with_external_sheet):
    testapp.patch_json(
        file_with_external_sheet['@id'],
        {
            'status': 'released',
            'no_file_available': True
        }
    )
    dummy_request.registry.settings['pds_public_bucket'] = 'pds_public_bucket_test'
    dummy_request.registry.settings['pds_private_bucket'] = 'pds_private_bucket_test'
    res = testapp.get(file_with_external_sheet['@id'] + '@@index-data')
    errors = res.json['audit']
    errors_list = [error for v in errors.values() for error in v if error['category'] == 'incorrect file bucket']
    assert not errors_list


def test_audit_incorrect_file_bucket_has_audit_no_file_available_false(testapp, dummy_request, file_with_external_sheet):
    testapp.patch_json(
        file_with_external_sheet['@id'],
        {
            'status': 'released',
            'no_file_available': False
        }
    )
    dummy_request.registry.settings['pds_public_bucket'] = 'pds_public_bucket_test'
    dummy_request.registry.settings['pds_private_bucket'] = 'pds_private_bucket_test'
    res = testapp.get(file_with_external_sheet['@id'] + '@@index-data')
    errors = res.json['audit']
    errors_list = [error for v in errors.values() for error in v if error['category'] == 'incorrect file bucket']
    assert errors_list
