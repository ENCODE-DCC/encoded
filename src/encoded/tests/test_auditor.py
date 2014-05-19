import pytest


def string_returning_checker(value, system):
    if not value.get('checker1'):
        return 'Missing checker1'


def raising_checker(value, system):
    from ..auditor import AuditFailure
    if not value.get('checker1'):
        raise AuditFailure('testchecker', 'Missing checker1')


def string_yielding_checker(value, system):
    if not value.get('checker1'):
        yield 'Missing checker1'


def yielding_checker(value, system):
    from ..auditor import AuditFailure
    if not value.get('checker1'):
        yield AuditFailure('testchecker', 'Missing checker1')


@pytest.fixture(params=[
    string_returning_checker,
    raising_checker,
    string_yielding_checker,
    string_returning_checker
])
def auditor(request):
    from ..auditor import Auditor
    auditor = Auditor()
    auditor.add_audit_checker(request.param, 'test', 'testchecker')
    return auditor


def test_audit_pass(auditor):
    value = {'checker1': True}
    errors = auditor.audit(value, 'test')
    assert errors == []


def test_audit_failure(auditor):
    value = {}
    error, = auditor.audit(value, 'test')
    assert error.detail == 'Missing checker1'
    assert error.category == 'testchecker'
    assert error.level == 0


def test_declarative_config():
    from pyramid.config import Configurator
    config = Configurator()
    config.include('..auditor')
    config.include('.testing_auditor')
    config.commit()

    auditor = config.registry['auditor']
    value = {}
    error, = auditor.audit(value, 'testing_auditor')
    assert error.detail == 'Missing checker1'
    assert error.category == 'testchecker'
    assert error.level == 0


def test_link_target_audit_fail(testapp):
    target = {'uuid': '775795d3-4410-4114-836b-8eeecf1d0c2f', 'status': 'CHECK'}
    testapp.post_json('/testing_link_target', target, status=201)
    res = testapp.get('/%s/@@index-data' % target['uuid']).maybe_follow()
    error, = res.json['audit']
    assert error['detail'] == 'Missing reverse items'
    assert error['category'] == 'status'
    assert error['level'] == 0


def test_link_target_audit_pass(testapp):
    target = {'uuid': '775795d3-4410-4114-836b-8eeecf1d0c2f', 'status': 'CHECK'}
    testapp.post_json('/testing_link_target', target, status=201)
    source = {'uuid': '16157204-8c8f-4672-a1a4-14f4b8021fcd', 'target': target['uuid']}
    testapp.post_json('/testing_link_source', source, status=201)
    res = testapp.get('/%s/@@index-data' % target['uuid']).maybe_follow()
    assert res.json['audit'] == []
