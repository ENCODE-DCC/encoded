import pytest
from encoded.types.file import File
from moto import (
    mock_sts,
    mock_s3
)


def test_get_external_sheet(root, file_with_external_sheet):
    file_item = root.get_by_uuid(file_with_external_sheet['uuid'])
    external = file_item._get_external_sheet()
    assert external.get('key') == 'xyz.bed'
    assert external.get('bucket') == 'test_file_bucket'


def test_set_external_sheet(root, file_with_external_sheet):
    file_item = root.get_by_uuid(file_with_external_sheet['uuid'])
    external = file_item._get_external_sheet()
    assert external.get('key') == 'xyz.bed'
    assert external.get('bucket') == 'test_file_bucket'
    new_external = {'bucket': 'new_test_file_bucket', 'key': 'abc.bam'}
    file_item._set_external_sheet(new_external)
    external = file_item._get_external_sheet()
    assert external.get('key') == 'abc.bam'
    assert external.get('bucket') == 'new_test_file_bucket'


@pytest.mark.parametrize("file_status", [
    status
    for status in File.public_s3_statuses
])
def test_public_file_not_in_correct_bucket(testapp, root, dummy_request, file_with_external_sheet, file_status):
    testapp.patch_json(
        file_with_external_sheet['@id'],
        {
            'status': file_status
        }
    )
    dummy_request.registry.settings['pds_public_bucket'] = 'pds_public_bucket_test'
    dummy_request.registry.settings['pds_private_bucket'] = 'pds_private_bucket_test'
    file_item = root.get_by_uuid(file_with_external_sheet['uuid'])
    external = file_item._get_external_sheet()
    assert external.get('bucket') == 'test_file_bucket'
    result, current_path, destination_path = file_item._file_in_correct_bucket(dummy_request)
    assert result is False
    assert current_path == 's3://test_file_bucket/xyz.bed'
    assert destination_path == 's3://pds_public_bucket_test/xyz.bed'


def test_file_in_correct_bucket_no_external_sheet(root, dummy_request, file_with_no_external_sheet):
    dummy_request.registry.settings['pds_public_bucket'] = 'pds_public_bucket_test'
    dummy_request.registry.settings['pds_private_bucket'] = 'pds_private_bucket_test'
    file_item = root.get_by_uuid(file_with_no_external_sheet['uuid'])
    result, current_path, destination_path = file_item._file_in_correct_bucket(dummy_request)
    assert result is True
    assert current_path is None
    assert destination_path is None


@pytest.mark.parametrize("file_status", [
    status
    for status in File.public_s3_statuses
])
def test_public_file_in_correct_bucket(testapp, root, dummy_request, file_with_external_sheet, file_status):
    testapp.patch_json(
        file_with_external_sheet['@id'],
        {
            'status': file_status
        }
    )
    dummy_request.registry.settings['pds_public_bucket'] = 'pds_public_bucket_test'
    dummy_request.registry.settings['pds_private_bucket'] = 'pds_private_bucket_test'
    file_item = root.get_by_uuid(file_with_external_sheet['uuid'])
    file_item._set_external_sheet({'bucket': 'pds_public_bucket_test'})
    external = file_item._get_external_sheet()
    assert external.get('bucket') == 'pds_public_bucket_test'
    result, current_path, destination_path = file_item._file_in_correct_bucket(dummy_request)
    assert result is True
    assert current_path == destination_path == 's3://pds_public_bucket_test/xyz.bed'


@pytest.mark.parametrize("file_status", [
    status
    for status in File.private_s3_statuses
])
def test_private_file_not_in_correct_bucket(testapp, root, dummy_request, file_with_external_sheet, file_status):
    testapp.patch_json(
        file_with_external_sheet['@id'],
        {
            'status': file_status
        }
    )
    dummy_request.registry.settings['pds_public_bucket'] = 'pds_public_bucket_test'
    dummy_request.registry.settings['pds_private_bucket'] = 'pds_private_bucket_test'
    file_item = root.get_by_uuid(file_with_external_sheet['uuid'])
    external = file_item._get_external_sheet()
    assert external.get('bucket') == 'test_file_bucket'
    result, current_path, destination_path = file_item._file_in_correct_bucket(dummy_request)
    assert result is False
    assert current_path == 's3://test_file_bucket/xyz.bed'
    assert destination_path == 's3://pds_private_bucket_test/xyz.bed'


