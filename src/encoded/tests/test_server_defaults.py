def test_server_defaults(users, anontestapp):
    email = users[0]['email']
    extra_environ={'REMOTE_USER': str(email)}
    res = anontestapp.post_json(
        '/testing_server_default', {}, status=201,
        extra_environ=extra_environ,
    )
    url = res.json['@graph'][0]
    res = anontestapp.get(url, status=200, extra_environ=extra_environ)
    assert res.json['now'].startswith('2')
    assert res.json['user'] == users[0]['@id']
    assert res.json['accession'].startswith('ENCXX')
