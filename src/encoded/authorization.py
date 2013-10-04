from .contentbase import LOCATION_ROOT
CHERRY_LAB_UUID = 'cfb789b8-46f3-4d59-a2b3-adc39e7df93a'


def groupfinder(login, request):
    if '.' not in login:
        return None
    namespace, localname = login.split('.', 1)
    user = None
    # We may get called before the context is found and the root set
    root = request.registry[LOCATION_ROOT]

    if namespace == 'remoteuser':
        if localname in ['TEST', 'IMPORT']:
            return ['group.admin']
        elif localname in ['TEST_SUBMITTER']:
            return ['group.submitter']

    if namespace in ('mailto', 'remoteuser'):
        users = root.by_item_type['user']
        try:
            user = users[localname]
        except KeyError:
            return None

    elif namespace == 'accesskey':
        access_keys = root.by_item_type['access_key']
        try:
            access_key = access_keys[localname]
        except KeyError:
            return None
        userid = access_key.properties['user']
        user = root.by_item_type['user'][userid]

    if user is None:
        return None

    principals = ['userid.%s' % user.uuid]
    lab = user.properties.get('lab')
    if lab:
        principals.append('lab.%s' % lab)
    submits_for = user.properties.get('submits_for', [])
    principals.extend('lab.%s' % lab_uuid for lab_uuid in submits_for)
    principals.extend('submits_for.%s' % lab_uuid for lab_uuid in submits_for)
    if CHERRY_LAB_UUID in submits_for:
        principals.append('group.admin')
    return principals
