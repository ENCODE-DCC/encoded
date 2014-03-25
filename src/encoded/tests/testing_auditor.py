from ..auditor import audit_checker


def includeme(config):
    config.scan(__name__)


@audit_checker('testing_auditor', 'testchecker')
def checker1(value, system):
    if not value.get('checker1'):
        return 'Missing checker1'


@audit_checker('testing_link_target', 'status')
def testing_link_target_status(value, system):
    if value.get('status') == 'CHECK':
        if not len(value['reverse']):
            return 'Missing reverse items'
