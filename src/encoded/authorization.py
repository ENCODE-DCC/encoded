from .contentbase import LOCATION_ROOT


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
        elif localname in ['TEST_AUTHENTICATED', 'EMBED', 'INDEXER']:
            return []

    if namespace in ('mailto', 'remoteuser', 'persona'):
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

    user_properties = user.properties

    if user_properties.get('status') in ('DELETED', 'DISABLED'):
        return None

    principals = ['userid.%s' % user.uuid]
    lab = user_properties.get('lab')
    if lab:
        principals.append('lab.%s' % lab)
    submits_for = user_properties.get('submits_for', [])
    principals.extend('lab.%s' % lab_uuid for lab_uuid in submits_for)
    principals.extend('submits_for.%s' % lab_uuid for lab_uuid in submits_for)
    if submits_for:
        principals.append('group.submitter')
    groups = user_properties.get('groups', [])
    principals.extend('group.%s' % group for group in groups)
    return principals
