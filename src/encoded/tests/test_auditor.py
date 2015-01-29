import pytest


def raising_checker(value, system):
    from ..auditor import AuditFailure
    if not value.get('checker1'):
        raise AuditFailure('testchecker', 'Missing checker1')


def returning_checker(value, system):
    from ..auditor import AuditFailure
    if not value.get('checker1'):
        return AuditFailure('testchecker', 'Missing checker1')


def yielding_checker(value, system):
    from ..auditor import AuditFailure
    if not value.get('checker1'):
        yield AuditFailure('testchecker', 'Missing checker1')


def has_condition1(value, system):
    return value.get('condition1')


@pytest.fixture(params=[
    raising_checker,
    returning_checker,
    yielding_checker,
])
def auditor(request):
    from ..auditor import Auditor
    auditor = Auditor()
    auditor.add_audit_checker(request.param, 'test')
    return auditor


@pytest.fixture
def auditor_conditions():
    from ..auditor import Auditor
    auditor = Auditor()
    auditor.add_audit_checker(raising_checker, 'test', has_condition1)
    return auditor


def test_audit_pass(auditor, monkeypatch):
    value = {'checker1': True}
    monkeypatch.setattr("encoded.auditor.embed", lambda request, path: value)
    errors = auditor.audit(request=None, path='/foo', types='test')
    assert errors == []


def test_audit_failure(auditor, monkeypatch):
    value = {}
    monkeypatch.setattr("encoded.auditor.embed", lambda request, path: value)
    error, = auditor.audit(request=None, path='/foo', types='test')
    assert error['detail'] == 'Missing checker1'
    assert error['category'] == 'testchecker'
    assert error['level'] == 0
    assert error['path'] == '/foo'


def test_audit_conditions(auditor_conditions, monkeypatch):
    value = {}
    monkeypatch.setattr("encoded.auditor.embed", lambda request, path: value)
    assert auditor_conditions.audit(request=None, path='/foo', types='test') == []
    value = {'condition1': True}
    error, = auditor_conditions.audit(request=None, path='/foo', types='test')
    assert error['detail'] == 'Missing checker1'
    assert error['category'] == 'testchecker'
    assert error['level'] == 0
    assert error['path'] == '/foo'


def test_declarative_config(monkeypatch):
    from pyramid.config import Configurator
    config = Configurator()
    config.include('..auditor')
    config.include('.testing_auditor')
    config.commit()

    auditor = config.registry['auditor']
    value = {'condition1': True}
    monkeypatch.setattr("encoded.auditor.embed", lambda request, path: value)
    error, = auditor.audit(request=None, path='/foo', types='testing_auditor')
    assert error['detail'] == 'Missing checker1'
    assert error['category'] == 'testchecker'
    assert error['level'] == 0
    assert error['path'] == '/foo'


def test_link_target_audit_fail(testapp):
    target = {'uuid': '775795d3-4410-4114-836b-8eeecf1d0c2f', 'status': 'CHECK'}
    testapp.post_json('/testing_link_target', target, status=201)
    res = testapp.get('/%s/@@index-data' % target['uuid']).maybe_follow()
    errors_dict = res.json['audit']
    errors_list = []
    for error_type in errors_dict:
        errors_list.extend(errors_dict[error_type])
    errors = [e for e in errors_list if e['name'] == 'testing_link_target_status']
    error, = errors
    assert error['detail'] == 'Missing reverse items'
    assert error['category'] == 'status'
    assert error['level'] == 0
    assert error['path'] == res.json['object']['@id']


def test_link_target_audit_pass(testapp):
    target = {'uuid': '775795d3-4410-4114-836b-8eeecf1d0c2f', 'status': 'CHECK'}
    testapp.post_json('/testing_link_target', target, status=201)
    source = {'uuid': '16157204-8c8f-4672-a1a4-14f4b8021fcd', 'target': target['uuid']}
    testapp.post_json('/testing_link_source', source, status=201)
    res = testapp.get('/%s/@@index-data' % target['uuid']).maybe_follow()
    errors_dict = res.json['audit']
    errors_list = []
    for error_type in errors_dict:
        errors_list.extend(errors_dict[error_type])
    errors = [e for e in errors_list if e['name'] == 'testing_link_target_status']
    assert errors == []
