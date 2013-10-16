from pytest import fixture

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
    assert item['accession'].startswith('ENCAB')

    anontestapp.patch_json(
        res.location, {}, status=200,
        extra_environ=extra_environ,
    )


@fixture(scope='session')
def test_accession_app(request, check_constraints, zsa_savepoints, app_settings):
    from encoded import main
    app_settings = app_settings.copy()
    app_settings['accession_factory'] = 'encoded.server_defaults.test_accession'
    return main({}, **app_settings)


@fixture
def test_accession_anontestapp(request, test_accession_app, external_tx, zsa_savepoints):
    '''TestApp with JSON accept header.
    '''
    from webtest import TestApp
    environ = {
        'HTTP_ACCEPT': 'application/json',
    }
    return TestApp(test_accession_app, environ)


def test_test_accession_server_defaults(users, test_accession_anontestapp):
    email = users[0]['email']
    extra_environ={'REMOTE_USER': str(email)}
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
