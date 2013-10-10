def test_server_defaults(users, anontestapp):
    email = users[0]['email']
    extra_environ={'REMOTE_USER': str(email)}
    res = anontestapp.post_json(
        '/testing_server_default', {}, status=201,
        extra_environ=extra_environ,
    )
    item = res.json['@graph'][0]
    assert item['now'].startswith('2')
    assert item['user'] == users[0]['@id']
    assert item['accession'].startswith('ENCXX')

    anontestapp.patch_json(
        res.location, {}, status=200,
        extra_environ=extra_environ,
    )