@pytest.mark.parametrize("file_status", [
    status
    for status in File.private_s3_statuses
])
def test_private_file_in_correct_bucket(testapp, root, dummy_request, file_with_external_sheet, file_status):
    testapp.patch_json(
        file_with_external_sheet['@id'],
        {
            'status': file_status
        }
    )
    dummy_request.registry.settings['pds_public_bucket'] = 'pds_public_bucket_test'
    dummy_request.registry.settings['pds_private_bucket'] = 'pds_private_bucket_test'
    file_item = root.get_by_uuid(file_with_external_sheet['uuid'])
    file_item._set_external_sheet({'bucket': 'pds_private_bucket_test'})
    external = file_item._get_external_sheet()
    assert external.get('bucket') == 'pds_private_bucket_test'
    result, current_path, destination_path = file_item._file_in_correct_bucket(dummy_request)
    assert result is True
    assert current_path == destination_path == 's3://pds_private_bucket_test/xyz.bed'


def test_restricted_or_missing_file_in_private_bucket(testapp, root, dummy_request, file_with_external_sheet):
    testapp.patch_json(
        file_with_external_sheet['@id'],
        {
            'status': 'released',
            'restricted': True
        }
    )
    dummy_request.registry.settings['pds_public_bucket'] = 'pds_public_bucket_test'
    dummy_request.registry.settings['pds_private_bucket'] = 'pds_private_bucket_test'
    file_item = root.get_by_uuid(file_with_external_sheet['uuid'])
    file_item._set_external_sheet({'bucket': 'pds_private_bucket_test'})
    external = file_item._get_external_sheet()
    assert external.get('bucket') == 'pds_private_bucket_test'
    result, current_path, destination_path = file_item._file_in_correct_bucket(dummy_request)
    assert result is True
    assert current_path == destination_path == None


@mock_sts
@mock_s3
@pytest.mark.parametrize("file_status", [
    status
    for status in File.public_s3_statuses
])
def test_public_file_has_cloud_metadata(testapp, file_with_external_sheet, file_status):
    testapp.patch_json(file_with_external_sheet['@id'], {'status': file_status})
    res = testapp.get(file_with_external_sheet['@id'])
    assert 'cloud_metadata' in res.json
    cm = res.json['cloud_metadata']
    assert 'test_file_bucket' in cm['url']
    assert 'xyz.bed' in cm['url']
    assert cm['md5sum_base64'] == '1B2M2Y8AsgTpgAmY7PhCfg=='
    assert cm['file_size'] == 34


def test_public_restricted_file_does_not_have_cloud_metadata(testapp, file_with_external_sheet):
    testapp.patch_json(
        file_with_external_sheet['@id'],
        {
            'status': 'released',
            'restricted': True
        }
    )
    res = testapp.get(file_with_external_sheet['@id'])
    assert 'cloud_metadata' not in res.json


def test_public_no_file_available_file_does_not_have_cloud_metadata(testapp, file_with_external_sheet):
    testapp.patch_json(
        file_with_external_sheet['@id'],
        {
            'status': 'released',
            'no_file_available': True
        }
    )
    res = testapp.get(file_with_external_sheet['@id'])
    assert 'cloud_metadata' not in res.json


def test_private_no_file_available_file_does_not_have_cloud_metadata(testapp, file_with_external_sheet):
    testapp.patch_json(
        file_with_external_sheet['@id'],
        {
            'status': 'in progress',
            'no_file_available': True
        }
    )
    res = testapp.get(file_with_external_sheet['@id'])
    assert 'cloud_metadata' not in res.json


@pytest.mark.parametrize("file_status", [
    status
    for status in File.private_s3_statuses
    if status != 'replaced'
])
def test_private_file_does_have_cloud_metadata(testapp, file_with_external_sheet, file_status):
    testapp.patch_json(file_with_external_sheet['@id'], {'status': file_status})
    res = testapp.get(file_with_external_sheet['@id'])
    assert 'cloud_metadata' in res.json


def test_public_file_with_no_external_sheet_no_cloud_metadata(testapp, file):
    testapp.patch_json(file['@id'], {'status': 'released'})
    res = testapp.get(file['@id'])
    assert 'cloud_metadata' not in res.json


