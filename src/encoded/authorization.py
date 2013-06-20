from .contentbase import LOCATION_ROOT
CHERRY_LAB_UUID = 'cfb789b8-46f3-4d59-a2b3-adc39e7df93a'


def groupfinder(login, request):
    if ':' not in login:
        return None
    namespace, localname = login.split(':', 1)
    user = None
    # We may get called before the context is found and the root set
    root = request.registry[LOCATION_ROOT]

    if namespace == 'remoteuser':
        if localname in ['TEST', 'IMPORT']:
            return ['group:admin']

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
        userid = access_key.properties['user_uuid']
        user = root.by_item_type['user'][userid]

    if user is None:
        return None

    principals = ['userid:%s' % user.uuid]
    lab_uuids = user.properties.get('lab_uuids', [])
    principals.extend('lab:' + lab_uuid for lab_uuid in lab_uuids)
    if CHERRY_LAB_UUID in lab_uuids:
        principals.append('group:admin')
    return principals
