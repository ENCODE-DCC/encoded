import pytest


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


def test_audit_file_inconsistent_paired_with(testapp, file1, file3):
    testapp.patch_json(file1['@id'], {
                       'run_type': 'paired-ended', 'paired_end': '1', 'paired_with': file3['uuid']})
    testapp.patch_json(file3['@id'], {
                       'run_type': 'paired-ended', 'paired_end': '1'})
    res = testapp.get(file1['@id'] + '@@index-data')
    errors = res.json['audit']
    errors_list = []
    for error_type in errors:
        errors_list.extend(errors[error_type])
    assert any(error['category'] ==
               'inconsistent paired_with' for error in errors_list)
    testapp.patch_json(file1['@id'], {
                       'run_type': 'paired-ended', 'paired_end': '2', 'paired_with': file3['uuid']})
    testapp.patch_json(file3['@id'], {
                       'run_type': 'paired-ended', 'paired_end': '2', 'paired_with': file1['uuid']})
    res2 = testapp.get(file1['@id'] + '@@index-data')
    errors = res2.json['audit']
    errors_list = []
    for error_type in errors:
        errors_list.extend(errors[error_type])
    assert any(error['category'] ==
               'inconsistent paired_with' for error in errors_list)
    testapp.patch_json(file1['@id'], {
                       'run_type': 'paired-ended', 'paired_end': '1'})
    res3 = testapp.get(file1['@id'] + '@@index-data')
    errors = res3.json['audit']
    errors_list = []
    for error_type in errors:
        errors_list.extend(errors[error_type])
    assert all(error['category'] !=
               'inconsistent paired_with' for error in errors_list)


def test_audit_missing_paired_with(testapp, file2, file4):
    testapp.patch_json(file2['@id'], {
                        'run_type': 'paired-ended', 'paired_end': '1'})
    res = testapp.get(file2['@id'] + '@@index-data')
    errors = res.json['audit']
    errors_list = []
    for error_type in errors:
        errors_list.extend(errors[error_type])
    assert any(error['category'] ==
                'missing paired_with' for error in errors_list)
    testapp.patch_json(file2['@id'], {
                        'paired_with': file4['uuid']})
    res2  = testapp.get(file2['@id'] + '@@index-data')
    errors = res2.json['audit']
    errors_list = []
    for error_type in errors:
        errors_list.extend(errors[error_type])
    assert all(error['category'] !=
                'missing paired_with' for error in errors_list)


def test_audit_paired_with_non_fastq(testapp, file1, file6, platform1):
    testapp.patch_json(
        file1['@id'], 
        {
            'run_type': 'paired-ended',
            'paired_end': '1'
        }
    )
    testapp.patch_json(
        file6['@id'], 
        {
            'run_type': 'paired-ended',
            'platform': platform1['uuid'],
            'paired_end': '2',
            'paired_with': file1['uuid']
        }
    )
    res = testapp.get(file1['@id'] + '@@index-data')
    errors = res.json['audit']
    errors_list = []
    for error_type in errors:
        errors_list.extend(errors[error_type])
    assert any(
        error['category'] == 'paired with non-fastq'
        for error in errors_list
    )


def test_audit_paired_with_fastq(testapp, file1, file4):
    testapp.patch_json(
        file1['@id'],
        {
            'run_type': 'paired-ended',
            'paired_end': '1'
        }
    )
    testapp.patch_json(
        file4['@id'], 
        {
            'run_type': 'paired-ended',
            'paired_end': '2',
            'paired_with': file1['uuid']
        }
    )
    res2 = testapp.get(file1['@id'] + '@@index-data')
    errors = res2.json['audit']
    errors_list = []
    for error_type in errors:
        errors_list.extend(errors[error_type])
    assert all(
        error['category'] != 'paired with non-fastq' 
        for error in errors_list
    )


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
    from encoded.types.file import File
    public_s3_statuses = File.public_s3_statuses
    private_s3_statuses = File.private_s3_statuses
    assert public_s3_statuses
    assert private_s3_statuses
    file_schema = testapp.get('/profiles/file.json').json
    file_statuses = file_schema.get('properties', {}).get('status', {}).get('enum')
    assert file_statuses
    file_statuses = [f for f in file_statuses if f not in ['content error', 'upload failed', 'uploading']]
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