@pytest.mark.parametrize("file_status", [
    status
    for status in File.public_s3_statuses
])
def test_public_file_has_s3_uri(testapp, file_with_external_sheet, file_status):
    testapp.patch_json(file_with_external_sheet['@id'], {'status': file_status})
    res = testapp.get(file_with_external_sheet['@id'])
    assert 's3_uri' in res.json
    assert res.json['s3_uri'] == 's3://test_file_bucket/xyz.bed'


@pytest.mark.parametrize("file_status", [
    status
    for status in File.private_s3_statuses
    if status != 'replaced'
])
def test_private_file_does_have_s3_uri(testapp, file_with_external_sheet, file_status):
    testapp.patch_json(file_with_external_sheet['@id'], {'status': file_status})
    res = testapp.get(file_with_external_sheet['@id'])
    assert 's3_uri' in res.json


def test_public_file_no_external_sheet_no_s3_uri(testapp, file):
    testapp.patch_json(file['@id'], {'status': 'released'})
    res = testapp.get(file['@id'])
    assert 's3_uri' not in res.json


def test_public_restricted_file_does_not_have_s3_uri(testapp, file_with_external_sheet):
    testapp.patch_json(
        file_with_external_sheet['@id'],
        {
            'status': 'released',
            'restricted': True,
        }
    )
    res = testapp.get(file_with_external_sheet['@id'])
    assert 's3_uri' not in res.json


@pytest.mark.parametrize("file_status", [
    status
    for status in ['uploading','upload failed']
])
def test_encode_files_does_have_s3_uri(testapp, file_with_external_sheet, file_status):
    testapp.patch_json(
        file_with_external_sheet['@id'],
        {
            'status': file_status
        }
    )
    res = testapp.get(file_with_external_sheet['@id'])
    assert 's3_uri' in res.json


def test_encode_files_content_error_does_have_s3_uri(testapp, file_with_external_sheet):
    testapp.patch_json(
        file_with_external_sheet['@id'],
        {
            'status': 'content error',
            'content_error_detail': "Required detail for content error"
        }
    )
    res = testapp.get(file_with_external_sheet['@id'])
    assert 's3_uri' in res.json

    
def test_file_update_bucket_as_admin(testapp, dummy_request, file_with_external_sheet):
    testapp.patch_json(
        file_with_external_sheet['@id'],
        {
            'status': 'released'
        }
    )
    dummy_request.registry.settings['file_upload_bucket'] = 'test_file_bucket'
    dummy_request.registry.settings['pds_public_bucket'] = 'pds_public_bucket_test'
    dummy_request.registry.settings['pds_private_bucket'] = 'pds_private_bucket_test'
    res = testapp.patch_json(file_with_external_sheet['@id'] + '@@update_bucket', {'new_bucket': 'pds_public_bucket_test'})
    assert res.json['old_bucket'] == 'test_file_bucket'
    assert res.json['new_bucket'] == 'pds_public_bucket_test'


def test_file_update_bucket_as_admin_unkown_bucket(testapp, dummy_request, file_with_external_sheet):
    testapp.patch_json(
        file_with_external_sheet['@id'],
        {
            'status': 'released'
        }
    )
    dummy_request.registry.settings['file_upload_bucket'] = 'test_file_bucket'
    dummy_request.registry.settings['pds_public_bucket'] = 'pds_public_bucket_test'
    dummy_request.registry.settings['pds_private_bucket'] = 'pds_private_bucket_test'
    testapp.patch_json(
        file_with_external_sheet['@id'] + '@@update_bucket',
        {'new_bucket': 'unknown bucket'},
        status=422
    )


def test_file_update_bucket_as_admin_unkown_bucket_with_force(testapp, dummy_request, file_with_external_sheet):
    testapp.patch_json(
        file_with_external_sheet['@id'],
        {
            'status': 'released'
        }
    )
    dummy_request.registry.settings['file_upload_bucket'] = 'test_file_bucket'
    dummy_request.registry.settings['pds_public_bucket'] = 'pds_public_bucket_test'
    dummy_request.registry.settings['pds_private_bucket'] = 'pds_private_bucket_test'
    res = testapp.patch_json(file_with_external_sheet['@id'] + '@@update_bucket?force=true', {'new_bucket': 'unknown bucket'})
    assert res.json['old_bucket'] == 'test_file_bucket'
    assert res.json['new_bucket'] == 'unknown bucket'


