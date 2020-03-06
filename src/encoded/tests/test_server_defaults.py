from pytest import fixture


def test_server_defaults(admin, anontestapp):
    email = admin['email']
    extra_environ = {'REMOTE_USER': str(email)}
    res = anontestapp.post_json(
        '/testing_server_default', {}, status=201,
        extra_environ=extra_environ,
    )
    item = res.json['@graph'][0]
    assert item['now'].startswith('2')
    assert item['user'] == admin['@id']
    assert item['accession'].startswith('ENCAB')

    anontestapp.patch_json(
        res.location, {}, status=200,
        extra_environ=extra_environ,
    )


def test_test_accession_server_defaults(admin, test_accession_anontestapp):
    email = admin['email']
    extra_environ = {'REMOTE_USER': str(email)}
    res = test_accession_anontestapp.post_json(
        '/testing_server_default', {}, status=201,
        extra_environ=extra_environ,
    )
    item = res.json['@graph'][0]
    assert item['accession'].startswith('TSTAB')

    test_accession_anontestapp.patch_json(
        res.location, {}, status=200,
        extra_environ=extra_environ,
    )