def test_audit_uploading_file_no_incorrect_bucket_audit(testapp, dummy_request, file_with_external_sheet):
    testapp.patch_json(
        file_with_external_sheet['@id'],
        {
            'status': 'uploading'
        }
    )
    dummy_request.registry.settings['pds_public_bucket'] = 'pds_public_bucket_test'
    dummy_request.registry.settings['pds_private_bucket'] = 'pds_private_bucket_test'
    res = testapp.get(file_with_external_sheet['@id'] + '@@index-data')
    errors = res.json['audit']
    errors_list = [error for v in errors.values() for error in v if error['category'] == 'incorrect file bucket']
    assert not errors_list


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


def test_audit_read_structure(testapp, file1_2):
    testapp.patch_json(
        file1_2['@id'],
        {
            'read_structure': [{
                'sequence_element': 'adapter',
                'start': -5,
                'end': -1
            }]
        }
    )
    res = testapp.get(file1_2['@id'] + '@@index-data')
    errors = [error for v in res.json['audit'].values() for error in v]
    assert all(
        error['category'] != 'invalid read_structure'
        for error in errors
    )
    testapp.patch_json(
        file1_2['@id'],
        {
            'read_structure': [{
                'sequence_element': 'adapter',
                'start': 0,
                'end': 5
            }]
        }
    )
    res = testapp.get(file1_2['@id'] + '@@index-data')
    errors = [error for v in res.json['audit'].values() for error in v]
    assert any(
        error['category'] == 'invalid read_structure'
        and error['detail'].startswith('The read_stucture is 1-based.')
        for error in errors
    )
    testapp.patch_json(
        file1_2['@id'],
        {
            'read_structure': [{
                'sequence_element': 'adapter',
                'start': 1,
                'end': -1
            }]
        }
    )
    res = testapp.get(file1_2['@id'] + '@@index-data')
    errors = [error for v in res.json['audit'].values() for error in v]
    assert any(
        error['category'] == 'invalid read_structure'
        and error['detail'].startswith(
            'The start coordinate is bigger than the end coordinate'
        )
        for error in errors
    )


def test_audit_matching_md5sum(testapp, file7, file6):
    testapp.patch_json(
        file7['@id'],
        {
            'matching_md5sum': [file6['@id']]
        }
    )
    res = testapp.get(file7['@id'] + '@@index-data')
    errors = res.json['audit']
    errors_list = []
    for error_type in errors:
        errors_list.extend(errors[error_type])
    assert any(error['category'] == 'inconsistent matching_md5sum'
               for error in errors_list)

    testapp.patch_json(
        file6['@id'],
        {
            'lab': '/labs/encode-processing-pipeline/',
            'md5sum': '91be74b6e11515394507f4ebfa66d78a',
        }
    )
    res = testapp.get(file7['@id'] + '@@index-data')
    errors = res.json['audit']
    errors_list = []
    for error_type in errors:
        errors_list.extend(errors[error_type])
    assert any(error['category'] == 'matching md5 sums'
               for error in errors_list)


def test_audit_self_matching_md5sum(testapp, file7):
    testapp.patch_json(
        file7['@id'],
        {
            'matching_md5sum': [file7['@id']]
        }
    )
    res = testapp.get(file7['@id'] + '@@index-data')
    errors = res.json['audit']
    errors_list = []
    for error_type in errors:
        errors_list.extend(errors[error_type])
    assert any(error['category'] == 'inconsistent matching_md5sum'
               for error in errors_list)
