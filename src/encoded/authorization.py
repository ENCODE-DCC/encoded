from sqlalchemy.orm.exc import NoResultFound
from .storage import (
    DBSession,
    UserMap,
    )


def groupfinder(login, request):
    if ':' not in login:
        return None
    namespace, localname = login.split(':', 1)

    if namespace == 'mailto':
        session = DBSession()
        query = session.query(UserMap).filter(UserMap.login == login)
        try:
            user = query.one().user
            principals = ['userid:' + str(user.rid)]
            principals.extend('lab:' + lab_uuid for lab_uuid in user.statement.object.get('lab_uuids', []))
            return principals
        except NoResultFound:
            return None

    elif namespace == 'remoteuser':
        if localname in ['TEST', 'IMPORT']:
            return ['group:admin']
