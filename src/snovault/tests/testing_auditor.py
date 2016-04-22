from snovault.auditor import (
    audit_checker,
    AuditFailure,
)


def includeme(config):
    config.scan('.testing_views')
    config.scan(__name__)


def has_condition1(value, system):
    return value.get('condition1')


@audit_checker('testing_link_source', condition=has_condition1)
def checker1(value, system):
    if not value.get('checker1'):
        return AuditFailure('testchecker', 'Missing checker1')


@audit_checker('testing_link_target')
def testing_link_target_status(value, system):
    if value.get('status') == 'CHECK':
        if not len(value['reverse']):
            return AuditFailure('status', 'Missing reverse items')
