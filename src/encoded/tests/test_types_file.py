import pytest
from encoded.types.file import File


@pytest.mark.parametrize("file_status", [
    status
    for status in File.public_s3_statuses
])
def test_public_file_has_google_transfer_metadata(testapp, file, file_status):
    testapp.patch_json(file['@id'], {'status': file_status})
    res = testapp.get(file['@id'])
    assert 'google_transfer' in res.json


@pytest.mark.parametrize("file_status", [
    status
    for status in File.private_s3_statuses
    if status != 'replaced'
])
def test_private_file_does_not_have_google_transfer_metadata(testapp, file, file_status):
    testapp.patch_json(file['@id'], {'status': file_status})
    res = testapp.get(file['@id'])
    assert 'google_transfer' not in res.json
