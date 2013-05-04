from .storage import (
    DBSession,
    EDWKey,
    UserMap,
)

CHERRY_LAB_UUID = 'cfb789b8-46f3-4d59-a2b3-adc39e7df93a'


def groupfinder(login, request):
    if ':' not in login:
        return None
    namespace, localname = login.split(':', 1)

    if namespace == 'mailto':
        session = DBSession()
        model = session.query(UserMap).get(login)
        if model is None:
            return None
        user = model.user
        principals = ['userid:' + str(user.rid)]
        lab_uuids = user.statement.object.get('lab_uuids', [])
        principals.extend('lab:' + lab_uuid for lab_uuid in lab_uuids)
        if CHERRY_LAB_UUID in lab_uuids:
            principals.append('group:admin')
        return principals

    elif namespace == 'edwkey':
        session = DBSession()
        model = session.query(EDWKey).get(localname)
        if model is None:
            return None
        user = model.user
        principals = ['userid:' + str(user.rid)]
        lab_uuids = user.statement.object.get('lab_uuids', [])
        principals.extend('lab:' + lab_uuid for lab_uuid in lab_uuids)
        if CHERRY_LAB_UUID in lab_uuids:
            principals.append('group:admin')
        return principals

    elif namespace == 'remoteuser':
        if localname in ['TEST', 'IMPORT']:
            return ['group:admin']

    elif namespace == 'accesskey':
        access_key = request.root['access-keys'][localname]
        userid = access_key.properties['user_uuid']
        principals = ['userid:' + userid]
        user = request.root['users'][userid]
        lab_uuids = user.properties.get('lab_uuids', [])
        principals.extend('lab:' + lab_uuid for lab_uuid in lab_uuids)
        if CHERRY_LAB_UUID in lab_uuids:
            principals.append('group:admin')
        return principals
