import pytest


def test_file_post(file_no_replicate):
    assert file_no_replicate['biological_replicates'] == []


def test_file_with_replicate_post(file_with_replicate):
    assert file_with_replicate['biological_replicates'] == [1]


def test_file_with_derived_from_post(testapp, file_with_derived):
    assert file_with_derived['biological_replicates'] == [1]


def test_file_no_assembly(testapp, file_no_assembly, file_with_replicate):
    res = testapp.post_json('/file', file_no_assembly, expect_errors=True)
    assert res.status_code == 422
    res = testapp.patch_json(file_with_replicate['@id'],
                             {'file_format': 'fastq', 'output_type': 'reads'},
                             expect_errors=True)
    assert res.status_code == 422
    file_no_assembly['file_format'] = 'bigBed'
    file_no_assembly['file_format_type'] = 'narrowPeak'
    file_no_assembly['output_type'] = 'peaks'
    res = testapp.post_json('/file', file_no_assembly, expect_errors=True)
    assert res.status_code == 422


def test_not_content_error_without_message_ok(testapp, file_no_error):
    # status != content error, so an error detail message is not required.
    res = testapp.post_json('/file', file_no_error, expect_errors=False)
    assert res.status_code == 201


def test_content_error_without_message_bad(testapp, file_content_error):
    # status == content error, so an error detail message is required.
    res = testapp.post_json('/file', file_content_error, expect_errors=True)
    assert res.status_code == 422


def test_content_error_with_message_ok(testapp, file_content_error):
    # status == content error and we have a message, yay!
    file_content_error.update({'content_error_detail': 'Pipeline says error'})
    res = testapp.post_json('/file', file_content_error, expect_errors=False)
    assert res.status_code == 201


def test_not_content_error_with_message_bad(testapp, file_no_error):
    # We shouldn't use the error detail property if status != content error
    file_no_error.update({'content_error_detail': 'I am not the pipeline, I cannot use this.'})
    res = testapp.post_json('/file', file_no_error, expect_errors=True)
    assert res.status_code == 422


def test_with_paired_end_1_2(testapp, file_no_error):
    # only sra files should be allowed to have paired_end == 1,2
    file_no_error.update({'paired_end': '1,2'})
    res = testapp.post_json('/file', file_no_error, expect_errors=True)
    assert res.status_code == 422
    file_no_error.update({'file_format': 'sra'})
    res = testapp.post_json('/file', file_no_error, expect_errors=True)
    assert res.status_code == 201


def test_fastq_no_platform(testapp, file_no_platform, platform1):
    res = testapp.post_json('/file', file_no_platform, expect_errors=True)
    assert res.status_code == 422
    file_no_platform.update({'platform': platform1['uuid']})
    res = testapp.post_json('/file', file_no_platform, expect_errors=True)
    assert res.status_code == 201


def test_with_run_type_no_paired_end(testapp, file_no_paired_end):
    res = testapp.post_json('/file', file_no_paired_end, expect_errors=True)
    assert res.status_code == 422
    file_no_paired_end.update({'paired_end': '1'})
    res = testapp.post_json('/file', file_no_paired_end, expect_errors=True)
    assert res.status_code == 201


def test_with_wrong_date_created(testapp, file_with_bad_date_created):
    res = testapp.post_json('/file', file_with_bad_date_created, expect_errors=True)
    assert res.status_code == 422


def test_no_file_available_md5sum(testapp, file_no_error):
    # Removing the md5sum from a file should not be allowed if the file exists
    res = testapp.post_json('/file', file_no_error, expect_errors=True)
    assert res.status_code == 201

    item = file_no_error.copy()
    item.pop('md5sum', None)
    res = testapp.post_json('/file', item, expect_errors=True)
    assert res.status_code == 422

    item = file_no_error.copy()
    item.pop('md5sum', None)
    item.update({'no_file_available': True})
    res = testapp.post_json('/file', item, expect_errors=True)
    assert res.status_code == 201

    item.update({'no_file_available': False})
    res = testapp.post_json('/file', item, expect_errors=True)
    assert res.status_code == 422


def test_no_file_available_file_size(testapp, file_no_error):
    # Removing the file_size from a file should not be allowed if the file exists
    # and in one of the following states "in progress",  "revoked", "archived", "released"
    item = file_no_error.copy()
    item.update({'status': 'upload failed'})
    item.update({'no_file_available': False})
    item.update({'md5sum': '136e501c4bacf3aab87debab20d76648'})
    res = testapp.post_json('/file', item, expect_errors=True)
    assert res.status_code == 201

    item = file_no_error.copy()
    item.pop('file_size', None)
    res = testapp.post_json('/file', item, expect_errors=True)
    assert res.status_code == 422

    item = file_no_error.copy()
    item.pop('file_size', None)
    item.update({'no_file_available': False})
    res = testapp.post_json('/file', item, expect_errors=True)
    assert res.status_code == 422

    item = file_no_error.copy()
    item.pop('file_size', None)
    item.update({'status': 'upload failed'})
    res = testapp.post_json('/file', item, expect_errors=True)
    assert res.status_code == 201

    item = file_no_error.copy()
    item.pop('file_size', None)
    item.pop('md5sum', None)
    item.update({'no_file_available': True})
    res = testapp.post_json('/file', item, expect_errors=True)
    assert res.status_code == 201


def test_revoke_detail(testapp, file_with_bad_revoke_detail):
    res = testapp.post_json('/file', file_with_bad_revoke_detail, expect_errors=True)
    assert res.status_code == 422
    file_with_bad_revoke_detail.update({'status': 'revoked'})
    res = testapp.post_json('/file', file_with_bad_revoke_detail, expect_errors=True)
    assert res.status_code == 201