def test_file_update_bucket_as_submitter(submitter_testapp, dummy_request, file_with_external_sheet):
    dummy_request.registry.settings['file_upload_bucket'] = 'test_file_bucket'
    dummy_request.registry.settings['pds_public_bucket'] = 'pds_public_bucket_test'
    dummy_request.registry.settings['pds_private_bucket'] = 'pds_private_bucket_test'
    submitter_testapp.patch_json(
        file_with_external_sheet['@id'] + '@@update_bucket',
        {'new_bucket': 'unknown bucket'},
        status=403
    )


@mock_s3
@mock_sts
def test_file_reset_file_upload_bucket_on_upload_credentials(testapp, root, dummy_request, file_with_external_sheet):
    dummy_request.registry.settings['file_upload_bucket'] = 'test_file_bucket'
    dummy_request.registry.settings['pds_public_bucket'] = 'pds_public_bucket_test'
    dummy_request.registry.settings['pds_private_bucket'] = 'pds_private_bucket_test'
    res = testapp.patch_json(file_with_external_sheet['@id'] + '@@update_bucket', {'new_bucket': 'pds_public_bucket_test'})
    file_item = root.get_by_uuid(file_with_external_sheet['uuid'])
    external = file_item._get_external_sheet()
    assert external.get('key') == 'xyz.bed'
    assert external.get('bucket') == 'pds_public_bucket_test'
    testapp.patch_json(
        file_with_external_sheet['@id'],
        {
            'status': 'uploading'
        }
    )
    file_item = root.get_by_uuid(file_with_external_sheet['uuid'])
    res = testapp.post_json(file_with_external_sheet['@id'] + '@@upload', {})
    file_item = root.get_by_uuid(file_with_external_sheet['uuid'])
    external = file_item._get_external_sheet()
    assert external.get('bucket') == 'test_file_bucket'
    assert res.json['@graph'][0]['upload_credentials']['upload_url'] == 's3://test_file_bucket/xyz.bed'


def test_file_embedded_annotation_properties(testapp, file_ccre,
                                             annotation_ccre,
                                             file_ccre_2, file_ccre_3):
    # https://encodedcc.atlassian.net/browse/ENCD-5806
    testapp.patch_json(
        annotation_ccre['@id'],
        {
            'annotation_subtype': 'CTCF-only'
        }
    )
    testapp.patch_json(file_ccre['@id'], {'derived_from': [file_ccre_2['@id'], file_ccre_3['@id']]})
    res = testapp.get(file_ccre['@id'] + '@@index-data')
    assert res.json['object']['annotation_subtype'] == 'CTCF-only'
    assert res.json['object']['biochemical_inputs'] == ['cDHS', 'rDHS']


def test_file_show_azure_uri():
    from encoded.types.file import show_azure_uri
    for status in File.public_s3_statuses:
        assert show_azure_uri(
            's3://encode-public/2020/09/26/71e9637f-bbcb-4e4b-9d92-d3acdda4bb7b/ENCFF841DAP.bigWig',
            status,
        )
        assert not show_azure_uri(
            None,
            status,
        )
    for status in File.private_s3_statuses:
        assert not show_azure_uri(
            's3://encode-public/2020/09/26/71e9637f-bbcb-4e4b-9d92-d3acdda4bb7b/ENCFF841DAP.bigWig',
            status,
        )
        assert not show_azure_uri(
            None,
            status,
        )


def test_get_key_from_s3_uri():
    from encoded.types.file import get_key_from_s3_uri
    s3_uri = 's3://encode-public/2020/09/26/71e9637f-bbcb-4e4b-9d92-d3acdda4bb7b/ENCFF841DAP.bigWig'
    assert (
        get_key_from_s3_uri(s3_uri) == '2020/09/26/71e9637f-bbcb-4e4b-9d92-d3acdda4bb7b/ENCFF841DAP.bigWig'
    )


