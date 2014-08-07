def test_reference_file_by_md5(testapp, file):
    res = testapp.get('/md5:{md5sum}'.format(**file)).follow(status=200)
    assert res.json['@id'] == file['@id']


def test_replaced_file_not_uniqued(testapp, file):
    testapp.patch_json('/{uuid}'.format(**file), {'status': 'replaced'}, status=200)
    testapp.get('/md5:{md5sum}'.format(**file), status=404)