def test_read_name_details(testapp, file_no_error, file_good_bam):
    file = testapp.post_json('/file', file_no_error).json['@graph'][0]
    testapp.patch_json(
        file['@id'], {'read_name_details': {
            'flowcell_id_location': 2,
            'barcode_location': 5}
        },
        status=200)
    file = testapp.post_json('/file', file_good_bam).json['@graph'][0]
    testapp.patch_json(
        file['@id'], {'read_name_details': {
            'flowcell_id_location': 2,
            'barcode_location': 5}
        },
        status=422)


def test_processed_output_raw_format(testapp, file_processed_output_raw_format):
    res = testapp.post_json('/file', file_processed_output_raw_format, expect_errors=True)
    assert res.status_code == 422
    file_processed_output_raw_format.update({'output_type': 'reads'})
    res = testapp.post_json('/file', file_processed_output_raw_format, expect_errors=True)
    assert res.status_code == 201


def test_raw_output_processed_format(testapp, file_raw_output_processed_format):
    res = testapp.post_json('/file', file_raw_output_processed_format, expect_errors=True)
    assert res.status_code == 422
    file_raw_output_processed_format.update({'output_type': 'alignments'})
    res = testapp.post_json('/file', file_raw_output_processed_format, expect_errors=True)
    assert res.status_code == 201


def test_restriction_map(testapp, file_restriction_map):
    res = testapp.post_json('/file', file_restriction_map, expect_errors=True)
    assert res.status_code == 422
    file_restriction_map.update({'restriction_enzymes': ['MboI', 'MboI']})
    res = testapp.post_json('/file', file_restriction_map, expect_errors=True)
    assert res.status_code == 422
    file_restriction_map.update({'restriction_enzymes': []})
    res = testapp.post_json('/file', file_restriction_map, expect_errors=True)
    assert res.status_code == 422
    file_restriction_map.update({
        'output_type': 'male genome reference',
        'restriction_enzymes': ['MboI']
    })
    res = testapp.post_json('/file', file_restriction_map, expect_errors=True)
    assert res.status_code == 422
    file_restriction_map.update({'output_type': 'restriction enzyme site locations'})
    res = testapp.post_json('/file', file_restriction_map, expect_errors=True)
    assert res.status_code == 201


def test_database_annotation_requirement(testapp, file_no_genome_annotation):
    testapp.post_json('/file', file_no_genome_annotation, status=422)
    file_no_genome_annotation.update({'genome_annotation': 'V24'})
    testapp.post_json('/file', file_no_genome_annotation, status=201)


def test_database_output_type_requirement(testapp, file_database_output_type):
    testapp.post_json('/file', file_database_output_type, status=422)
    file_database_output_type.update({'output_type': 'transcriptome index'})
    testapp.post_json('/file', file_database_output_type, status=201)


def test_matching_md5sum(testapp, file_no_error, file_good_bam):
    file = testapp.post_json('/file', file_good_bam).json['@graph'][0]
    file_no_error.update({'matching_md5sum': [file['@id']]})
    res = testapp.post_json('/file', file_no_error, expect_errors=False)
    assert res.status_code == 201


def test_no_runtype_readlength_dependency(testapp, file_no_runtype_readlength, platform4):
    testapp.post_json('/file', file_no_runtype_readlength, status=422)
    file_no_runtype_readlength.update({'platform': platform4['@id']})
    testapp.post_json('/file', file_no_runtype_readlength, status=201)


def test_subreads_bam(testapp, file_subreads):
    res = testapp.post_json('/file', file_subreads, expect_errors=False)
    assert res.status_code == 201


def test_no_runtype_dependency(testapp, file_no_runtype, platform3):
    testapp.post_json('/file', file_no_runtype, status=422)
    file_no_runtype.update({'run_type': 'single-ended'})
    testapp.post_json('/file', file_no_runtype, status=201)

def test_hotspots_prefix_dependency_requirement(testapp, file_hotspots_prefix, file_hotspots1_reference):
    testapp.post_json('/file', file_hotspots_prefix, status=422)
    file_hotspots_prefix.update({'output_type': 'hotspots1 reference'})
    testapp.post_json('/file', file_hotspots_prefix, status=201)
    testapp.post_json('/file', file_hotspots1_reference, status=422)
    file_hotspots1_reference.update({'hotspots_prefix': 'mm10'})
    testapp.post_json('/file', file_hotspots1_reference, status=201)


def test_subreads_bam_replicate(testapp, file_subreads):
    item = file_subreads.copy()
    item.pop('replicate', None)
    testapp.post_json('/file', item, status=422)


def test_nanopore_signal_platform(testapp, file_nanopore_signal):
    testapp.post_json('/file', file_nanopore_signal, status=201)
    file_nanopore_signal.pop('replicate', None)
    testapp.post_json('/file', file_nanopore_signal, status=422)


def test_R2C2_subreads_bam_replicate(testapp, file_subreads, platform4):
    item = file_subreads.copy()
    item.update({'output_type': 'R2C2 subreads',
                 'file_format': 'fastq',
                 'platform': platform4['@id']})
    testapp.post_json('/file', item, status=201)
    item.pop('replicate', None)
    testapp.post_json('/file', item, status=422)


def test_no_readlength_dependency(testapp, file_no_readlength, platform5):
    testapp.post_json('/file', file_no_readlength, status=422)
    file_no_readlength.update({'platform': platform5['@id']})
    testapp.post_json('/file', file_no_readlength, status=201)