def test_convert_s3_uri_to_azure_uri():
    from encoded.types.file import convert_s3_uri_to_azure_uri
    s3_uri = 's3://encode-public/2020/09/26/71e9637f-bbcb-4e4b-9d92-d3acdda4bb7b/ENCFF841DAP.bigWig'
    azure_uri = convert_s3_uri_to_azure_uri(s3_uri)
    assert azure_uri == (
        'https://datasetencode.blob.core.windows.net/dataset/'
        '2020/09/26/71e9637f-bbcb-4e4b-9d92-d3acdda4bb7b/ENCFF841DAP.bigWig'
        '?sv=2019-10-10&si=prod&sr=c&sig=9qSQZo4ggrCNpybBExU8SypuUZV33igI11xw0P7rB3c%3D'
    )


@pytest.mark.parametrize(
    'status',
    [
        status
        for status in File.public_s3_statuses
    ]
)
def test_file_public_file_has_azure_uri(testapp, file_with_external_sheet, status):
    testapp.patch_json(
        file_with_external_sheet['@id'],
        {
            'status': status
        }
    )
    r = testapp.get(
        file_with_external_sheet['@id']
    )
    assert 'azure_uri' in r.json
    assert r.json['azure_uri'] == (
        'https://datasetencode.blob.core.windows.net/dataset/'
        'xyz.bed'
        '?sv=2019-10-10&si=prod&sr=c&sig=9qSQZo4ggrCNpybBExU8SypuUZV33igI11xw0P7rB3c%3D'
    )


@pytest.mark.parametrize(
    'status',
    [
        status
        for status in File.private_s3_statuses
        if status != 'replaced'
    ]
)
def test_file_private_file_does_not_have_azure_uri(testapp, file_with_external_sheet, status):
    testapp.patch_json(
        file_with_external_sheet['@id'],
        {
            'status': status
        }
    )
    r = testapp.get(
        file_with_external_sheet['@id']
    )
    assert 'azure_uri' not in r.json


def test_file_without_external_sheet_does_not_have_azure_uri(testapp, file):
    testapp.patch_json(file['@id'], {'status': 'released'})
    r = testapp.get(file['@id'])
    assert 'azure_uri' not in r.json


def test_file_restricted_file_does_not_have_azure_uri(testapp, file_with_external_sheet):
    testapp.patch_json(
        file_with_external_sheet['@id'],
        {
            'status': 'released',
            'restricted': True,
        }
    )
    r = testapp.get(file_with_external_sheet['@id'])
    assert 'azure_uri' not in r.json


def test_file_origin_batches(testapp, file_bam_1_1, replicate_1_1, base_library, file_fastq_control_chip, biosample_human_1, a549):
    # Origin batches directly from fastq
    testapp.patch_json(
        biosample_human_1['@id'],
        {
            'biosample_ontology': a549['uuid']
        }
    )
    res = testapp.get(file_fastq_control_chip['@id'] + '@@index-data')
    origin_batches = res.json['object']['origin_batches']
    assert biosample_human_1['@id'] in origin_batches
    # Origin batches from derived_from
    testapp.patch_json(
        base_library['@id'],
        {
            'biosample': biosample_human_1['uuid']
        }
    )
    testapp.patch_json(
        replicate_1_1['@id'],
        {
            'library': base_library['uuid']
        }
    )
    res = testapp.get(file_bam_1_1['@id'] + '@@index-data')
    origin_batches = res.json['object']['origin_batches']
    assert biosample_human_1['@id'] in origin_batches


def test_file_replicates_1(testapp, file_bam):
    r = testapp.get(file_bam['@id'] + '?frame=embedded') 
    assert r.json['biological_replicates'] == [1]
    assert r.json['biological_replicates_formatted'] == "Rep 1"


def test_file_replicates_2_3(testapp, file_bed_IDR_peaks_2_atac):
    r = testapp.get(file_bed_IDR_peaks_2_atac['@id'] + '?frame=embedded') 
    assert r.json['biological_replicates'] == [2, 3]
    assert r.json['biological_replicates_formatted'] == "Rep 2, Rep 3"


def test_file_raw_data(testapp, file_fastq_2):
    res = testapp.get(file_fastq_2['@id'] + '@@index-data')
    assert res.json['object']['processed'] == False


def test_file_processed_with_assembly(testapp, GRCh38_file):
    res = testapp.get(GRCh38_file['@id'] + '@@index-data')
    assert res.json['object']['processed'] == True
